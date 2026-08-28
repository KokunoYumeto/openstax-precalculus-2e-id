#!/usr/bin/env python3
"""Read-only final verifier for the sealed HP-A30-003 helper handoff."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath

import jsonschema


PACKET = Path(__file__).resolve().parents[1]
MODULES = (
    "m49386", "m49387", "m49389", "m49390", "m49392", "m49393",
    "m49395", "m49396", "m49397", "m49398", "m49399",
)
HANDOFF_FIELDS = {
    "packet_id", "helper_thread_id", "canonical_owner_thread_id",
    "source_revision", "source_artifacts", "contract_artifacts",
    "assigned_semantic_unit_ids", "excluded_neighboring_unit_ids",
    "output_files", "coverage_result", "formula_and_markup_preservation_result",
    "terminology_result", "asset_result", "qa_result", "issues_file",
    "aggregate_sha256", "signed_by",
}
BACKEND_FIELDS = (
    "schema", "schema_version", "entity", "id", "source_local_id",
    "source_label", "parent_id", "order", "path", "resource_id",
    "edition_id", "source_locator", "source_sha256", "language", "locale",
    "translation_state", "source_record_id", "provenance", "concept_ids",
    "prerequisite_ids", "rights_id", "status", "timestamp",
    "responsible_workflow", "supersedes_id", "qa_event_ids", "artifact_ids",
    "data",
)
REQUIRED_ENTITIES = {
    "program", "course", "resource", "edition", "unit", "concept", "segment",
    "term", "asset", "relation", "rights", "qa_event", "artifact", "correction",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_path(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not relative or "\\" in relative:
        raise RuntimeError(f"unsafe packet-relative path: {relative!r}")
    result = (PACKET / Path(*pure.parts)).resolve()
    if PACKET.resolve() not in result.parents and result != PACKET.resolve():
        raise RuntimeError(f"path escapes packet root: {relative!r}")
    return result


def verify_identity(item: dict[str, object]) -> None:
    path = safe_path(str(item["path"]))
    if not path.is_file():
        raise RuntimeError(f"missing sealed file: {item['path']}")
    if path.stat().st_size != int(item["bytes"]) or sha(path) != item["sha256"]:
        raise RuntimeError(f"sealed identity mismatch: {item['path']}")


def verify_source_and_contracts() -> None:
    source_manifest_path = PACKET / "source_manifest.json"
    source = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if source["assigned_modules"] != list(MODULES) or source["assigned_source_orders"] != [38, 48]:
        raise RuntimeError("source scope differs from the assigned boundary")
    for item in source["modules"]:
        verify_identity(item)
    for item in source["assets"]:
        source_copy = PACKET / "source" / item["path"]
        target_copy = PACKET / "translated" / item["path"]
        if source_copy.stat().st_size != item["bytes"] or sha(source_copy) != item["sha256"]:
            raise RuntimeError(f"source asset mismatch: {item['path']}")
        if source_copy.read_bytes() != target_copy.read_bytes():
            raise RuntimeError(f"translated asset differs: {item['path']}")
    contracts = json.loads((PACKET / "contract_manifest.json").read_text(encoding="utf-8"))
    for item in contracts["contracts"]:
        verify_identity({"path": item["packet_path"], "bytes": item["bytes"], "sha256": item["sha256"]})


def verify_qa_and_readers() -> None:
    packet_qa = json.loads((PACKET / "qa/PACKET_QA.json").read_text(encoding="utf-8"))
    if str(packet_qa["status"]).upper() != "PASS" or packet_qa["scope"]["module_ids"] != list(MODULES):
        raise RuntimeError("aggregate packet QA is not a scope-correct PASS")
    if packet_qa["coverage"]["reader_slots"] != 5118:
        raise RuntimeError("aggregate packet QA reader-slot count differs")
    for item in packet_qa["module_qa"]:
        qa_path = safe_path(item["path"])
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        if qa["status"] != "PASS" or qa["target"]["sha256"] != sha(PACKET / f"translated/modules/{qa['module_id']}/index.cnxml"):
            raise RuntimeError(f"module QA current-byte binding failed: {qa['module_id']}")
    for filename in (
        "qa/independent_m49398_review.json",
        "qa/independent_m49399_review.json",
        "qa/independent_chapter6_review.json",
        "qa/independent_chapter7_core_review.json",
        "qa/terminology_reference_decision.json",
        "qa/RIGHTS_QA.json",
    ):
        doc = json.loads(safe_path(filename).read_text(encoding="utf-8"))
        if str(doc.get("status") or doc.get("overall_status") or doc.get("verdict")).upper() != "PASS":
            raise RuntimeError(f"independent QA is not PASS: {filename}")
        current_target_bindings = 0

        def check_embedded_identities(value: object) -> None:
            nonlocal current_target_bindings
            if isinstance(value, dict):
                if {"path", "bytes", "sha256"} <= set(value) and str(value["path"]).startswith("translated/modules/"):
                    verify_identity(value)
                    current_target_bindings += 1
                if {"target_path", "target_bytes", "target_sha256"} <= set(value) and str(value["target_path"]).startswith("translated/modules/"):
                    verify_identity({"path": value["target_path"], "bytes": value["target_bytes"], "sha256": value["target_sha256"]})
                    current_target_bindings += 1
                for child in value.values():
                    check_embedded_identities(child)
            elif isinstance(value, list):
                for child in value:
                    check_embedded_identities(child)

        if filename not in {"qa/terminology_reference_decision.json", "qa/RIGHTS_QA.json"}:
            check_embedded_identities(doc)
            if current_target_bindings == 0:
                raise RuntimeError(f"independent QA lacks a current translated-byte binding: {filename}")
    reader_build = json.loads((PACKET / "qa/READER_BUILD.json").read_text(encoding="utf-8"))
    reader_qa = json.loads((PACKET / "qa/READER_QA.json").read_text(encoding="utf-8"))
    if str(reader_build["status"]).upper() != "PASS" or str(reader_qa["status"]).upper() != "PASS":
        raise RuntimeError("reader build/QA is not PASS")
    for key in ("html", "pdf"):
        verify_identity(reader_build[key])
        verify_identity(reader_qa[key])
        if reader_build[key] != {name: value for name, value in reader_qa[key].items() if name in reader_build[key]}:
            raise RuntimeError(f"reader build/QA identity differs: {key}")


def verify_backend() -> None:
    manifest = json.loads((PACKET / "backend/BACKEND_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["status"] != "PASS" or set(manifest["entity_counts"]) != REQUIRED_ENTITIES:
        raise RuntimeError("backend manifest lacks a required entity class or PASS")
    for item in manifest["exports"]:
        verify_identity(item)
    jsonl_path = PACKET / "backend/records.jsonl"
    raw_lines = [line for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line]
    rows = [json.loads(line) for line in raw_lines]
    if len(rows) != manifest["record_count"] or rows != sorted(rows, key=lambda item: (item["entity"], item["id"])):
        raise RuntimeError("backend record count or canonical sort failed")
    schema = json.loads((PACKET / "contracts/backend-record-v0.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for raw_line, row in zip(raw_lines, rows, strict=True):
        validator.validate(row)
        if set(row) != set(BACKEND_FIELDS):
            raise RuntimeError(f"backend field set differs: {row['id']}")
        if raw_line != canonical(row):
            raise RuntimeError(f"backend JSONL record is not canonically serialized: {row['id']}")
    with (PACKET / "backend/records.csv").open("r", encoding="utf-8", newline="") as stream:
        csv_rows = [{key: json.loads(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    if csv_rows != rows:
        raise RuntimeError("backend canonical JSON-cell CSV round-trip differs")


def verify_handoff_and_checksums() -> dict[str, object]:
    handoff_path = PACKET / "HANDOFF.json"
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    if set(handoff) != HANDOFF_FIELDS:
        raise RuntimeError(f"HANDOFF fields differ: {sorted(set(handoff) ^ HANDOFF_FIELDS)}")
    if handoff["packet_id"] != "HP-A30-003" or handoff["assigned_semantic_unit_ids"] != list(MODULES):
        raise RuntimeError("HANDOFF packet/scope mismatch")
    output_files = handoff["output_files"]
    paths = [item["path"] for item in output_files]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise RuntimeError("HANDOFF output file list is not unique and sorted")
    for item in output_files:
        verify_identity(item)
    aggregate = hashlib.sha256(canonical(output_files).encode("utf-8")).hexdigest()
    if aggregate != handoff["aggregate_sha256"]:
        raise RuntimeError("HANDOFF aggregate differs")

    expected_checksum_paths = set(paths) | {"HANDOFF.json"}
    observed: dict[str, str] = {}
    for line in (PACKET / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        if relative in observed:
            raise RuntimeError(f"duplicate checksum path: {relative}")
        observed[relative] = digest
    if set(observed) != expected_checksum_paths:
        raise RuntimeError("checksums.sha256 file set differs from HANDOFF outputs plus HANDOFF.json")
    for relative, digest in observed.items():
        if sha(safe_path(relative)) != digest:
            raise RuntimeError(f"checksum mismatch: {relative}")
    return {"aggregate_sha256": aggregate, "checksums_entries": len(observed), "output_files": len(output_files)}


def main() -> None:
    verify_source_and_contracts()
    verify_qa_and_readers()
    verify_backend()
    result = verify_handoff_and_checksums()
    closure = json.loads((PACKET / "closure_manifest.json").read_text(encoding="utf-8"))
    if closure["status"] != "PASS" or closure["counts"]["reader_slots"] != 5118:
        raise RuntimeError("closure manifest is not PASS")
    result.update({"packet_id": "HP-A30-003", "status": "PASS"})
    print(canonical(result))


if __name__ == "__main__":
    main()
