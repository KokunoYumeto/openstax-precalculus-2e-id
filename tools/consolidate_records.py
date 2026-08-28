#!/usr/bin/env python3
"""Build normalized terminology proposals and source-correction observations.

This helper reads only frozen HP-A30-003 evidence and writes only the four
packet-root consolidation artifacts requested by the canonical owner.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


PACKET = Path(__file__).resolve().parents[1]
MODULE_ORDER = (
    "m49386",
    "m49387",
    "m49389",
    "m49390",
    "m49392",
    "m49393",
    "m49395",
    "m49396",
    "m49397",
    "m49398",
    "m49399",
)

TERM_FIELDS = (
    "proposal_id",
    "source_term",
    "preferred_id",
    "variants",
    "rejected",
    "modules",
    "register",
    "confidence",
    "status",
    "evidence",
    "rationale",
    "owner_contract_match",
)

CORRECTION_FIELDS = (
    "module",
    "slot",
    "locator",
    "source",
    "correction",
    "disposition",
    "confidence",
)


def term(
    source_term: str,
    preferred_id: str,
    modules: str,
    evidence: str,
    rationale: str,
    *,
    variants: str = "",
    rejected: str = "",
    register: str = "formal",
) -> dict[str, str]:
    return {
        "source_term": source_term,
        "preferred_id": preferred_id,
        "variants": variants,
        "rejected": rejected,
        "modules": modules,
        "register": register,
        "confidence": "high",
        "evidence": evidence,
        "rationale": rationale,
    }


# One record per concept. Combined source-agent entries have been split, and
# duplicates across agents have been merged by source concept.
TERMS = [
    term("periodic function", "fungsi periodik", "m49386;m49387;m49399", "qa/agent_a/terminology_proposals.json; m49399 slots 10-11", "Standard Indonesian function terminology."),
    term("sine function", "fungsi sinus", "m49386;m49387;m49395;m49398;m49399", "qa/agent_a/terminology_proposals.json; m49398 recurring equation prose", "Standard Indonesian trigonometry; use sinus rather than English sine in prose."),
    term("cosine function", "fungsi kosinus", "m49386;m49387;m49389;m49390;m49395;m49398;m49399", "qa/agent_a/terminology_proposals.json; qa/agent_b/terminology_proposals.csv", "Standard Indonesian spelling uses kosinus."),
    term("tangent function", "fungsi tangen", "m49389;m49390;m49396;m49398", "qa/agent_b/terminology_proposals.csv", "Names the trigonometric function and avoids the geometric-line sense garis singgung."),
    term("cotangent function", "fungsi kotangen", "m49389;m49396", "qa/agent_b/terminology_proposals.csv", "Conventional ko- spelling, parallel with kosinus and kosekan."),
    term("secant function", "fungsi sekan", "m49389;m49390;m49398", "qa/agent_b/terminology_proposals.csv", "Names the trigonometric function and avoids the geometric-line sense garis potong."),
    term("cosecant function", "fungsi kosekan", "m49389;m49398", "qa/agent_b/terminology_proposals.csv", "Conventional Indonesian spelling paired with sekan."),
    term("sinusoidal function", "fungsi sinusoidal", "m49387;m49399", "qa/agent_a/terminology_proposals.json; m49399 slots 5 and 479-483", "Distinguishes the broader sinusoidal class from the sine function itself."),
    term("period", "periode", "m49387;m49389;m49390;m49398;m49399", "qa/agent_a/terminology_proposals.json; qa/agent_b/terminology_proposals.csv", "Established function and oscillation terminology."),
    term("amplitude", "amplitudo", "m49387;m49389;m49390;m49399", "qa/agent_a/terminology_proposals.json; m49399 recurring harmonic-motion prose", "Established wave and function terminology."),
    term("midline", "garis tengah", "m49387;m49399", "qa/agent_a/terminology_proposals.json; m49399 graphing prose", "Names the horizontal center line of a sinusoidal graph.", variants="garis tengah grafik", register="pedagogical formal"),
    term("phase shift", "pergeseran fase", "m49387;m49389;m49390;m49399", "qa/agent_a/terminology_proposals.json; qa/agent_b/terminology_proposals.csv", "Established transformation terminology."),
    term("vertical shift", "pergeseran vertikal", "m49387;m49399", "qa/agent_a/terminology_proposals.json", "Matches the existing transformation contract."),
    term("horizontal shift", "pergeseran horizontal", "m49387;m49399", "qa/agent_a/terminology_proposals.json", "Matches the existing transformation contract."),
    term("exact value", "nilai eksak", "m49390;m49395;m49396;m49398", "qa/agent_a/terminology_proposals.json; qa/agent_b/terminology_proposals.csv; qa/agent_c/terminology_proposals.json", "Distinguishes a symbolic exact value from an approximation."),
    term("exact solution", "solusi eksak", "m49398", "m49398 slots 29, 39, 96, 368, 374, and 380", "Concise equation-solving counterpart to nilai eksak."),
    term("sum formula", "rumus jumlah", "m49395;m49396", "qa/agent_a/terminology_proposals.json", "Pairs consistently with rumus selisih."),
    term("difference formula", "rumus selisih", "m49395;m49397", "qa/agent_a/terminology_proposals.json", "The operation is subtraction; selisih is more precise than perbedaan."),
    term("Pythagorean identities", "identitas Pythagoras", "m49393;m49395;m49396", "qa/agent_a/terminology_proposals.json; qa/agent_c/terminology_proposals.json", "Standard name for the family of trigonometric identities."),
    term("cofunction", "kofungsi", "m49395", "qa/agent_a/terminology_proposals.json", "Productive Indonesian mathematical compound."),
    term("cofunction identities", "identitas kofungsi", "m49395", "qa/agent_a/terminology_proposals.json", "Consistent plural concept label."),
    term("special angles", "sudut istimewa", "m49395;m49398", "qa/agent_a/terminology_proposals.json; m49398 slot 102", "Established Indonesian school-mathematics term.", variants="sudut khusus", register="pedagogical formal"),
    term("guy-wire", "kawat penyangga", "m49395", "qa/agent_a/terminology_proposals.json", "Describes the structural support cable rather than a literal person.", variants="kawat penahan", register="technical"),
    term("inverse trigonometric function", "fungsi trigonometri invers", "m49390", "qa/agent_b/terminology_proposals.csv", "Invers distinguishes a functional inverse from a reciprocal."),
    term("inverse sine", "sinus invers", "m49390;m49398", "qa/agent_b/terminology_proposals.csv; m49398 calculator-solving prose", "Stable concise name for the restricted-domain inverse function."),
    term("inverse cosine", "kosinus invers", "m49390;m49398", "qa/agent_b/terminology_proposals.csv; m49398 calculator-solving prose", "Stable concise name for the restricted-domain inverse function."),
    term("inverse tangent", "tangen invers", "m49390;m49398", "qa/agent_b/terminology_proposals.csv; m49398 calculator-solving prose", "Stable concise name for the restricted-domain inverse function."),
    term("arcsine", "arkus sinus", "m49390", "qa/agent_b/terminology_proposals.csv", "Alternate arc-function name, kept distinct from reciprocal terminology.", variants="arcsin"),
    term("arccosine", "arkus kosinus", "m49390", "qa/agent_b/terminology_proposals.csv", "Alternate arc-function name, kept distinct from reciprocal terminology.", variants="arccos"),
    term("arctangent", "arkus tangen", "m49390", "qa/agent_b/terminology_proposals.csv", "Alternate arc-function name, kept distinct from reciprocal terminology.", variants="arctan"),
    term("reciprocal", "resiprokal", "m49389;m49393;m49396", "qa/agent_b/terminology_proposals.csv; qa/agent_c/terminology_proposals.json", "Prevents collision with functional inverse terminology.", variants="kebalikan"),
    term("reciprocal identities", "identitas resiprokal", "m49389;m49393;m49396;m49397", "qa/agent_b/terminology_proposals.csv; qa/agent_c/terminology_proposals.json", "Names identities based on multiplicative reciprocals, not inverse functions."),
    term("stretch factor", "faktor peregangan", "m49389;m49390", "qa/agent_b/terminology_proposals.csv", "Matches established transformation terminology."),
    term("compression factor", "faktor pemampatan", "m49389;m49390", "qa/agent_b/terminology_proposals.csv", "Natural counterpart to faktor peregangan."),
    term("even-odd identities", "identitas genap-ganjil", "m49393", "qa/agent_c/terminology_proposals.json", "Concise label for the parity identities."),
    term("quotient identities", "identitas hasil bagi", "m49393", "qa/agent_c/terminology_proposals.json", "Names the identities expressing tangent and cotangent as quotients."),
    term("double-angle formulas", "rumus sudut ganda", "m49396;m49397", "qa/agent_c/terminology_proposals.json; m49396 recurring reader text", "Consistent natural label across titles, formulas, and proofs.", variants="rumus sudut rangkap"),
    term("power-reducing formulas", "rumus penurunan pangkat", "m49396", "qa/agent_c/terminology_proposals.json; m49396 slots 107-139", "States that even powers of sine or cosine are reduced and avoids ambiguity with angle reduction.", variants="rumus reduksi|rumus pengurangan pangkat"),
    term("half-angle formulas", "rumus setengah sudut", "m49396", "qa/agent_c/terminology_proposals.json; m49396 slots 142-152", "Direct and established description of the formulas."),
    term("product-to-sum formulas", "rumus hasil kali menjadi jumlah", "m49397", "qa/agent_c/terminology_proposals.json", "Preserves the direction of the identity transformation."),
    term("sum-to-product formulas", "rumus jumlah menjadi hasil kali", "m49397", "qa/agent_c/terminology_proposals.json", "Preserves the direction of the identity transformation."),
    term("right triangle", "segitiga siku-siku", "m49393;m49396;m49398;m49399", "qa/agent_c/terminology_proposals.json; m49398 slots 10, 285-318; m49399 slot 712", "Standard Indonesian geometry term.", rejected="segitiga persegi panjang"),
    term("right angle", "sudut siku-siku", "m49396;m49398;m49399", "qa/agent_c/terminology_proposals.json; m49398 accessibility descriptions", "Standard Indonesian geometry term.", rejected="sudut lurus"),
    term("trigonometric equation", "persamaan trigonometri", "m49392;m49398;m49399", "m49398 slots 1-27 and recurring section prose", "Standard equation-solving term."),
    term("solve a trigonometric equation", "menyelesaikan persamaan trigonometri", "m49398;m49399", "m49398 title, objectives, and section titles; m49399 slot 721", "Use the active verbal construction for instructional headings and objectives."),
    term("multiple-angle trigonometric equation", "persamaan trigonometri sudut kelipatan", "m49398", "m49398 slots 9, 233-283, and 349", "Multiple angle means an integer multiple of an angle, not merely several unrelated angles.", rejected="persamaan dengan berbagai sudut"),
    term("reference angle", "sudut acuan", "m49398", "m49398 slot 131 and calculator-solving context", "Standard pedagogical label for the acute associated angle.", variants="sudut referensi"),
    term("angle of elevation", "sudut elevasi", "m49398", "m49398 slots 15, 292, 297, 299, 400, and 401", "Established surveying and trigonometry terminology."),
    term("angle of depression", "sudut depresi", "m49398", "m49398 slots 15 and 397", "Established surveying and trigonometry terminology."),
    term("unit circle", "lingkaran satuan", "m49398", "m49398 slots 31, 65, 99, 102, and 283", "Established Indonesian trigonometry terminology.", rejected="lingkaran unit"),
    term("periodic motion", "gerak periodik", "m49399", "m49399 slots 276, 326, 484, and 491", "Standard physics terminology for repeating motion."),
    term("harmonic motion", "gerak harmonik", "m49399", "m49399 slots 275-280 and 489-497", "Standard physics term for motion under a restoring force."),
    term("simple harmonic motion", "gerak harmonik sederhana", "m49399", "m49399 slots 281-288, 474, and 839-840", "Standard Indonesian physics term."),
    term("damped harmonic motion", "gerak harmonik teredam", "m49399", "m49399 slots 325-440, 476, 491, and 837-838", "Standard Indonesian physics term; teredam describes energy loss."),
    term("damping factor", "faktor redaman", "m49399", "m49399 slots 326-343 and recurring model prose", "Standard physics terminology for the energy-dissipating factor."),
    term("damping constant", "konstanta redaman", "m49399", "m49399 slots 357, 376-377, and 437-439", "Names the constant controlling exponential amplitude decay."),
    term("displacement", "simpangan", "m49399", "m49399 slots 284, 288, 294-319, 333-345, and 567-588", "For oscillations, simpangan is the physics quantity measured from equilibrium.", rejected="perpindahan"),
    term("restoring force", "gaya pemulih", "m49399", "m49399 slots 280, 284, and 489", "Standard mechanics term for force directed toward equilibrium."),
    term("equilibrium", "keseimbangan", "m49399", "m49399 slots 284, 326, and spring-system exercises", "Standard physics term for the rest position of the system.", variants="titik keseimbangan"),
    term("bounding curves", "kurva pembatas", "m49399", "m49399 slots 447-463 and 497", "Curves that bound an oscillatory graph above and below."),
    term("bounding function", "fungsi pembatas", "m49399", "m49399 slot 456", "Names the function whose graph supplies a bounding curve.", variants="kurva pembatas"),
    term("oscillation", "osilasi", "m49399", "m49399 harmonic-motion section and glossary", "Standard physics term for repeated motion about equilibrium.", variants="gerak berosilasi"),
    term("frequency", "frekuensi", "m49387;m49389;m49399", "m49399 simple and damped harmonic-motion examples", "Standard wave and oscillation term."),
    term("sinusoidal model", "model sinusoidal", "m49399", "m49399 modeling sections and applications", "Concise label for a model expressed with a sine or cosine function."),
    term("varying amplitude", "amplitudo yang berubah-ubah", "m49399", "m49399 slots 448-450 and 463", "Describes amplitude that rises and falls within a period.", variants="amplitudo berubah"),
]


def correction(
    module: str,
    slot: int,
    source: str,
    replacement: str,
    disposition: str,
) -> dict[str, str]:
    return {
        "module": module,
        "slot": str(slot),
        "source": source,
        "correction": replacement,
        "disposition": disposition,
        "confidence": "high",
    }


PROSE = "correct upstream prose; translate the intended meaning; frozen source bytes remain unchanged"
ALT = "correct upstream accessibility text; translate the intended meaning; frozen source bytes remain unchanged"
REPORT_ALT = "correct upstream accessibility text and during owner integration; current helper target preserves the reported source value"
SUMMARY = "replace the placeholder summary upstream and during owner integration; frozen source bytes remain unchanged"

CORRECTIONS = [
    correction("m49386", 4, "bordering tha Masai Mara", "bordering the Masai Mara", PROSE),
    correction("m49386", 6, "most most prominent", "most prominent", PROSE),
    correction("m49387", 44, "we can plots points", "we can plot points", PROSE),
    correction("m49387", 72, "document=\"m49387\">The Other Trigonometric Functions", "document=\"m49384\">The Other Trigonometric Functions", "correct the collection xref upstream; helper xref bytes remain unchanged"),
    correction("m49387", 418, "compared to it's parent function", "compared to its parent function", ALT),
    correction("m49387", 453, "3sin(*(pi/4)x-pi/4)", "3sin((pi/4)x-pi/4)", ALT),
    correction("m49387", 530, "-3cox(x)+4", "-3cos(x)+4", ALT),
    correction("m49387", 548, "range [-1,-7]", "range [-7,-1]", ALT),
    correction("m49387", 671, "Grpah has amplitude", "Graph has amplitude", ALT),
    correction("m49395", 131, "involves taking quotient", "involves taking the quotient", PROSE),
    correction("m49395", 230, "Three rows, two columns/", "Three rows, two columns.", ALT),
    correction("m49395", 305, "..", "Seven rows and two columns. The table lists the sum and difference formulas for cosine, sine, and tangent, followed by the cofunction identities.", SUMMARY),
    correction("m49395", 383, "They are the different, try ", "They are different; try ", PROSE),
    correction("m49395", 389, "They are the different, try ", "They are different; try ", PROSE),
    correction("m49389", 47, "Th table", "The table", ALT),
    correction("m49389", 61, "Th table", "The table", ALT),
    correction("m49389", 279, "rendered heading: y = cscx", "rendered heading: y = csc x", "add typographic spacing upstream; frozen source bytes remain unchanged"),
    correction("m49389", 441, "draw the cosecant function", "draw the secant function", "correct the mathematical function name upstream; Indonesian target renders the intended secant instruction"),
    correction("m49389", 448, "prarbola", "parabola", ALT),
    correction("m49389", 453, "prarbola", "parabola", ALT),
    correction("m49389", 542, "prarbola", "parabola", ALT),
    correction("m49389", 587, "consine", "cosine", ALT),
    correction("m49389", 587, "Grpah", "Graph", ALT),
    correction("m49389", 786, "and the function is decreasing at each point in its range", "and the function is decreasing on each continuity interval in its domain", "correct the mathematical domain/continuity description upstream; helper target preserves the reported source claim"),
    correction("m49390", 16, "Trig Functinos", "Trig Functions", ALT),
    correction("m49390", 509, "- ", "", "remove the unexplained trailing hyphen upstream; helper target preserves the source punctuation"),
    correction("m49390", 585, "Maximums as -pi and pi", "Maximums at -pi and pi", ALT),
    correction("m49390", 646, "consine", "cosine", ALT),
    correction("m49390", 738, "sinusodial", "sinusoidal", ALT),
    correction("m49393", 18, "the first of these identifies", "the first of these identities", PROSE),
    correction("m49393", 233, "..", "Four rows and two columns. The table lists Pythagorean, even-odd, reciprocal, and quotient identities with their equations.", SUMMARY),
    correction("m49396", 58, "We see that we to need to find", "We see that we need to find", PROSE),
    correction("m49396", 101, "if we had chosen the left side to rewrite", "if we had chosen the right side to rewrite", "correct the internal left/right contradiction upstream; translate the intended reasoning"),
    correction("m49396", 165, "o", "°", "replace the letter o used as a degree mark in source MathML mtext; helper target preserves the reported source token"),
    correction("m49396", 220, "rad34. Rad 34", "sqrt(34). The square root of 34", ALT),
    correction("m49396", 233, "..", "Three rows and two columns. The table lists double-angle, power-reducing, and half-angle formulas with their equations.", SUMMARY),
    correction("m49397", 102, "..", "Two rows and two columns. The table lists product-to-sum and sum-to-product formulas with their equations.", SUMMARY),
    correction("m49397", 70, "Substitute for", "Substitute u for", "complete the missing substitution variable in source MathML mtext; helper target preserves the reported source equation annotation"),
    correction("m49397", 71, " and ", " and v for ", "complete the second missing substitution variable in source MathML mtext; helper target preserves the reported source equation annotation"),
    correction("m49397", 112, "or products sine and cosine", "as products of sines and cosines", PROSE),
    correction("m49397", 145, "It is and identity.", "It is an identity.", PROSE),
    correction("m49398", 16, "such as the finding the dimensions", "such as finding the dimensions", PROSE),
    correction("m49398", 102, "Not all functions can be solved exactly", "Not all equations can be solved exactly", "correct the mathematical object upstream; Indonesian target renders the intended equation meaning"),
    correction("m49398", 294, "23 feet", "23 meters", REPORT_ALT),
    correction("m49399", 50, "shifted it on the x-axis by pi/2", "shifted it on the x-axis by pi/8", REPORT_ALT),
    correction("m49399", 122, "(i/2, 0)", "(pi/2, 0)", REPORT_ALT),
    correction("m49399", 211, "(6 PM, 78 in, (6,8))", "(6 PM, 78 in, (6,78))", REPORT_ALT),
    correction("m49399", 284, "spring, When", "spring. When", PROSE),
    correction("m49399", 459, "bonding function", "bounding function", ALT),
    correction("m49399", 471, "..", "Three rows and two columns. The table lists the standard sinusoidal equation, simple harmonic motion equations, and damped harmonic motion equations.", SUMMARY),
]


def load_slots() -> dict[tuple[str, int], dict[str, object]]:
    slots: dict[tuple[str, int], dict[str, object]] = {}
    for module in MODULE_ORDER:
        path = PACKET / "work" / f"{module}_source_slots.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload["slots"]:
            slots[(module, int(row["slot"]))] = row
    return slots


def load_owner_contract() -> dict[str, dict[str, str]]:
    with (PACKET / "contracts" / "TERMINOLOGY.csv").open(encoding="utf-8-sig", newline="") as handle:
        return {row["source_term"].strip().casefold(): row for row in csv.DictReader(handle)}


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    slots = load_slots()
    owner = load_owner_contract()

    seen_terms: set[str] = set()
    term_rows: list[dict[str, str]] = []
    for index, raw in enumerate(TERMS, start=1):
        key = raw["source_term"].strip().casefold()
        if key in seen_terms:
            raise RuntimeError(f"duplicate normalized terminology concept: {raw['source_term']}")
        seen_terms.add(key)
        contract = owner.get(key)
        if contract:
            match = contract["term_id"]
            if contract["preferred_id"].strip().casefold() == raw["preferred_id"].strip().casefold():
                status = "already_accepted_in_owner_contract"
            else:
                status = "proposal_conflicts_with_owner_contract_owner_decides"
        else:
            match = ""
            status = "proposal_only_owner_decides"
        row = {
            "proposal_id": f"HP-A30-003-TERM-{index:03d}",
            **raw,
            "status": status,
            "owner_contract_match": match,
        }
        term_rows.append({field: row[field] for field in TERM_FIELDS})

    correction_rows: list[dict[str, str]] = []
    seen_corrections: set[tuple[str, str, str, str]] = set()
    special_rendered = {("m49387", 72), ("m49389", 279)}
    for raw in CORRECTIONS:
        module = raw["module"]
        slot = int(raw["slot"])
        source_slot = slots[(module, slot)]
        source_text = str(source_slot["source"])
        if (module, slot) not in special_rendered and raw["source"] not in source_text:
            raise RuntimeError(
                f"correction evidence does not occur in frozen slot {module}:{slot}: {raw['source']!r}"
            )
        key = (module, raw["slot"], raw["source"], raw["correction"])
        if key in seen_corrections:
            raise RuntimeError(f"duplicate correction: {key}")
        seen_corrections.add(key)
        row = {**raw, "locator": str(source_slot["locator"])}
        correction_rows.append({field: row[field] for field in CORRECTION_FIELDS})

    term_csv = PACKET / "terminology_proposals.csv"
    term_json = PACKET / "terminology_proposals.json"
    corr_csv = PACKET / "correction_observations.csv"
    corr_json = PACKET / "correction_observations.json"

    write_csv(term_csv, TERM_FIELDS, term_rows)
    write_json(
        term_json,
        {
            "schema_id": "hp-a30-003-terminology-proposals-v1",
            "packet_id": "HP-A30-003",
            "authority_note": "Proposal-only helper artifact; the owner terminology contract was read but not modified.",
            "source_revision": {
                "repository": "openstax/osbooks-college-algebra-bundle",
                "commit": "789b54099106b071d1d32bfcee454fed72eb4768",
                "tree": "05b39123f698772482c0c33a43fa2d2d4ea562ae",
            },
            "field_order": list(TERM_FIELDS),
            "proposal_count": len(term_rows),
            "records": term_rows,
        },
    )
    write_csv(corr_csv, CORRECTION_FIELDS, correction_rows)
    write_json(
        corr_json,
        {
            "schema_id": "hp-a30-003-source-correction-observations-v1",
            "packet_id": "HP-A30-003",
            "authority_note": "Observations only; frozen source and translated CNXML bytes were not modified by this consolidation.",
            "source_revision": {
                "repository": "openstax/osbooks-college-algebra-bundle",
                "commit": "789b54099106b071d1d32bfcee454fed72eb4768",
                "tree": "05b39123f698772482c0c33a43fa2d2d4ea562ae",
            },
            "field_order": list(CORRECTION_FIELDS),
            "observation_count": len(correction_rows),
            "all_high_confidence": all(row["confidence"] == "high" for row in correction_rows),
            "records": correction_rows,
        },
    )

    result = {
        "terminology_proposals": len(term_rows),
        "correction_observations": len(correction_rows),
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (term_csv, term_json, corr_csv, corr_json)
        },
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
