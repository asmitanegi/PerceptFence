"""Render each ScreenCase with headless Chrome, optionally degrade it, and OCR it.

Pipeline per case:  HTML -> Chrome --headless=new screenshot (1280x720, DPR 1)
                    -> [compressed: 0.75x downscale + JPEG q55 + upscale back]
                    -> tesseract 5 (eng, --psm 6) -> OCR text

The OCR text is what a screen-share assistant's vision/OCR front end would hand
to the model, so it is the input every defense sees. Output is cached as JSONL
(one row per case: case_id + ocr text); PNGs are written to a scratch directory
outside the repository and are never committed, because they contain the
generated (fictitious) credential strings in pixel form.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from eval.screen import corpus  # noqa: E402

CHROME = os.environ.get("PF_CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def _chrome_version() -> str:
    try:
        return subprocess.run([CHROME, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as exc:  # pragma: no cover
        return f"unknown ({exc})"


def _tesseract_version() -> str:
    out = subprocess.run(["tesseract", "--version"], capture_output=True, text=True).stdout
    return out.splitlines()[0] if out else "unknown"


class Browser:
    """One headless Chrome, driven over the DevTools protocol (much faster than a process per screen)."""

    def __init__(self, workdir: Path) -> None:
        import socket
        import time
        import urllib.request

        import websocket

        s = socket.socket(); s.bind(("127.0.0.1", 0)); self.port = s.getsockname()[1]; s.close()
        self.profile = workdir / "_chrome-profile"
        self.proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--no-default-browser-check", f"--user-data-dir={self.profile}", "--force-device-scale-factor=1",
             f"--remote-debugging-port={self.port}", "--window-size=1280,720", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=2))
                page = next(t for t in tabs if t.get("type") == "page")
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("chrome did not expose DevTools")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        self._id = 0
        self.call("Emulation.setDeviceMetricsOverride", width=1280, height=720, deviceScaleFactor=1, mobile=False)

    def call(self, method: str, **params):
        self._id += 1
        self.ws.send(json.dumps({"id": self._id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def shot(self, html_path: Path, png: Path) -> None:
        import base64 as b64
        import time
        self.call("Page.navigate", url=html_path.as_uri())
        for _ in range(100):
            if self.call("Runtime.evaluate", expression="document.readyState")["result"].get("value") == "complete":
                break
            time.sleep(0.05)
        data = self.call("Page.captureScreenshot", format="png", clip={"x": 0, "y": 0, "width": 1280, "height": 720, "scale": 1})["data"]
        png.write_bytes(b64.b64decode(data))

    def close(self) -> None:
        try:
            self.ws.close()
        finally:
            self.proc.terminate(); self.proc.wait(timeout=20)
            shutil.rmtree(self.profile, ignore_errors=True)


def ocr_one(case: corpus.ScreenCase, workdir: Path) -> dict:
    d = workdir / case.case_id
    png = d / "screen.png"
    src = png
    if case.quality == "compressed":
        im = Image.open(png).convert("RGB")
        w, h = im.size
        small = im.resize((int(w * 0.75), int(h * 0.75)), Image.Resampling.BILINEAR)
        jpg = d / "screen.jpg"
        small.save(jpg, "JPEG", quality=55)
        Image.open(jpg).resize((w, h), Image.Resampling.BILINEAR).save(d / "screen_degraded.png")
        src = d / "screen_degraded.png"
    ocr = subprocess.run(["tesseract", str(src), "-", "-l", "eng", "--psm", "6"],
                         capture_output=True, text=True, timeout=120).stdout
    return {"case_id": case.case_id, "ocr": ocr, "png_sha256": hashlib.sha256(src.read_bytes()).hexdigest()}


def run(cases: list[corpus.ScreenCase], out: Path, workers: int) -> None:
    workdir = Path(os.environ.get("PF_RENDER_DIR") or tempfile.mkdtemp(prefix="pf-render-"))
    workdir.mkdir(parents=True, exist_ok=True)
    rows = []
    browser = Browser(workdir)
    try:
        shots = []
        for c in cases:  # screenshots are serial through one Chrome; OCR runs in parallel
            d = workdir / c.case_id
            d.mkdir(parents=True, exist_ok=True)
            (d / "screen.html").write_text(c.html, encoding="utf-8")
            browser.shot(d / "screen.html", d / "screen.png")
            shots.append(c)
    finally:
        browser.close()
    print(f"  captured {len(shots)} screenshots", flush=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(ocr_one, c, workdir): c.case_id for c in shots}
        for i, f in enumerate(cf.as_completed(futs), 1):
            rows.append(f.result())
            if i % 50 == 0:
                print(f"  ocr {i}/{len(cases)}", flush=True)
    rows.sort(key=lambda r: r["case_id"])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    meta = {"chrome": _chrome_version(), "tesseract": _tesseract_version(), "n_cases": len(rows),
            "render_dir": str(workdir)}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {out} ({len(rows)} cases); {meta['chrome']}; {meta['tesseract']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=("dev", "test"), required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    cases = corpus.dev_cases() if a.split == "dev" else corpus.test_cases()
    run(cases, a.out, a.workers)


if __name__ == "__main__":
    main()
