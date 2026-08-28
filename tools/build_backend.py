#!/usr/bin/env python3
"""Build and validate the deterministic modular-backend fragment for HP-A30-003."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import jsonschema


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
SCHEMA_NAME = "openstax-precalculus-2e-modular-backend"
SCHEMA_VERSION = "0.1.0"
TIMESTAMP = "2026-08-28T00:00:00Z"
PROGRAM = "urn:interlanguage:program:open-and-share-alike-educational-materials-translations"
COURSE = "urn:interlanguage:course:openstax:precalculus"
RESOURCE = "urn:interlanguage:resource:openstax:precalculus-2e"
EDITION = "urn:interlanguage:edition:openstax:precalculus-2e:id-ID"
RIGHTS = "urn:interlanguage:rights:openstax:precalculus-2e:cc-by-nc-sa-4.0"
WORKFLOW = "HP-A30-003 deterministic helper workflow"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
FIELDS = (
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
CONCEPTS = {
    "periodic-function": ("periodic function", "fungsi periodik"),
    "sinusoidal-function": ("sinusoidal function", "fungsi sinusoidal"),
    "sine-function": ("sine function", "fungsi sinus"),
    "cosine-function": ("cosine function", "fungsi kosinus"),
    "tangent-function": ("tangent function", "fungsi tangen"),
    "cotangent-function": ("cotangent function", "fungsi kotangen"),
    "secant-function": ("secant function", "fungsi sekan"),
    "cosecant-function": ("cosecant function", "fungsi kosekan"),
    "inverse-trigonometric-function": ("inverse trigonometric function", "fungsi trigonometri invers"),
    "amplitude": ("amplitude", "amplitudo"),
    "period": ("period", "periode"),
    "phase-shift": ("phase shift", "pergeseran fase"),
    "midline": ("midline", "garis tengah"),
    "asymptote": ("asymptote", "asimtot"),
    "trigonometric-identity": ("trigonometric identity", "identitas trigonometri"),
    "pythagorean-identity": ("Pythagorean identity", "identitas Pythagoras"),
    "sum-difference-identity": ("sum and difference identity", "identitas jumlah dan selisih"),
    "double-angle-formula": ("double-angle formula", "rumus sudut rangkap"),
    "half-angle-formula": ("half-angle formula", "rumus setengah sudut"),
    "power-reduction-formula": ("power-reduction formula", "rumus penurunan pangkat"),
    "sum-to-product-formula": ("sum-to-product formula", "rumus jumlah menjadi hasil kali"),
    "product-to-sum-formula": ("product-to-sum formula", "rumus hasil kali menjadi jumlah"),
    "trigonometric-equation": ("trigonometric equation", "persamaan trigonometri"),
    "simple-harmonic-motion": ("simple harmonic motion", "gerak harmonik sederhana"),
    "damped-harmonic-motion": ("damped harmonic motion", "gerak harmonik teredam"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return result or hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def load_pipeline():
    path = PACKET / "tools/cnxml_pipeline.py"
    spec = importlib.util.spec_from_file_location("hp_a30_backend_cnxml", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PIPE = load_pipeline()


def record(
    entity: str,
    identity: str,
    *,
    source_local_id: str | None = None,
    source_label: str | None = None,
    parent_id: str | None = None,
    order: int | None = None,
    path: list[str] | None = None,
    source_locator: str | None = None,
    source_sha256: str | None = None,
    translation_state: str | None = None,
    source_record_id: str | None = None,
    concept_ids: list[str] | None = None,
    prerequisite_ids: list[str] | None = None,
    rights_id: str | None = RIGHTS,
    status: str = "active",
    qa_event_ids: list[str] | None = None,
    artifact_ids: list[str] | None = None,
    data: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "entity": entity,
        "id": identity,
        "source_local_id": source_local_id,
        "source_label": source_label,
        "parent_id": parent_id,
        "order": order,
        "path": path or [],
        "resource_id": RESOURCE,
        "edition_id": EDITION,
        "source_locator": source_locator,
        "source_sha256": source_sha256,
        "language": "Indonesian",
        "locale": "id-ID",
        "translation_state": translation_state,
        "source_record_id": source_record_id,
        "provenance": {
            "packet_id": "HP-A30-003",
            "helper_thread_id": "01a01f58-86dc-7692-89df-8edc30c8ec38",
            "canonical_owner_thread_id": "01a01f42-6678-7043-89c5-87cc465202e8",
            "source_repository": "openstax/osbooks-college-algebra-bundle",
            "source_commit": "789b54099106b071d1d32bfcee454fed72eb4768",
            "source_tree": "05b39123f698772482c0c33a43fa2d2d4ea562ae",
            "translation_localization_assistance": MODEL,
        },
        "concept_ids": concept_ids or [],
        "prerequisite_ids": prerequisite_ids or [],
        "rights_id": rights_id,
        "status": status,
        "timestamp": TIMESTAMP,
        "responsible_workflow": WORKFLOW,
        "supersedes_id": None,
        "qa_event_ids": qa_event_ids or [],
        "artifact_ids": artifact_ids or [],
        "data": data or {},
    }


def concept_ids(text: str) -> list[str]:
    lower = text.casefold()
    found: list[str] = []
    for key, (english, _indonesian) in CONCEPTS.items():
        variants = {english.casefold(), english.casefold().replace(" function", ""), english.casefold().replace(" formula", "")}
        if any(len(variant) >= 5 and variant in lower for variant in variants):
            found.append(f"urn:interlanguage:concept:openstax:precalculus-2e:{key}")
    return sorted(set(found))


def overlay_for(module: str) -> tuple[Path, dict[int, str]]:
    path = PACKET / OVERLAYS[module]
    raw = json.loads(path.read_text(encoding="utf-8"))
    values = raw.get("translations", raw)
    return path, {int(key): str(value) for key, value in values.items()}


def exact_slots(module: str) -> tuple[list[tuple[str, str, str]], dict[int, str]]:
    source = PACKET / f"source/modules/{module}/index.cnxml"
    target = PACKET / f"translated/modules/{module}/index.cnxml"
    source_root = PIPE.parse_xml(source.read_bytes())
    slots = PIPE.extract_text_slots(source_root)
    _overlay_path, mapping = overlay_for(module)
    if set(mapping) != set(range(1, len(slots) + 1)):
        raise RuntimeError(f"{module}: backend overlay coverage mismatch")
    rebuilt = PIPE.apply_text_overlay(source_root, mapping)
    PIPE.validate_preservation(source_root, rebuilt, module)
    ET.register_namespace("", PIPE.CNXML)
    ET.register_namespace("m", PIPE.MATHML)
    ET.register_namespace("md", PIPE.MDML)
    if ET.tostring(rebuilt, encoding="utf-8", short_empty_elements=True) != target.read_bytes():
        raise RuntimeError(f"{module}: backend overlay does not reproduce target")
    return slots, mapping


def source_relations(module: str, module_source_sha: str) -> list[dict[str, object]]:
    source = PACKET / f"source/modules/{module}/index.cnxml"
    root = PIPE.parse_xml(source.read_bytes())
    unit_id = f"urn:interlanguage:unit:openstax:precalculus-2e:{module}"
    rows: list[dict[str, object]] = []
    number = 0
    for element_number, element in enumerate(root.iter(), start=1):
        if PIPE.local_name(element.tag) == "#comment":
            continue
        local_id = element.attrib.get("id")
        for attribute in ("target-id", "document", "url"):
            if attribute not in element.attrib:
                continue
            number += 1
            rows.append(record(
                "relation", f"urn:interlanguage:relation:openstax:precalculus-2e:{module}:xref:{number:05d}",
                source_local_id=local_id, source_label="source cross-reference", parent_id=unit_id,
                order=number, path=[module, "relations", f"xref-{number:05d}"],
                source_locator=f"source/modules/{module}/index.cnxml#element-{element_number}",
                source_sha256=module_source_sha, translation_state="structurally_verified",
                data={"relation_type": "cross_reference", "attribute": attribute, "target": element.attrib[attribute]},
            ))
        if PIPE.local_name(element.tag) != "exercise":
            continue
        exercise_id = local_id or f"element-{element_number}"
        for descendant_number, descendant in enumerate(element.iter(), start=1):
            role = PIPE.local_name(descendant.tag)
            if role not in {"problem", "solution"}:
                continue
            number += 1
            rows.append(record(
                "relation", f"urn:interlanguage:relation:openstax:precalculus-2e:{module}:exercise:{number:05d}",
                source_local_id=descendant.attrib.get("id"), source_label=f"exercise {role}", parent_id=unit_id,
                order=number, path=[module, "exercises", exercise_id, role, str(descendant_number)],
                source_locator=f"source/modules/{module}/index.cnxml#{exercise_id}",
                source_sha256=module_source_sha, translation_state="structurally_verified",
                data={"relation_type": f"exercise_to_{role}", "exercise_local_id": exercise_id},
            ))
    return rows


def load_json_list(path: Path, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
    return []


def normalized_terms() -> list[dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    consolidated = load_json_list(PACKET / "terminology_proposals.json", ("proposals", "terms", "records"))
    if not consolidated:
        consolidated = [
            {"source_term": source, "preferred_id": target, "modules": list(MODULES),
             "status": "packet_usage_and_owner_proposal", "rationale": "Used consistently in the packet translation."}
            for source, target in CONCEPTS.values()
        ]
    for item in consolidated:
        source = str(item.get("source_term") or item.get("source") or "").strip()
        target = str(item.get("proposed_id_id") or item.get("proposed_id") or item.get("preferred_id") or "").strip()
        if source and target:
            rows[(source.casefold(), target.casefold())] = {**item, "source_term": source, "proposed_id_id": target}
    return [rows[key] for key in sorted(rows)]


def normalized_corrections() -> list[dict[str, Any]]:
    values = load_json_list(PACKET / "correction_observations.json", ("observations", "corrections", "records"))
    if not values:
        raise RuntimeError("correction_observations.json is missing or contains no observations")
    return values


def build_records() -> list[dict[str, object]]:
    manifest_path = PACKET / "source_manifest.json"
    source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if source_manifest["assigned_modules"] != list(MODULES) or source_manifest["assigned_source_orders"] != [38, 48]:
        raise RuntimeError("source manifest scope differs from HP-A30-003")
    module_data = {item["module_id"]: item for item in source_manifest["modules"]}
    packet_qa_path = PACKET / "qa/PACKET_QA.json"
    reader_qa_path = PACKET / "qa/READER_QA.json"
    packet_qa = json.loads(packet_qa_path.read_text(encoding="utf-8"))
    reader_qa = json.loads(reader_qa_path.read_text(encoding="utf-8"))
    if str(packet_qa["status"]).upper() != "PASS" or str(reader_qa["status"]).upper() != "PASS":
        raise RuntimeError("backend requires PASS packet and reader QA")

    rows = [
        record("program", PROGRAM, source_local_id="open-and-share-alike-translations", source_label="Open and Share-Alike Educational Materials Translations", rights_id=None, translation_state=None, data={"packet_role": "isolated helper contribution"}),
        record("course", COURSE, source_local_id="precalculus", source_label="Precalculus", parent_id=PROGRAM, rights_id=None, translation_state=None, data={"discipline": "mathematics"}),
        record("resource", RESOURCE, source_local_id="precalculus-2e", source_label="OpenStax Precalculus 2e", parent_id=COURSE, source_locator="https://openstax.org/books/precalculus-2e/", translation_state="source_frozen", data={"author": "Jay Abramson", "publisher": "OpenStax, Rice University", "source_title": "Precalculus 2e"}),
        record("edition", EDITION, source_local_id="id-ID", source_label="Precalculus 2e — Edisi Bahasa Indonesia", parent_id=RESOURCE, translation_state="visually_checked", data={"coverage": "complete Chapters 6–7 within source orders 38–48", "packet_id": "HP-A30-003", "reader_slots": 5118}),
        record("rights", RIGHTS, source_local_id="CC-BY-NC-SA-4.0", source_label="Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International", parent_id=RESOURCE, source_locator="https://creativecommons.org/licenses/by-nc-sa/4.0/", rights_id=None, status="verified", data={"license_spdx_like": "CC-BY-NC-SA-4.0", "license_name": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International", "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/", "source_book_url": "https://openstax.org/books/precalculus-2e/", "attribution": "Access for free at https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions", "component_notice": "Figure and asset captions retain any component-specific credit or rights notice."}),
    ]

    for key, (source, target) in sorted(CONCEPTS.items()):
        rows.append(record("concept", f"urn:interlanguage:concept:openstax:precalculus-2e:{key}", source_local_id=key, source_label=source, parent_id=RESOURCE, path=["concepts", key], translation_state="language_reviewed", data={"source_term": source, "preferred_id_id": target}))

    for number, item in enumerate(normalized_terms(), start=1):
        source = str(item["source_term"]).strip()
        target = str(item["proposed_id_id"]).strip()
        modules = item.get("modules") or item.get("scope") or []
        if isinstance(modules, str):
            modules = [part for part in re.split(r"[;,]", modules) if part]
        rows.append(record(
            "term", f"urn:interlanguage:term:openstax:precalculus-2e:id-ID:{number:04d}:{slug(source)}",
            source_local_id=source, source_label=source, parent_id=EDITION, order=number,
            path=["terminology", f"{number:04d}"], source_locator="terminology_proposals.json",
            source_sha256=text_sha(source), translation_state="language_reviewed", concept_ids=concept_ids(source),
            status="proposal_only_owner_decides", data={"source_term": source, "proposed_id_id": target, "modules": list(modules), "rationale": item.get("rationale"), "register": item.get("register"), "variants": item.get("variants")},
        ))

    previous_unit: str | None = None
    for unit_order, module in enumerate(MODULES, start=1):
        source_info = module_data[module]
        slots, mapping = exact_slots(module)
        unit_id = f"urn:interlanguage:unit:openstax:precalculus-2e:{module}"
        qa_id = f"urn:interlanguage:qa:openstax:precalculus-2e:{module}:helper"
        artifact_id = f"urn:interlanguage:artifact:openstax:precalculus-2e:{module}:cnxml-id"
        rows.append(record(
            "unit", unit_id, source_local_id=module, source_label=mapping[1].strip(), parent_id=EDITION,
            order=unit_order, path=[module], source_locator=source_info["path"], source_sha256=source_info["sha256"],
            translation_state="mathematically_reviewed", source_record_id=module,
            concept_ids=concept_ids(source_info["title"]), prerequisite_ids=[previous_unit] if previous_unit else [],
            qa_event_ids=[qa_id], artifact_ids=[artifact_id],
            data={"source_order": source_info["source_order"], "source_title": source_info["title"], "reader_slots": len(slots)},
        ))
        if previous_unit:
            rows.append(record("relation", f"urn:interlanguage:relation:openstax:precalculus-2e:{module}:previous", source_label="source-order predecessor", parent_id=EDITION, order=unit_order, path=[module, "relations", "previous"], source_locator=source_info["path"], source_sha256=source_info["sha256"], translation_state="structurally_verified", data={"relation_type": "preceded_by", "source_unit_id": unit_id, "target_unit_id": previous_unit}))
        previous_unit = unit_id

        for slot, (locator, kind, source_text) in enumerate(slots, start=1):
            translated_text = mapping[slot]
            rows.append(record(
                "segment", f"urn:interlanguage:segment:openstax:precalculus-2e:{module}:slot:{slot:06d}",
                source_local_id=f"{module}:slot:{slot:06d}", parent_id=unit_id, order=slot,
                path=[module, "segments", f"{slot:06d}"], source_locator=locator, source_sha256=text_sha(source_text),
                translation_state="language_reviewed", source_record_id=f"urn:interlanguage:source:openstax:precalculus-2e:{module}:slot:{slot:06d}",
                concept_ids=concept_ids(source_text), qa_event_ids=[qa_id], artifact_ids=[artifact_id],
                data={"kind": kind, "source_text": source_text, "translated_text": translated_text, "translated_sha256": text_sha(translated_text)},
            ))

        rows.extend(source_relations(module, source_info["sha256"]))
        module_qa_path = PACKET / f"qa/{module}_qa.json"
        module_qa = json.loads(module_qa_path.read_text(encoding="utf-8"))
        rows.append(record(
            "qa_event", qa_id, source_local_id=module, source_label="current-byte module QA", parent_id=unit_id,
            path=[module, "qa"], source_locator=f"qa/{module}_qa.json", source_sha256=sha256(module_qa_path),
            translation_state="mathematically_reviewed", rights_id=None, status="pass",
            data={"coverage": module_qa["coverage"], "preservation": module_qa["preservation"], "math_and_numeric": module_qa["math_and_numeric"], "language": module_qa["language"], "assets": {key: value for key, value in module_qa["assets"].items() if key != "records"}, "repeat_build": module_qa["repeat_build"]},
        ))
        target = PACKET / f"translated/modules/{module}/index.cnxml"
        rows.append(record("artifact", artifact_id, source_local_id=module, source_label="translated CNXML", parent_id=unit_id, path=[module, "artifacts", "cnxml"], source_locator=f"translated/modules/{module}/index.cnxml", source_sha256=sha256(target), translation_state="built", qa_event_ids=[qa_id], data={"bytes": target.stat().st_size, "media_type": "application/xml"}))

    for number, dependency in enumerate(source_manifest["external_module_dependencies"], start=1):
        source_module = dependency["from_module"]
        target_module = dependency["reference"]
        rows.append(record("relation", f"urn:interlanguage:relation:openstax:precalculus-2e:dependency:{number:04d}", source_local_id=f"{source_module}->{target_module}", source_label="module dependency", parent_id=EDITION, order=number, path=["dependencies", f"{number:04d}"], source_locator=f"source/modules/{source_module}/index.cnxml", source_sha256=module_data[source_module]["sha256"], translation_state="structurally_verified", data={"relation_type": "module_reference", "from_module": source_module, "to_module": target_module, "target_in_packet": target_module in MODULES}))

    for number, asset in enumerate(source_manifest["assets"], start=1):
        source_copy = PACKET / "source" / asset["path"]
        translated_copy = PACKET / "translated" / asset["path"]
        if sha256(source_copy) != asset["sha256"] or source_copy.read_bytes() != translated_copy.read_bytes():
            raise RuntimeError(f"asset byte closure failed: {asset['path']}")
        referencing = [item["module_id"] for item in source_manifest["modules"] if asset["path"] in item["active_assets"]]
        rows.append(record("asset", f"urn:interlanguage:asset:openstax:precalculus-2e:{asset['sha256']}", source_local_id=Path(asset["path"]).name, source_label=Path(asset["path"]).name, parent_id=EDITION, order=number, path=["assets", Path(asset["path"]).name], source_locator="source/" + asset["path"], source_sha256=asset["sha256"], translation_state="structurally_verified", data={"bytes": asset["bytes"], "referenced_by_modules": referencing, "translated_copy": "translated/" + asset["path"], "translated_copy_byte_identical": True}))

    packet_qa_id = "urn:interlanguage:qa:openstax:precalculus-2e:HP-A30-003"
    reader_qa_id = "urn:interlanguage:qa:openstax:precalculus-2e:HP-A30-003:reader"
    rows.extend([
        record("qa_event", packet_qa_id, source_local_id="HP-A30-003", source_label="aggregate current-byte packet QA", parent_id=EDITION, path=["qa", "packet"], source_locator="qa/PACKET_QA.json", source_sha256=sha256(packet_qa_path), translation_state="mathematically_reviewed", rights_id=None, status="pass", data=packet_qa),
        record("qa_event", reader_qa_id, source_local_id="HP-A30-003-reader", source_label="reader render and visual QA", parent_id=EDITION, path=["qa", "reader"], source_locator="qa/READER_QA.json", source_sha256=sha256(reader_qa_path), translation_state="visually_checked", rights_id=None, status="pass", data=reader_qa),
    ])

    for kind, filename, media_type, state in (
        ("pdf-reader", "preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.pdf", "application/pdf", "visually_checked"),
        ("html-reader", "preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.html", "text/html", "built"),
        ("source-manifest", "source_manifest.json", "application/json", "built"),
    ):
        file_path = PACKET / filename
        rows.append(record("artifact", f"urn:interlanguage:artifact:openstax:precalculus-2e:HP-A30-003:{kind}", source_local_id="HP-A30-003", source_label=kind, parent_id=EDITION, path=["artifacts", kind], source_locator=filename, source_sha256=sha256(file_path), translation_state=state, qa_event_ids=[reader_qa_id] if "reader" in kind else [packet_qa_id], data={"bytes": file_path.stat().st_size, "media_type": media_type}))

    for number, item in enumerate(normalized_corrections(), start=1):
        module = str(item.get("module_id") or item.get("module") or "packet")
        source_excerpt = str(item.get("source_excerpt") or item.get("source_text") or item.get("source") or "")
        correction = str(item.get("proposed_correction") or item.get("high_confidence_correction") or item.get("correction") or item.get("observation") or "")
        rows.append(record("correction", f"urn:interlanguage:correction:openstax:precalculus-2e:HP-A30-003:{number:04d}", source_local_id=str(item.get("observation_id") or f"HP-A30-003-CORR-{number:04d}"), source_label=source_excerpt[:240] or "source correction observation", parent_id=EDITION, order=number, path=["corrections", f"{number:04d}"], source_locator=str(item.get("locator") or "correction_observations.json"), source_sha256=text_sha(source_excerpt) if source_excerpt else None, translation_state=None, status="reported_for_owner_review", data={**item, "normalized_module_id": module, "normalized_proposed_correction": correction}))

    rows.sort(key=lambda item: (str(item["entity"]), str(item["id"])))
    return rows


def main() -> None:
    rows = build_records()
    identities = [str(item["id"]) for item in rows]
    if len(identities) != len(set(identities)):
        raise RuntimeError("backend record IDs are not unique")
    entity_counts = Counter(str(item["entity"]) for item in rows)
    missing = REQUIRED_ENTITIES - set(entity_counts)
    if missing:
        raise RuntimeError(f"missing required backend entity classes: {sorted(missing)}")
    if entity_counts["segment"] != 5118 or entity_counts["unit"] != 11 or entity_counts["asset"] != 196:
        raise RuntimeError(f"unexpected principal entity counts: {dict(entity_counts)}")

    schema = json.loads((PACKET / "contracts/backend-record-v0.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for item in rows:
        validator.validate(item)
        if tuple(item) != FIELDS:
            raise RuntimeError(f"record fields/order differ for {item['id']}")

    jsonl_payload = "".join(canonical(item) + "\n" for item in rows)
    second_jsonl_payload = "".join(canonical(item) + "\n" for item in build_records())
    if jsonl_payload != second_jsonl_payload:
        raise RuntimeError("two-run backend record build differs")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for item in rows:
        writer.writerow({key: canonical(item[key]) for key in FIELDS})
    csv_payload = buffer.getvalue()
    rebuilt: list[dict[str, object]] = []
    for item in csv.DictReader(io.StringIO(csv_payload, newline="")):
        rebuilt.append({key: json.loads(item[key]) for key in FIELDS})
    if rebuilt != rows:
        raise RuntimeError("canonical JSON-cell CSV round-trip differs")

    backend = PACKET / "backend"
    backend.mkdir(parents=True, exist_ok=True)
    jsonl = backend / "records.jsonl"
    csv_path = backend / "records.csv"
    jsonl.write_text(jsonl_payload, encoding="utf-8", newline="\n")
    csv_path.write_text(csv_payload, encoding="utf-8", newline="\n")
    manifest = {
        "checks": {"all_28_required_fields": "PASS", "canonical_entity_id_sort": "PASS", "csv_canonical_json_cell_round_trip": "PASS", "exact_overlay_to_target_reproduction": "PASS", "json_schema_draft_2020_12": "PASS", "two_run_record_build": "PASS"},
        "entity_counts": dict(sorted(entity_counts.items())),
        "exports": [
            {"bytes": jsonl.stat().st_size, "path": "backend/records.jsonl", "sha256": sha256(jsonl)},
            {"bytes": csv_path.stat().st_size, "path": "backend/records.csv", "sha256": sha256(csv_path)},
        ],
        "packet_id": "HP-A30-003", "record_count": len(rows),
        "schema_id": "hp-a30-003-backend-manifest-v2", "schema_version": SCHEMA_VERSION, "status": "PASS",
    }
    manifest_path = backend / "BACKEND_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(canonical({"entity_counts": manifest["entity_counts"], "manifest_sha256": sha256(manifest_path), "records": len(rows), "status": "PASS"}))


if __name__ == "__main__":
    main()
