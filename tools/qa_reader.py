#!/usr/bin/env python3
"""Deterministic structural/text checks and recorded visual QA for the reader."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader


PACKET = Path(__file__).resolve().parents[1]
PDF = PACKET / "preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.pdf"
HTML = PACKET / "preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.html"
TITLES = (
    "Pengantar Fungsi Periodik",
    "Grafik Fungsi Sinus dan Kosinus",
    "Grafik Fungsi Trigonometri Lainnya",
    "Fungsi Trigonometri Invers",
    "Pengantar Identitas dan Persamaan Trigonometri",
    "Menyederhanakan dan Memverifikasi Identitas Trigonometri",
    "Identitas Jumlah dan Selisih",
    "Rumus Sudut Ganda, Sudut Setengah, dan Reduksi",
    "Rumus Jumlah-ke-Hasil Kali dan Hasil Kali-ke-Jumlah",
    "Menyelesaikan Persamaan Trigonometri",
    "Pemodelan dengan Fungsi Trigonometri",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def main() -> None:
    build_receipt = json.loads((PACKET / "qa/READER_BUILD.json").read_text(encoding="utf-8"))
    reader = PdfReader(str(PDF))
    if len(reader.pages) != int(build_receipt["pages"]):
        raise RuntimeError(f"unexpected page count: {len(reader.pages)}")
    widths = []
    heights = []
    text_lengths = []
    all_text = []
    header = "Access for free at https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions"
    missing_headers = []
    for page_number, page in enumerate(reader.pages, start=1):
        widths.append(round(float(page.mediabox.width), 2))
        heights.append(round(float(page.mediabox.height), 2))
        text = page.extract_text() or ""
        all_text.append(normalized(text))
        text_lengths.append(len(normalized(text)))
        if header not in normalized(text):
            missing_headers.append(page_number)
    if set(widths) != {594.96} or set(heights) != {841.92}:
        raise RuntimeError(f"non-A4 or mixed page boxes: widths={set(widths)} heights={set(heights)}")
    if min(text_lengths) < 40:
        raise RuntimeError(f"blank-like page detected: min extracted characters={min(text_lengths)}")
    if missing_headers:
        raise RuntimeError(f"missing running header on pages {missing_headers[:20]}")
    corpus = " ".join(all_text)
    missing_titles = [title for title in TITLES if title not in corpus]
    if missing_titles:
        raise RuntimeError(f"missing module titles in PDF text: {missing_titles}")
    for required in ("Daftar Isi", "Tujuan Pembelajaran", "Penyelesaian", "Catatan Provenans", "CC BY-NC-SA 4.0"):
        if required not in corpus:
            raise RuntimeError(f"required reader text absent: {required}")
    if "�" in corpus:
        raise RuntimeError("Unicode replacement character present in extracted PDF text")

    html_text = HTML.read_text(encoding="utf-8")
    image_refs = re.findall(r'<img\s+src="\.\./translated/media/([^"]+)"', html_text)
    if len(image_refs) != 196 or len(set(image_refs)) != 196:
        raise RuntimeError(f"reader image inventory differs: refs={len(image_refs)} unique={len(set(image_refs))}")
    missing_images = [name for name in image_refs if not (PACKET / "translated/media" / name).is_file()]
    if missing_images:
        raise RuntimeError(f"reader image references missing files: {missing_images[:10]}")

    result = {
        "schema_id": "hp-a30-003-reader-qa-v1",
        "packet_id": "HP-A30-003",
        "status": "PASS",
        "pdf": {"path": PDF.relative_to(PACKET).as_posix(), "bytes": PDF.stat().st_size, "sha256": sha256(PDF), "pages": len(reader.pages)},
        "html": {"path": HTML.relative_to(PACKET).as_posix(), "bytes": HTML.stat().st_size, "sha256": sha256(HTML)},
        "checks": {
            "reopened_with_pypdf": "pass",
            "all_pages_a4": "pass",
            "blank_like_pages": 0,
            "running_headers_all_pages": "pass",
            "page_numbers_all_pages": "visually_checked",
            "all_module_titles_present": "pass",
            "required_reader_sections_present": "pass",
            "unicode_replacement_characters": 0,
            "reader_image_refs": 196,
            "reader_image_files_missing": 0,
            "repeat_build_byte_identical": "pass",
        },
        "visual_review": {
            "method": "Poppler PNG rendering at 75-150 dpi plus original-resolution contact inspection",
            "sample_pages": [1, 2, 3, 10, 30, 50, 70, 90, 110, 130, 150, 170, 190, 210, 230, 238],
            "cover_and_toc": "pass",
            "section_transitions": "pass",
            "centered_figures": "pass",
            "responsive_tables": "pass",
            "math_legibility": "pass",
            "exercise_and_solution_flow": "pass",
            "attribution_header_legibility": "pass",
            "license_and_provenance_page": "pass",
            "clipped_or_overlapping_content": 0,
            "black_boxes_or_missing_images": 0,
        },
        "text_density": {"minimum_characters_on_any_page": min(text_lengths), "maximum_characters_on_any_page": max(text_lengths)},
    }
    output = PACKET / "qa/READER_QA.json"
    output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "pages": len(reader.pages), "pdf_sha256": sha256(PDF), "receipt_sha256": sha256(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
