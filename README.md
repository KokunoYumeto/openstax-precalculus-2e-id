# HP-A30-003 — OpenStax Precalculus 2e, Bab 6–7, Bahasa Indonesia

This is a helper-only, integration-ready packet for the complete assigned Chapter 6–7 range of *OpenStax Precalculus 2e*. It does not modify or replace the canonical A30 edition. The canonical owner remains the sole integrator and publisher.

## Exact scope

- Source repository: `openstax/osbooks-college-algebra-bundle`
- Commit: `789b54099106b071d1d32bfcee454fed72eb4768`
- Tree: `05b39123f698772482c0c33a43fa2d2d4ea562ae`
- Contiguous source-order boundary: **38–48**
- Assigned modules, in order: `m49386`, `m49387`, `m49389`, `m49390`, `m49392`, `m49393`, `m49395`, `m49396`, `m49397`, `m49398`, `m49399`
- Coverage: **5,118 of 5,118 reader-facing slots**
- Excluded: every module outside the explicit assignment, including the known preceding module `m49384`

## Reader-first entry point

Open `preview/HP-A30-003_Bab_6-7_Bahasa_Indonesia.pdf` first. The HTML source beside it is the deterministic reflow input. The reader contains the complete assigned translation, all referenced figures, equations, examples, exercises, and solutions, followed by source, license, and process provenance.

## Packet contents

- `translated/modules/`: complete Indonesian CNXML for all 11 assigned modules
- `translated/media/`: all 196 active assets, byte-identical to the frozen source copies
- `source/`: exact frozen assigned CNXML and active source assets
- `contracts/`: exact read-only terminology and backend contracts; no owner contract was edited
- `backend/records.jsonl` and `backend/records.csv`: equivalent modular-backend exports using all 28 required fields; every CSV cell is canonical JSON
- `backend/BACKEND_MANIFEST.json`: schema, entity-count, export-hash, round-trip, and repeat-build receipt
- `terminology_proposals.csv` / `.json`: deduplicated, proposal-only id-ID terminology for owner consideration
- `correction_observations.csv` / `.json` and `issues.csv`: high-confidence source issues and their exact nonblocking disposition
- `closure_manifest.json`: exact source, contract, dependency, translation, QA, and asset closure
- `qa/`: module, packet, independent semantic, terminology-reference, reader, and final preseal QA evidence
- `HANDOFF.json` and `checksums.sha256`: sealed owner handoff and complete file identities

## Translation and QA result

Every reader-facing text, tail, MathML `mtext`, image `alt`, and table `summary` slot in the assigned range was translated into natural id-ID. XML topology, protected attributes, IDs, comments, cross-references, non-`mtext` MathML, formulas, numeric facts, examples, exercises, solutions, citations, and source/component credits are preserved. Deliberate Indonesian decimal and clock localization is explicitly enumerated in module QA.

Independent semantic review covered all 11 modules after initial translation. Every exact repair identified by those audits was propagated through its declared overlay and rebuilt CNXML before final aggregate QA. Source-authored discrepancies were not silently rewritten: they are retained or rendered by intended meaning according to the recorded disposition in `correction_observations.json` and `issues.csv`.

The terminology comparison first searched arXiv for a suitable Indonesian-language source with downloadable TeX. None was identified in the bounded search, so the recorded fallback directly inspected the 2024 Indonesian Ministry of Education Chapter 3 trigonometry summary. The comparison and decisions are in `qa/terminology_reference_decision.json`.

## Canonical packet overlays

| Module | Overlay |
|---|---|
| m49386 | `tools/agent_a_overlays/m49386.json` |
| m49387 | `tools/agent_a_overlays/m49387.json` |
| m49389 | `tools/agent_b_m49389_translations.json` |
| m49390 | `tools/agent_b_m49390_translations.json` |
| m49392 | `tools/agent_b_m49392_translations.json` |
| m49393 | `tools/agent_c_m49393_final.json` |
| m49395 | `tools/agent_a_overlays/m49395.json` |
| m49396 | `tools/agent_c_m49396_final.json` |
| m49397 | `tools/agent_c_m49397_final.json` |
| m49398 | `work/m49398_translation_overlay.json` |
| m49399 | `work/m49399_translation_overlay.json` |

Other draft or historical work files are evidence only; the paths above are the sole overlays bound by current-byte aggregate QA and the backend export.

## Deterministic rebuild and verification

Run from this packet root, in this order:

```text
python tools/aggregate_qa.py
python tools/build_reader.py
python tools/qa_reader.py
python tools/build_issues.py
python tools/build_backend.py
python tools/build_closure_manifest.py
python tools/seal_packet.py
python tools/verify_packet.py
```

The seal must be regenerated after any intentional byte change. `tools/verify_packet.py` is read-only and requires the handoff, every listed output identity, all checksums, the backend JSONL/CSV round-trip, independent review bindings, reader identities, and scope boundary to agree.

## License and attribution

The exact license and attribution are in `LICENSE.md`: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). Figure and asset captions retain their component-specific credits and notices.

Translation and localization assistance: **OpenAI Codex gpt-5.6-sol, Ultra**. This is a process disclosure, not an authorship claim. All source, author, and human-contributor credits remain intact.

Signed by **Codex on instructions of the user**.
