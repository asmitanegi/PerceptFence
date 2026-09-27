from __future__ import annotations

import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_submission_package.py"
VERIFIER = ROOT / "tools" / "verify_submission.py"


def test_submission_verifier_tracks_single_anonymous_identity_source() -> None:
    spec = importlib.util.spec_from_file_location("verify_submission", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert ROOT / "paper" / "authors_identity.tex" in module.PACK


def test_single_anonymous_package_contains_author_identity_without_employer(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--repo",
            str(ROOT),
            "--output",
            str(output),
            "--work",
            str(tmp_path / "work"),
            "--review-model",
            "single-anonymous",
            "--target",
            "international-journal-information-security",
            "--journal-name",
            "International Journal of Information Security",
            "--date",
            "2026-09-07",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    source_zip = output / "perceptfence_international-journal-information-security_source_2026-09-07.zip"
    manuscript_pdf = output / "perceptfence_international-journal-information-security_manuscript_2026-09-07.pdf"
    additional_zip = output / "perceptfence_international-journal-information-security_additional_file_1_2026-09-07.zip"
    assert source_zip.is_file()
    assert manuscript_pdf.is_file()
    assert additional_zip.is_file()

    with zipfile.ZipFile(source_zip) as archive:
        names = set(archive.namelist())
        root = "PerceptFence_international-journal-information-security_source"
        assert f"{root}/authors_identity.tex" in names
        main = archive.read(f"{root}/main.tex").decode("utf-8")
        assert r"\blindfalse" in main
        assert r"\blindtrue" not in main
        assert "single-blind" in main
        assert "single-anonymous" not in main

    text_path = tmp_path / "manuscript.txt"
    extracted = subprocess.run(
        ["pdftotext", str(manuscript_pdf), str(text_path)],
        capture_output=True,
        text=True,
    )
    assert extracted.returncode == 0, extracted.stdout + extracted.stderr
    text = text_path.read_text(encoding="utf-8")
    assert "Asmita Negi" in text
    assert "Neeraj Kumar Singh Beshane" in text
    assert "Independent Researcher" in text
    assert "b.neerajkumarsingh@gmail.com" in text
    assert "San Francisco" in text
    assert "Fremont" in text
    assert "Parafin" not in text
    assert "10.5281/zenodo.21289219" in text
    assert "double-anonymous review" not in text
    assert "perceptfence_additional_file_1_2026-07-09.zip" not in text

    with zipfile.ZipFile(additional_zip) as archive:
        names = archive.namelist()
        citation_name = next(name for name in names if name.endswith("/CITATION.cff"))
        citation = archive.read(citation_name).decode("utf-8")
        text_names = [
            name
            for name in names
            if name.endswith((".md", ".txt", ".cff", ".toml"))
        ]
        additional_text = "\n".join(
            archive.read(name).decode("utf-8", errors="replace") for name in text_names
        )
    assert "Asmita" in citation
    assert "Beshane" in citation
    assert "Cybersecurity" not in additional_text
    assert "Discover Computing" not in additional_text
    assert "double-anonymous" not in additional_text
    assert "journal=International Journal of Information Security" in additional_text
    assert "review_model=single-blind" in additional_text
    assert "corresponding_email=b.neerajkumarsingh@gmail.com" in additional_text
    assert "author_1_location=San Francisco, California, United States" in additional_text
    assert "author_2_location=Fremont, California, United States" in additional_text


def test_double_anonymous_package_excludes_identity_and_public_archive(tmp_path: Path) -> None:
    output = tmp_path / "output"
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--repo",
            str(ROOT),
            "--output",
            str(output),
            "--work",
            str(tmp_path / "work"),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    source_zip = output / "perceptfence_blinded_source_2026-07-09.zip"
    manuscript_pdf = output / "perceptfence_blinded_manuscript_2026-07-09.pdf"
    additional_zip = output / "perceptfence_additional_file_1_2026-07-09.zip"
    assert additional_zip.is_file()
    with zipfile.ZipFile(source_zip) as archive:
        names = set(archive.namelist())
        root = "PerceptFence_blinded_source"
        assert f"{root}/authors_identity.tex" not in names
        main = archive.read(f"{root}/main.tex").decode("utf-8")
        assert "Asmita" not in main
        assert "Negi" not in main
        assert "10.5281/zenodo" not in main
        assert "github.com/asmitanegi" not in main

    text_path = tmp_path / "manuscript.txt"
    extracted = subprocess.run(
        ["pdftotext", str(manuscript_pdf), str(text_path)],
        capture_output=True,
        text=True,
    )
    assert extracted.returncode == 0, extracted.stdout + extracted.stderr
    text = text_path.read_text(encoding="utf-8")
    assert "Anonymous Author(s)" in text
    assert "Asmita Negi" not in text
    assert "Neeraj Kumar Singh Beshane" not in text
    assert "10.5281/zenodo" not in text

    with zipfile.ZipFile(additional_zip) as archive:
        names = archive.namelist()
        text_names = [
            name
            for name in names
            if name.endswith((".md", ".txt", ".cff", ".toml"))
        ]
        additional_text = "\n".join(
            archive.read(name).decode("utf-8", errors="replace") for name in text_names
        )
    assert "Asmita" not in additional_text
    assert "Beshane" not in additional_text
    assert "10.5281/zenodo" not in additional_text
    assert "Discover Computing" not in additional_text
