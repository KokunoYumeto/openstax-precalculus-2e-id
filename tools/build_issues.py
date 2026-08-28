#!/usr/bin/env python3
"""Project consolidated source observations into the required packet issues.csv."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


PACKET = Path(__file__).resolve().parents[1]
FIELDS = (
    "issue_id", "module_id", "slot", "locator", "category", "severity",
    "status", "source", "high_confidence_correction", "disposition", "evidence",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def category(item: dict[str, str]) -> str:
    locator = item["locator"].casefold()
    source = item["source"].casefold()
    correction = item["correction"].casefold()
    if "@alt" in locator or "@summary" in locator:
        if any(token in source + " " + correction for token in ("pi/", "meter", "feet", "(6,", "range", "equation")):
            return "source_accessibility_math_or_data"
        return "source_accessibility_text"
    if any(token in item["disposition"].casefold() for token in ("mathematical", "contradiction", "collection map")):
        return "source_mathematical_or_reference_issue"
    return "source_prose_typo_or_grammar"


def main() -> None:
    source_path = PACKET / "correction_observations.json"
    document = json.loads(source_path.read_text(encoding="utf-8"))
    records = document["records"]
    if document["observation_count"] != len(records) or not document["all_high_confidence"]:
        raise RuntimeError("consolidated correction observation contract failed")
    output = PACKET / "issues.csv"
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for number, item in enumerate(records, start=1):
            disposition = item["disposition"]
            status = "source_issue_preserved_nonblocking_owner_integration" if "current helper target preserves" in disposition else "intended_meaning_translated_source_issue_open"
            writer.writerow({
                "issue_id": f"HP-A30-003-ISSUE-{number:03d}",
                "module_id": item["module"],
                "slot": item["slot"],
                "locator": item["locator"],
                "category": category(item),
                "severity": "source_high_confidence_nonblocking",
                "status": status,
                "source": item["source"],
                "high_confidence_correction": item["correction"],
                "disposition": disposition,
                "evidence": "correction_observations.json",
            })
    with output.open("r", encoding="utf-8", newline="") as stream:
        readback = list(csv.DictReader(stream))
    if len(readback) != len(records) or tuple(readback[0]) != FIELDS:
        raise RuntimeError("issues.csv readback failed")
    print(json.dumps({"path": "issues.csv", "issues": len(readback), "bytes": output.stat().st_size, "sha256": sha(output), "status": "PASS"}, sort_keys=True))


if __name__ == "__main__":
    main()
