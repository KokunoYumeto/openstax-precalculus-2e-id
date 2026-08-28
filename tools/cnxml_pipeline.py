#!/usr/bin/env python3
"""Deterministic reader-slot extraction, overlay, and preservation checks."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET


PACKET = Path(__file__).resolve().parents[1]
CNXML = "http://cnx.rice.edu/cnxml"
MATHML = "http://www.w3.org/1998/Math/MathML"
MDML = "http://cnx.rice.edu/mdml"
MODULES = (
    "m49386", "m49387", "m49389", "m49390", "m49392", "m49393",
    "m49395", "m49396", "m49397", "m49398", "m49399",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_xml(payload: bytes) -> ET.Element:
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.fromstring(payload, parser=parser)


def local_name(tag: object) -> str:
    if tag is ET.Comment or not isinstance(tag, str):
        return "#comment"
    return tag.rsplit("}", 1)[-1]


def element_paths(root: ET.Element) -> dict[int, str]:
    paths: dict[int, str] = {}

    def walk(element: ET.Element, path: str) -> None:
        paths[id(element)] = path
        counts: dict[str, int] = {}
        for child in list(element):
            name = local_name(child.tag)
            counts[name] = counts.get(name, 0) + 1
            walk(child, f"{path}/{name}[{counts[name]}]")

    walk(root, f"/{local_name(root.tag)}[1]")
    return paths


def extract_text_slots(root: ET.Element, *, include_blank: bool = False) -> list[tuple[str, str, str]]:
    paths = element_paths(root)
    slots: list[tuple[str, str, str]] = []

    def add(locator: str, kind: str, value: str | None) -> None:
        if include_blank or (value is not None and value.strip()):
            slots.append((locator, kind, value or ""))

    def walk(element: ET.Element, inside_math: bool = False) -> None:
        name = local_name(element.tag)
        if name == "#comment":
            return
        current_math = inside_math or (
            isinstance(element.tag, str) and element.tag.startswith("{" + MATHML + "}")
        )
        if name not in {"content-id", "uuid"} and (not current_math or name == "mtext"):
            add(paths[id(element)] + "/text()", "text", element.text)
        for attr in ("alt", "summary"):
            if attr in element.attrib:
                add(paths[id(element)] + f"/@{attr}", f"attribute:{attr}", element.attrib[attr])
        for child in list(element):
            walk(child, current_math)
            if not current_math:
                add(paths[id(child)] + "/tail()", "tail", child.tail)

    walk(root)
    return slots


def apply_text_overlay(source_root: ET.Element, translations: dict[int, str]) -> ET.Element:
    target = copy.deepcopy(source_root)
    slots = extract_text_slots(target)
    if set(translations) != set(range(1, len(slots) + 1)):
        missing = sorted(set(range(1, len(slots) + 1)) - set(translations))
        extra = sorted(set(translations) - set(range(1, len(slots) + 1)))
        raise RuntimeError(f"translation slot coverage differs: missing={missing[:10]} extra={extra[:10]}")
    paths = element_paths(target)
    inverse = {path: element for element in target.iter() for path in [paths[id(element)]]}
    for index, (locator, kind, _source) in enumerate(slots, start=1):
        value = translations[index]
        if kind == "text":
            inverse[locator.removesuffix("/text()")].text = value
        elif kind == "tail":
            inverse[locator.removesuffix("/tail()")].tail = value
        elif kind.startswith("attribute:"):
            attr = kind.split(":", 1)[1]
            inverse[locator.rsplit("/@", 1)[0]].set(attr, value)
        else:
            raise RuntimeError(kind)
    return target


def validate_preservation(source: ET.Element, target: ET.Element, module: str) -> dict[str, int]:
    counts = {"elements": 0, "ids": 0, "mathml_elements": 0, "images": 0, "xrefs": 0, "comments": 0}

    def exact_text(a: str | None, b: str | None) -> bool:
        return a == b or (not (a or "").strip() and not (b or "").strip())

    def walk(a: ET.Element, b: ET.Element, inside_math: bool = False) -> None:
        name = local_name(a.tag)
        if a.tag != b.tag:
            raise RuntimeError(f"{module}: tag mismatch at {name}")
        counts["elements"] += 1
        if name == "#comment":
            counts["comments"] += 1
            if a.text != b.text or a.attrib != b.attrib:
                raise RuntimeError(f"{module}: XML comment changed")
            return
        current_math = inside_math or (
            isinstance(a.tag, str) and a.tag.startswith("{" + MATHML + "}")
        )
        if current_math:
            counts["mathml_elements"] += 1
        if "id" in a.attrib:
            counts["ids"] += 1
        if name == "image":
            counts["images"] += 1
        if name in {"link", "xref"} or "target-id" in a.attrib or "document" in a.attrib:
            counts["xrefs"] += 1
        excluded = {"alt", "summary"}
        if {k: v for k, v in a.attrib.items() if k not in excluded} != {k: v for k, v in b.attrib.items() if k not in excluded}:
            raise RuntimeError(f"{module}: protected attribute mismatch at {a.attrib.get('id', name)}")
        if ("alt" in a.attrib) != ("alt" in b.attrib) or ("summary" in a.attrib) != ("summary" in b.attrib):
            raise RuntimeError(f"{module}: accessibility attribute presence mismatch")
        if name in {"content-id", "uuid"} and not exact_text(a.text, b.text):
            raise RuntimeError(f"{module}: protected metadata text mismatch")
        if current_math and name != "mtext" and not exact_text(a.text, b.text):
            raise RuntimeError(f"{module}: protected MathML text mismatch at {a.attrib.get('id', name)}")
        a_children = list(a)
        b_children = list(b)
        if len(a_children) != len(b_children):
            raise RuntimeError(f"{module}: child count mismatch at {a.attrib.get('id', name)}")
        for ac, bc in zip(a_children, b_children):
            walk(ac, bc, current_math)
            if current_math and not exact_text(ac.tail, bc.tail):
                raise RuntimeError(f"{module}: protected MathML tail mismatch")

    walk(source, target)
    source_ids = [element.attrib["id"] for element in source.iter() if "id" in element.attrib]
    target_ids = [element.attrib["id"] for element in target.iter() if "id" in element.attrib]
    if source_ids != target_ids or len(target_ids) != len(set(target_ids)):
        raise RuntimeError(f"{module}: ID sequence/set mismatch")
    return counts


def write_slots(module: str) -> None:
    source_path = PACKET / f"source/modules/{module}/index.cnxml"
    payload = source_path.read_bytes()
    root = parse_xml(payload)
    slots = extract_text_slots(root)
    record = {
        "schema_id": "hp-a30-cnxml-source-reader-slots-v1",
        "module_id": module,
        "source": {"path": f"source/modules/{module}/index.cnxml", "bytes": len(payload), "sha256": sha256_bytes(payload)},
        "slot_count": len(slots),
        "slots": [
            {"slot": index, "locator": locator, "kind": kind, "source": value}
            for index, (locator, kind, value) in enumerate(slots, start=1)
        ],
    }
    output = PACKET / f"work/{module}_source_slots.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"module": module, "slots": len(slots), "path": output.relative_to(PACKET).as_posix()}))


def build(module: str, translations_path: Path) -> None:
    source_path = PACKET / f"source/modules/{module}/index.cnxml"
    source_payload = source_path.read_bytes()
    source_root = parse_xml(source_payload)
    data = json.loads(translations_path.read_text(encoding="utf-8"))
    raw_mapping = data.get("translations", data)
    mapping = {int(key): value for key, value in raw_mapping.items()}
    if not all(isinstance(value, str) for value in mapping.values()):
        raise RuntimeError("all translation values must be strings")
    target_root = apply_text_overlay(source_root, mapping)
    counts = validate_preservation(source_root, target_root, module)
    ET.register_namespace("", CNXML)
    ET.register_namespace("m", MATHML)
    ET.register_namespace("md", MDML)
    payload = ET.tostring(target_root, encoding="utf-8", short_empty_elements=True)
    reparsed = parse_xml(payload)
    validate_preservation(source_root, reparsed, module)
    output = PACKET / f"translated/modules/{module}/index.cnxml"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    result = {
        "module_id": module,
        "source_bytes": len(source_payload),
        "source_sha256": sha256_bytes(source_payload),
        "target_bytes": len(payload),
        "target_sha256": sha256_bytes(payload),
        "reader_slots": len(mapping),
        "preservation": counts,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("modules", nargs="*", default=list(MODULES))
    build_parser = sub.add_parser("build")
    build_parser.add_argument("module")
    build_parser.add_argument("translations", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        for module in args.modules:
            if module not in MODULES:
                raise SystemExit(f"out-of-scope module: {module}")
            write_slots(module)
    else:
        if args.module not in MODULES:
            raise SystemExit(f"out-of-scope module: {args.module}")
        build(args.module, args.translations)


if __name__ == "__main__":
    main()
