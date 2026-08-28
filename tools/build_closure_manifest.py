#!/usr/bin/env python3
"""Generate the exact source/dependency/asset/output closure for HP-A30-003."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


PACKET = Path(__file__).resolve().parents[1]
MODULES = (
    "m49386", "m49387", "m49389", "m49390", "m49392", "m49393",
    "m49395", "m49396", "m49397", "m49398", "m49399",
)
OVERLAYS = {
    "m49386": "tools/agent_a_overlays/m49386.json",
    "m49387": "tools/agent_a_overlays/m49387.json",
    "m49389": "tools/agent_b_m49389_translations.json",
    "m49390": "tools/agent_b_m49390_translations.json",
    "m49392": "tools/agent_b_m49392_translations.json",
    "m49393": "tools/agent_c_m49393_final.json",
    "m49395": "tools/agent_a_overlays/m49395.json",
    "m49396": "tools/agent_c_m49396_final.json",
    "m49397": "tools/agent_c_m49397_final.json",
    "m49398": "work/m49398_translation_overlay.json",
    "m49399": "work/m49399_translation_overlay.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(PACKET).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


def main() -> None:
    source_manifest_path = PACKET / "source_manifest.json"
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    contract_manifest_path = PACKET / "contract_manifest.json"
    contract_manifest = json.loads(contract_manifest_path.read_text(encoding="utf-8"))
    if source_manifest["assigned_modules"] != list(MODULES):
        raise RuntimeError("module boundary mismatch")
    if source_manifest["assigned_source_orders"] != [38, 48]:
        raise RuntimeError("source-order boundary mismatch")

    source_modules = []
    translated_modules = []
    for source_record in source_manifest["modules"]:
        module = source_record["module_id"]
        source = PACKET / source_record["path"]
        if source.stat().st_size != source_record["bytes"] or sha(source) != source_record["sha256"]:
            raise RuntimeError(f"frozen source drift: {module}")
        source_modules.append({**identity(source), "module_id": module, "source_order": source_record["source_order"], "title": source_record["title"]})
        target = PACKET / f"translated/modules/{module}/index.cnxml"
        overlay = PACKET / OVERLAYS[module]
        module_qa = PACKET / f"qa/{module}_qa.json"
        qa_record = json.loads(module_qa.read_text(encoding="utf-8"))
        if qa_record["status"] != "PASS" or qa_record["target"]["sha256"] != sha(target):
            raise RuntimeError(f"current-byte module QA drift: {module}")
        translated_modules.append({
            "module_id": module,
            "source_order": source_record["source_order"],
            "target": identity(target),
            "overlay": identity(overlay),
            "qa": identity(module_qa),
            "reader_slots": qa_record["coverage"]["translated_slots"],
        })

    contracts = []
    for contract in contract_manifest["contracts"]:
        path = PACKET / contract["packet_path"]
        if path.stat().st_size != contract["bytes"] or sha(path) != contract["sha256"]:
            raise RuntimeError(f"frozen contract drift: {contract['packet_path']}")
        contracts.append({**identity(path), "source_locator": contract["source_locator"]})

    assets = []
    for asset in source_manifest["assets"]:
        source_copy = PACKET / "source" / asset["path"]
        translated_copy = PACKET / "translated" / asset["path"]
        if source_copy.stat().st_size != asset["bytes"] or sha(source_copy) != asset["sha256"]:
            raise RuntimeError(f"source asset drift: {asset['path']}")
        if source_copy.read_bytes() != translated_copy.read_bytes():
            raise RuntimeError(f"translated asset differs: {asset['path']}")
        assets.append({
            "path": asset["path"],
            "bytes": asset["bytes"],
            "sha256": asset["sha256"],
            "source_copy": "source/" + asset["path"],
            "translated_copy": "translated/" + asset["path"],
            "byte_identical": True,
        })

    packet_qa = PACKET / "qa/PACKET_QA.json"
    packet_qa_data = json.loads(packet_qa.read_text(encoding="utf-8"))
    if packet_qa_data["status"] != "PASS":
        raise RuntimeError("aggregate packet QA is not PASS")
    result = {
        "schema_id": "hp-a30-003-dependency-asset-closure-v1",
        "packet_id": "HP-A30-003",
        "status": "PASS",
        "scope": {
            "source_orders": [38, 48],
            "module_ids": list(MODULES),
            "module_count": len(MODULES),
            "neighboring_modules_included": False,
        },
        "authority": {
            "repository": source_manifest["repository"],
            "commit": source_manifest["commit"],
            "tree": source_manifest["tree"],
            "source_manifest": identity(source_manifest_path),
            "contract_manifest": identity(contract_manifest_path),
        },
        "source_modules": source_modules,
        "translated_modules": translated_modules,
        "contracts": contracts,
        "external_module_dependencies": source_manifest["external_module_dependencies"],
        "assets": assets,
        "counts": {
            "source_modules": len(source_modules),
            "translated_modules": len(translated_modules),
            "reader_slots": sum(item["reader_slots"] for item in translated_modules),
            "contracts": len(contracts),
            "external_module_dependencies": len(source_manifest["external_module_dependencies"]),
            "unique_assets": len(assets),
        },
        "checks": {
            "source_hashes": "PASS",
            "contract_hashes": "PASS",
            "current_target_qa_bindings": "PASS",
            "asset_source_and_translated_copy_identity": "PASS",
            "scope_boundary": "PASS",
        },
    }
    output = PACKET / "closure_manifest.json"
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    output.write_text(payload, encoding="utf-8", newline="\n")
    if output.read_text(encoding="utf-8") != payload:
        raise RuntimeError("closure manifest write/read mismatch")
    print(json.dumps({"path": "closure_manifest.json", "bytes": output.stat().st_size, "sha256": sha(output), "status": "PASS"}, sort_keys=True))


if __name__ == "__main__":
    main()
