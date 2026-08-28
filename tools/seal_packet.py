#!/usr/bin/env python3
"""Create the final QA receipt, HANDOFF.json, and checksums for HP-A30-003."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


PACKET = Path(__file__).resolve().parents[1]
MODULES = (
    "m49386", "m49387", "m49389", "m49390", "m49392", "m49393",
    "m49395", "m49396", "m49397", "m49398", "m49399",
)
INDEPENDENT_REVIEWS = (
    "qa/independent_m49398_review.json",
    "qa/independent_m49399_review.json",
    "qa/independent_chapter6_review.json",
    "qa/independent_chapter7_core_review.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict[str, object]:
    return {"path": path.relative_to(PACKET).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def status(document: dict[str, object]) -> str:
    return str(document.get("status") or document.get("overall_status") or document.get("verdict") or "").upper()


def included_files() -> list[Path]:
    canonical_tools = {
        "aggregate_qa.py", "build_backend.py", "build_closure_manifest.py",
        "build_issues.py", "build_reader.py", "cnxml_pipeline.py",
        "consolidate_records.py", "qa_reader.py", "seal_packet.py",
        "verify_packet.py", "agent_b_m49389_translations.json",
        "agent_b_m49390_translations.json", "agent_b_m49392_translations.json",
        "agent_c_m49393_final.json", "agent_c_m49396_final.json",
        "agent_c_m49397_final.json",
    }
    files: list[Path] = []
    for path in PACKET.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(PACKET)
        if relative.parts[0] == "tmp" or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if relative.parts[0] == "qa" and len(relative.parts) > 1 and relative.parts[1] in {"agent_a", "agent_b", "agent_c"}:
            continue
        if relative.parts[0] == "tools":
            if len(relative.parts) == 2 and relative.parts[1] not in canonical_tools:
                continue
            if len(relative.parts) > 2 and relative.parts[1] != "agent_a_overlays":
                continue
        if relative.parts[0] == "work":
            name = relative.name
            if not (name.endswith("_source_slots.json") or name in {"m49398_translation_overlay.json", "m49399_translation_overlay.json"}):
                continue
        if relative.as_posix() in {"HANDOFF.json", "checksums.sha256"}:
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(PACKET).as_posix())


def main() -> None:
    source_manifest_path = PACKET / "source_manifest.json"
    contract_manifest_path = PACKET / "contract_manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    contract_manifest = json.loads(contract_manifest_path.read_text(encoding="utf-8"))
    packet_qa_path = PACKET / "qa/PACKET_QA.json"
    reader_qa_path = PACKET / "qa/READER_QA.json"
    backend_manifest_path = PACKET / "backend/BACKEND_MANIFEST.json"
    closure_path = PACKET / "closure_manifest.json"
    packet_qa = json.loads(packet_qa_path.read_text(encoding="utf-8"))
    reader_qa = json.loads(reader_qa_path.read_text(encoding="utf-8"))
    backend_manifest = json.loads(backend_manifest_path.read_text(encoding="utf-8"))
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    terminology = json.loads((PACKET / "terminology_proposals.json").read_text(encoding="utf-8"))
    corrections = json.loads((PACKET / "correction_observations.json").read_text(encoding="utf-8"))
    term_reference = json.loads((PACKET / "qa/terminology_reference_decision.json").read_text(encoding="utf-8"))
    rights_qa_path = PACKET / "qa/RIGHTS_QA.json"
    rights_qa = json.loads(rights_qa_path.read_text(encoding="utf-8"))
    if source_manifest["assigned_modules"] != list(MODULES) or source_manifest["assigned_source_orders"] != [38, 48]:
        raise RuntimeError("seal scope boundary differs")
    for label, document in (
        ("packet QA", packet_qa), ("reader QA", reader_qa),
        ("backend", backend_manifest), ("closure", closure),
        ("terminology reference", term_reference), ("rights QA", rights_qa),
    ):
        if status(document) != "PASS":
            raise RuntimeError(f"{label} is not PASS")
    review_identities = []
    for relative in INDEPENDENT_REVIEWS:
        path = PACKET / relative
        document = json.loads(path.read_text(encoding="utf-8"))
        if status(document) != "PASS":
            raise RuntimeError(f"independent review is not PASS: {relative}")
        review_identities.append(identity(path))
    if packet_qa["coverage"]["reader_slots"] != 5118 or backend_manifest["entity_counts"]["segment"] != 5118:
        raise RuntimeError("seal segment/slot count differs")
    if packet_qa["assets"]["unique_count"] != 196 or backend_manifest["entity_counts"]["asset"] != 196:
        raise RuntimeError("seal asset count differs")
    with (PACKET / "issues.csv").open("r", encoding="utf-8", newline="") as stream:
        issues_count = sum(1 for _item in csv.DictReader(stream))
    if issues_count != corrections["observation_count"]:
        raise RuntimeError("issues.csv and correction observations differ")

    final_qa = {
        "schema_id": "hp-a30-003-final-preseal-qa-v1",
        "packet_id": "HP-A30-003",
        "status": "PASS",
        "scope": {"source_orders": [38, 48], "module_ids": list(MODULES), "neighboring_ranges_touched": False},
        "counts": {
            "modules": 11,
            "reader_slots": 5118,
            "assets": 196,
            "backend_records": backend_manifest["record_count"],
            "terminology_proposals": terminology["proposal_count"],
            "correction_observations": corrections["observation_count"],
            "issues": issues_count,
            "reader_pages": reader_qa["pdf"]["pages"],
        },
        "gates": {
            "source_and_contract_freeze": "PASS",
            "exact_translation_coverage": "PASS",
            "xml_topology_ids_xrefs_comments": "PASS",
            "non_mtext_mathml_and_numeric_fidelity": "PASS",
            "independent_semantic_review": "PASS",
            "terminology_reference_comparison": "PASS",
            "license_and_attribution": "PASS",
            "accessibility_language_and_asset_closure": "PASS",
            "reader_repeat_build_and_visual_review": "PASS",
            "backend_schema_csv_roundtrip_repeat_build": "PASS",
            "helper_only_write_boundary": "PASS",
        },
        "evidence": {
            "packet_qa": identity(packet_qa_path),
            "reader_qa": identity(reader_qa_path),
            "backend_manifest": identity(backend_manifest_path),
            "closure_manifest": identity(closure_path),
            "independent_reviews": review_identities,
            "rights_qa": identity(rights_qa_path),
            "issues": identity(PACKET / "issues.csv"),
        },
        "signed_by": "Codex on instructions of the user",
    }
    final_qa_path = PACKET / "qa/FINAL_SEAL_QA.json"
    final_qa_path.write_text(json.dumps(final_qa, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")

    output_files = [identity(path) for path in included_files()]
    aggregate = hashlib.sha256(canonical(output_files).encode("utf-8")).hexdigest()
    source_artifacts = [
        {"module_id": item["module_id"], **identity(PACKET / item["path"])}
        for item in source_manifest["modules"]
    ]
    contract_artifacts = [
        {"source_locator": item["source_locator"], **identity(PACKET / item["packet_path"])}
        for item in contract_manifest["contracts"]
    ]
    handoff = {
        "packet_id": "HP-A30-003",
        "helper_thread_id": "01a01f58-86dc-7692-89df-8edc30c8ec38",
        "canonical_owner_thread_id": "01a01f42-6678-7043-89c5-87cc465202e8",
        "source_revision": {
            "repository": source_manifest["repository"],
            "commit": source_manifest["commit"],
            "tree": source_manifest["tree"],
            "source_orders": [38, 48],
        },
        "source_artifacts": source_artifacts,
        "contract_artifacts": contract_artifacts,
        "assigned_semantic_unit_ids": list(MODULES),
        "excluded_neighboring_unit_ids": ["m49384"],
        "output_files": output_files,
        "coverage_result": {"status": "PASS", "modules": 11, "source_slots": 5118, "translated_slots": 5118, "complete_chapters": [6, 7], "all_unassigned_modules_excluded": True},
        "formula_and_markup_preservation_result": {"status": "PASS", **packet_qa["aggregate_preservation"], "checks": {"non_mtext_mathml": "PASS", "numeric_reader_fidelity": "PASS", "xml_topology_ids_xrefs_comments": "PASS"}},
        "terminology_result": {"status": "PASS", "proposal_count": terminology["proposal_count"], "owner_contract_modified": False, "reference_comparison": identity(PACKET / "qa/terminology_reference_decision.json")},
        "asset_result": {"status": "PASS", "unique_assets": 196, "all_present": True, "translated_copies_byte_identical": True, "closure_manifest": identity(closure_path)},
        "qa_result": {"status": "PASS", "final_preseal_qa": identity(final_qa_path), "packet_qa": identity(packet_qa_path), "reader_qa": identity(reader_qa_path), "backend_manifest": identity(backend_manifest_path), "independent_reviews": review_identities},
        "issues_file": identity(PACKET / "issues.csv"),
        "aggregate_sha256": aggregate,
        "signed_by": "Codex on instructions of the user",
    }
    handoff_path = PACKET / "HANDOFF.json"
    handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    checksum_records = [identity(path) for path in included_files()] + [identity(handoff_path)]
    checksum_records.sort(key=lambda item: str(item["path"]))
    checksums_path = PACKET / "checksums.sha256"
    checksums_path.write_text("".join(f"{item['sha256']}  {item['path']}\n" for item in checksum_records), encoding="utf-8", newline="\n")
    print(canonical({"aggregate_sha256": aggregate, "checksums_entries": len(checksum_records), "handoff_sha256": sha(handoff_path), "checksums_sha256": sha(checksums_path), "status": "PASS"}))


if __name__ == "__main__":
    main()
