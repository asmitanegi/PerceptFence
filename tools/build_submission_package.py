#!/usr/bin/env python3
"""Build and verify the double-anonymous PerceptFence submission archives.

The source and Additional-file ZIPs are allow-list products. The staged manuscript
PDF is compiled from a clean extraction of the source ZIP so the PDF and uploaded
source necessarily share the same files.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

DATE = "2026-07-09"
IDENTITY_TOKENS = (
    "Asmita",
    "Asmitha",
    "Negi",
    "Neeraj",
    "Singh",
    "Beshane",
    "Parafin",
    "asmitanegi07",
    "b.neerajkumarsingh",
    "0009-0005-7566-9555",
    "0009-0002-2125-1805",
)
BANNED_REVIEW_PATH_NAMES = {
    "authors_identity.tex",
    "model_in_loop.csv",
    "model_in_loop_weakmodel.csv",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise SystemExit(f"required source file missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree_files(source: Path, destination: Path, patterns: tuple[str, ...]) -> None:
    if not source.is_dir():
        raise SystemExit(f"required source directory missing: {source}")
    copied = 0
    for pattern in patterns:
        for path in sorted(source.rglob(pattern)):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            copy_file(path, destination / path.relative_to(source))
            copied += 1
    if copied == 0:
        raise SystemExit(f"allow-list copied no files from {source}: {patterns}")


def write_checksums(root: Path, filename: str) -> Path:
    manifest = root / filename
    rows = [
        f"{sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(root.rglob("*"))
        if path.is_file() and path != manifest
    ]
    if not rows:
        raise SystemExit(f"cannot write empty checksum manifest: {manifest}")
    manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return manifest


def verify_checksum_manifest(root: Path, filename: str) -> None:
    manifest = root / filename
    expected_paths: set[Path] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = root / relative
        expected_paths.add(path)
        if not path.is_file() or sha256(path) != expected:
            raise SystemExit(f"checksum verification failed: {relative}")
    actual_paths = {path for path in root.rglob("*") if path.is_file() and path != manifest}
    if expected_paths != actual_paths:
        raise SystemExit("checksum manifest inventory does not match archive tree")


def scan_blinded_tree(root: Path) -> None:
    hits: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.name in BANNED_REVIEW_PATH_NAMES:
            hits.append(f"banned path: {relative}")
        lowered_path = relative.casefold()
        for token in IDENTITY_TOKENS:
            if token.casefold() in lowered_path:
                hits.append(f"identity in path: {relative} ({token})")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in IDENTITY_TOKENS:
            if token.casefold() in text.casefold():
                hits.append(f"identity in content: {relative} ({token})")
        if re.search(r"/(?:Users|home)/[^/]+/", text):
            hits.append(f"absolute home path in content: {relative}")
        if "zenodo.org" in text.casefold() or "10.5281/zenodo" in text.casefold():
            hits.append(f"public archive link in blinded content: {relative}")
    if hits:
        raise SystemExit("blinded-tree scan failed:\n" + "\n".join(hits))


def deterministic_zip(source_root: Path, archive: Path, package_date: str = DATE) -> None:
    year, month, day = (int(part) for part in package_date.split("-"))
    archive.unlink(missing_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file():
                continue
            archive_name = path.relative_to(source_root.parent).as_posix()
            info = zipfile.ZipInfo(archive_name, date_time=(year, month, day, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            handle.writestr(info, path.read_bytes())


def extract_single_root(archive: Path, destination: Path) -> Path:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    with zipfile.ZipFile(archive) as handle:
        handle.extractall(destination)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise SystemExit(f"archive must contain one root directory: {archive}")
    return roots[0]


def build_source_package(
    repo: Path,
    work: Path,
    output: Path,
    *,
    review_model: str,
    target: str,
    package_date: str,
) -> tuple[Path, Path]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", target):
        raise SystemExit(f"invalid target slug: {target}")
    if review_model not in {"double-anonymous", "single-anonymous"}:
        raise SystemExit(f"unsupported review model: {review_model}")

    review_label = "single-blind" if review_model == "single-anonymous" else review_model
    legacy_blinded = review_model == "double-anonymous" and target == "cybersecurity"
    source_name = "PerceptFence_blinded_source" if legacy_blinded else f"PerceptFence_{target}_source"
    source = work / source_name
    source.mkdir(parents=True)
    for name in ("main.tex", "references.bib", "sn-jnl.cls", "sn-mathphys-num.bst"):
        copy_file(repo / "paper" / name, source / name)

    if review_model == "single-anonymous":
        copy_file(repo / "paper" / "authors_identity.tex", source / "authors_identity.tex")
        main = source / "main.tex"
        text = main.read_text(encoding="utf-8")
        if r"\blindtrue" not in text:
            raise SystemExit("main.tex does not declare the expected blinded review mode")
        text = text.replace(r"\blindtrue", r"\blindfalse")
        text = text.replace("double-anonymous", review_label)
        main.write_text(text, encoding="utf-8")

    tex = (repo / "paper" / "main.tex").read_text(encoding="utf-8")
    figures = sorted(set(re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex)))
    if not figures:
        raise SystemExit("main.tex declares no figure dependencies")
    for relative in figures:
        copy_file(repo / "paper" / relative, source / relative)

    identity_note = (
        "authors_identity.tex is intentionally excluded for double-anonymous review.\n"
        if review_model == "double-anonymous"
        else "authors_identity.tex is included for single-blind review.\n"
    )
    (source / "README.txt").write_text(
        f"PerceptFence {review_label} LaTeX source for {target}\n\n"
        "Compile with:\n"
        "  tectonic -X compile main.tex --outdir build --keep-logs --keep-intermediates\n\n"
        + identity_note,
        encoding="utf-8",
    )
    write_checksums(source, "SOURCE_CHECKSUMS.sha256")
    if review_model == "double-anonymous":
        scan_blinded_tree(source)

    source_stem = "perceptfence_blinded_source" if legacy_blinded else f"perceptfence_{target}_source"
    archive = output / f"{source_stem}_{package_date}.zip"
    deterministic_zip(source, archive, package_date)
    extracted = extract_single_root(archive, work / "source-extracted")
    verify_checksum_manifest(extracted, "SOURCE_CHECKSUMS.sha256")
    if review_model == "double-anonymous":
        scan_blinded_tree(extracted)

    build = extracted / "build"
    build.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["tectonic", "-X", "compile", "main.tex", "--outdir", str(build), "--keep-logs", "--keep-intermediates"],
        cwd=extracted,
        text=True,
        capture_output=True,
    )
    (work / "source_compile.stdout").write_text(result.stdout, encoding="utf-8")
    (work / "source_compile.stderr").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0 or not (build / "main.pdf").is_file():
        raise SystemExit("clean-extracted blinded source did not compile")
    manuscript_stem = (
        "perceptfence_blinded_manuscript"
        if legacy_blinded
        else f"perceptfence_{target}_manuscript"
    )
    staged_pdf = output / f"{manuscript_stem}_{package_date}.pdf"
    shutil.copy2(build / "main.pdf", staged_pdf)
    if review_model == "single-anonymous":
        text_path = work / "single-anonymous-manuscript.txt"
        extracted_text = subprocess.run(
            ["pdftotext", str(staged_pdf), str(text_path)],
            text=True,
            capture_output=True,
        )
        if extracted_text.returncode != 0:
            raise SystemExit("single-anonymous PDF text extraction failed")
        rendered = " ".join(text_path.read_text(encoding="utf-8").split())
        required = ("Asmita Negi", "Neeraj Kumar Singh Beshane", "Independent Researcher")
        missing = [value for value in required if value not in rendered]
        if missing:
            raise SystemExit(f"single-anonymous PDF is missing author metadata: {missing}")
        if "Parafin" in rendered:
            raise SystemExit("single-anonymous PDF contains employer identity")
    return archive, staged_pdf


def build_blinded_source(repo: Path, work: Path, output: Path) -> tuple[Path, Path]:
    return build_source_package(
        repo,
        work,
        output,
        review_model="double-anonymous",
        target="cybersecurity",
        package_date=DATE,
    )


def build_additional_file(
    repo: Path,
    work: Path,
    output: Path,
    *,
    review_model: str = "double-anonymous",
    target: str = "cybersecurity",
    journal_name: str = "Cybersecurity",
    package_date: str = DATE,
) -> Path:
    review_label = "single-blind" if review_model == "single-anonymous" else review_model
    additional = work / "PerceptFence_review_artifact"
    additional.mkdir(parents=True)

    copy_file(repo / "supplement" / "README_REVIEW_ARTIFACT.md", additional / "README.md")
    copy_file(repo / "supplement" / "SUPPLEMENT_MANIFEST.md", additional / "SUPPLEMENT_MANIFEST.md")
    copy_file(repo / "supplement" / "artifact_checklist.md", additional / "artifact_checklist.md")
    citation_source = (
        repo / "CITATION.cff"
        if review_model == "single-anonymous"
        else repo / "supplement" / "CITATION.cff"
    )
    copy_file(citation_source, additional / "CITATION.cff")
    for name in ("pyproject.toml", "requirements-eval.txt"):
        copy_file(repo / name, additional / name)

    package_context = [
        f"target={target}",
        f"journal={journal_name}",
        f"review_model={review_label}",
        f"package_date={package_date}",
        "article_title=PerceptFence: Content-Mediation Architecture and Deterministic Coverage for Screen-Share AI Assistants",
    ]
    if review_model == "single-anonymous":
        package_context.extend(
            [
                "authors=Asmita Negi; Neeraj Kumar Singh Beshane",
                "affiliation=Independent Researcher",
                "author_1_location=San Francisco, California, United States",
                "author_2_location=Fremont, California, United States",
                "corresponding_author=Neeraj Kumar Singh Beshane",
                "corresponding_email=b.neerajkumarsingh@gmail.com",
            ]
        )
    (additional / "PACKAGE_CONTEXT.txt").write_text(
        "\n".join(package_context) + "\n",
        encoding="utf-8",
    )
    rights_holders = (
        "Asmita Negi and Neeraj Kumar Singh Beshane"
        if review_model == "single-anonymous"
        else "Anonymous Authors"
    )
    artifact_label = (
        "review artifact"
        if review_model == "single-anonymous"
        else "identity-hidden review artifact"
    )
    (additional / "LICENSE").write_text(
        "All rights reserved.\n\n"
        f"Copyright (c) 2026 {rights_holders}.\n\n"
        f"This {artifact_label} is provided solely for peer review, citation, "
        "and reproducibility inspection. No permission is granted to redistribute, "
        "sublicense, sell, or reuse it outside the review process without explicit "
        "written permission from the rights holders.\n",
        encoding="utf-8",
    )

    copy_tree_files(repo / "screenshare_mediator", additional / "screenshare_mediator", ("*.py",))
    copy_tree_files(repo / "tests", additional / "tests", ("*.py",))
    copy_tree_files(repo / "policies", additional / "policies", ("*.json",))
    copy_tree_files(repo / "data" / "synthetic", additional / "data" / "synthetic", ("*.json", "*.md"))

    for name in ("benchmark.py", "smoke_test.py", "ablation_study.py", "metrics.md", "render_figure.py", "render_architecture_figure.py", "render_coverage_figure.py"):
        copy_file(repo / "eval" / name, additional / "eval" / name)
    for name in ("run_model_eval.py", "README.md"):
        copy_file(repo / "eval" / "model_in_loop" / name, additional / "eval" / "model_in_loop" / name)
    copy_tree_files(repo / "eval" / "heldout", additional / "eval" / "heldout", ("*.py", "*.md"))
    for name in (
        "baseline_vs_guarded.csv",
        "per_module_ablation.csv",
        "per_fixture_ablation.csv",
        "heldout_overall.csv",
        "heldout_by_family.csv",
        "heldout_benign_controls.csv",
        "heldout_dose_response.csv",
        "heldout_sensitivity.csv",
        "heldout_paired_presidio.csv",
    ):
        copy_file(repo / "eval" / "results" / name, additional / "eval" / "results" / name)
    for name in ("architecture_walkthrough.pdf", "heldout_coverage.pdf"):
        copy_file(repo / "paper" / "figures" / name, additional / "paper" / "figures" / name)

    write_checksums(additional, "ADDITIONAL_FILE_CHECKSUMS.sha256")
    if review_model == "double-anonymous":
        scan_blinded_tree(additional)
    archive_stem = (
        "perceptfence_additional_file_1"
        if target == "cybersecurity" and package_date == DATE
        else f"perceptfence_{target}_additional_file_1"
    )
    archive = output / f"{archive_stem}_{package_date}.zip"
    deterministic_zip(additional, archive, package_date)
    extracted = extract_single_root(archive, work / "additional-extracted")
    verify_checksum_manifest(extracted, "ADDITIONAL_FILE_CHECKSUMS.sha256")
    if review_model == "double-anonymous":
        scan_blinded_tree(extracted)
    return archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work", type=Path, default=Path("/tmp/perceptfence-final-package-build"))
    parser.add_argument(
        "--review-model",
        choices=("double-anonymous", "single-anonymous"),
        default="double-anonymous",
    )
    parser.add_argument("--target", default="cybersecurity")
    parser.add_argument("--journal-name", default="Cybersecurity")
    parser.add_argument("--date", default=DATE)
    args = parser.parse_args()

    repo = args.repo.resolve()
    output = args.output.resolve()
    work = args.work.resolve()
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    output.mkdir(parents=True, exist_ok=True)

    source_zip, manuscript_pdf = build_source_package(
        repo,
        work,
        output,
        review_model=args.review_model,
        target=args.target,
        package_date=args.date,
    )
    additional_zip = build_additional_file(
        repo,
        work,
        output,
        review_model=args.review_model,
        target=args.target,
        journal_name=args.journal_name,
        package_date=args.date,
    )
    print(f"source_zip={source_zip} sha256={sha256(source_zip)}")
    print(f"manuscript_pdf={manuscript_pdf} sha256={sha256(manuscript_pdf)}")
    print(f"additional_zip={additional_zip} sha256={sha256(additional_zip)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
