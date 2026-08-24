# OpenStax Precalculus 2e — Bahasa Indonesia

This is the separate working lane for an independent Bahasa Indonesia (`id-ID`)
edition of **OpenStax Precalculus 2e**, curriculum resource R002 / course A30.
It does not contain or represent the three earlier OpenStax foundation books or
the other books stored in the upstream bundle repository.

## Exact upstream authority

- Repository: <https://github.com/openstax/osbooks-college-algebra-bundle>
- Branch: `main`
- Commit: `789b54099106b071d1d32bfcee454fed72eb4768`
- Tree: `05b39123f698772482c0c33a43fa2d2d4ea562ae`
- Selected collection: `collections/precalculus-2e.collection.xml`
- Collection UUID: `f021395f-fd63-46cd-ab95-037c6f051730`

The exact archive and API evidence are retained under `authority/`. The selected
closure contains 87 modules and 1,873 explicitly referenced media files; shared
bundle metadata, the trademark-controlled original cover, and all other works
are excluded from the target/publication.

## Current state

The source closure and component-rights inventory are frozen, and an exact copy
of the 1,961 selected files has been materialized under `repo/source/`. The prose
rights gate passes for noncommercial translation under CC BY-NC-SA 4.0. Of the
1,873 media assets, 1,835 are admitted and 38 remain quarantined until replaced,
excluded, or independently cleared.

The first 26 of 87 modules are translated contiguously and structurally verified,
from the front matter (`m50919`) through Exponential Functions (`m49361`).
One hundred-nine baked-English or source-defective assets have deterministic
Indonesian SVG derivatives. The modular backend contains 74,454
records and 36 deterministic exports; two consecutive builds were byte-identical.
`m49362` is the next source-order module and remains outside the admitted prefix. No
upstream author has been contacted. The current public checkpoint reader still
ends at `m49352`; it is 685 A4 pages and passed three byte-identical builds,
logical PDF checks, and independent visual review. It renders 569 admitted media
references and explicit replacement panels for twelve quarantined binaries.

Translation and localization were produced with tool/process assistance on the
user's request. Model identification: OpenAI Codex gpt-5.6-sol, Ultra. This is
a process disclosure, not an authorship credit; Jay Abramson, OpenStax, and the
source's human contributors retain their existing credits.

Field-terminology QA through `m49361` inspected two downloaded arXiv source
packages and rejected both because their actual TeX bodies are English. The
edition therefore uses an Indonesian Universitas Jember calculus textbook and
the official 2024 Kemdikbudristek advanced-mathematics textbook as its recorded
fallback witnesses. Their evidence supports `fungsi logaritma`, `fungsi
sesepenggal`, and `perilaku ujung`; the exact identities, hashes, comparison,
and propagation receipt are under `evidence/terminology/m49361/` and
`qa/TERMINOLOGY_QA_20260824.json`.

## Preservation

The current rights-gated reader checkpoint is version
`0.1.0-alpha.23-reader.1`, preserved at <https://doi.org/10.5281/zenodo.22071329>.
It has the 685-page PDF as its primary artifact and
compact resumable CNXML source and modular backend packages alongside it. The
release is explicitly incomplete. Twelve quarantined binaries referenced inside
the translated prefix are omitted and identified by path and hash. All reader
versions remain on Zenodo concept DOI <https://doi.org/10.5281/zenodo.22059757>;
the exact version DOI and anonymous byte-readback are recorded in
`qa/ZENODO_READER_0.1.0-alpha.23-reader.1_20260823T212500+0200.json` and the
public release metadata. The first bounded attempts encountered transient 504
responses; the recovered retry created this single new version on the existing
concept, with no duplicate concept.

The intended Figshare metadata/link lineage is the requested public project
<https://figshare.com/projects/Open_and_Share-Alike_Educational_Materials_Translations/280296>.
At this checkpoint article 33314805 is still absent from the anonymous
project/article inventory; the alpha.23 retry therefore made no mutation and no
duplicate item or mislicensed release bytes were created. The bounded evidence
is in `qa/FIGSHARE_READER_LINK_0.1.0-alpha.23-reader.1_20260823T214000+0200_BLOCKED.json`.
Retry the same article after Figshare visibility/account restoration. Zenodo
remains the canonical public file host.

The corpus-specific public repository is
<https://github.com/KokunoYumeto/openstax-precalculus-2e-id>. Reader checkpoints
are published as clearly labeled prereleases while contiguous translation
continues.

## Structure

- `00_control/`: durable goal, cursor, authority, decisions, terminology,
  rights, backend version, and later release receipts.
- `authority/`: immutable pinned repository evidence and selected source closure.
- `repo/`: separate editable Indonesian source and reader project.
- `backend/`: locale-neutral entities and deterministic JSON/JSONL/CSV exports.
- `qa/`: structural, semantic, mathematical, language, rights, build, visual,
  and artifact witnesses.
- `scripts/`: bounded deterministic tooling for this corpus only.

This is a noncommercial translation program. The selected collection declares
CC BY-NC-SA 4.0, but every materially distinct component must still be recorded
at the smallest useful rights boundary before publication.
