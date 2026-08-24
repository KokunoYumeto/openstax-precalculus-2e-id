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

The first 27 of 87 modules are translated contiguously and structurally verified,
from the front matter (`m50919`) through Graphs of Exponential Functions (`m49362`).
One hundred thirteen baked-English or source-defective assets have deterministic
Indonesian SVG derivatives. The modular backend contains 77,811
records and 36 deterministic exports; two consecutive builds were byte-identical.
`m49363` is the next source-order module and remains outside the admitted prefix. No
upstream author has been contacted. The current public checkpoint reader ends at
`m49362`; it is 781 A4 pages and passed two byte-identical builds, complete logical
PDF checks, restoration checks for all 20 root glossaries and 104 definitions,
Poppler visual review, and a 781-page sparse-page screen. It renders 633 admitted
media references and explicit replacement panels for twelve quarantined binaries.

Translation and localization were produced with tool/process assistance on the
user's request. Model identification: OpenAI Codex gpt-5.6-sol, Ultra. This is
a process disclosure, not an authorship credit; Jay Abramson, OpenStax, and the
source's human contributors retain their existing credits.

The recorded field-terminology policy is applied through `m49362`. Its QA inspected two downloaded arXiv source
packages and rejected both because their actual TeX bodies are English. The
edition therefore uses an Indonesian Universitas Jember calculus textbook and
the official 2024 Kemdikbudristek advanced-mathematics textbook as its recorded
fallback witnesses. Their evidence supports `fungsi logaritma`, `fungsi
sesepenggal`, and `perilaku ujung`; the exact identities, hashes, comparison,
and propagation receipt are under `evidence/terminology/m49361/` and
`qa/TERMINOLOGY_QA_20260824.json`.

## Preservation

The current rights-gated reader checkpoint is version
`0.1.0-alpha.27-reader.1`, preserved at <https://doi.org/10.5281/zenodo.22074925>.
It has the 781-page PDF as its primary artifact and
compact resumable CNXML source and modular backend packages alongside it. The
release is explicitly incomplete. Twelve quarantined binaries referenced inside
the translated prefix are omitted and identified by path and hash. All reader
versions remain on Zenodo concept DOI <https://doi.org/10.5281/zenodo.22059757>;
the exact version DOI and anonymous byte-readback are recorded in
`qa/ZENODO_READER_0.1.0-alpha.27-reader.1_20260824T054900+0200.json` and the
public release metadata. The identical seven-file payload is also preserved as
GitHub prerelease
<https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/tag/v0.1.0-alpha.27-reader.1>;
its anonymous byte-readback is recorded in
`qa/GITHUB_READER_0.1.0-alpha.27-reader.1_20260824T055900+0200.json`.

The intended Figshare metadata/link lineage is the requested public project
<https://figshare.com/projects/Open_and_Share-Alike_Educational_Materials_Translations/280296>.
At this checkpoint the former article 33314805 returns HTTP 404, the requested
project has no exact-title replacement, and the collection is empty. The
authenticated Figshare API returns `403 InactiveAccount`; both bounded attempts
stopped before mutation, so no duplicate item or mislicensed release bytes were
created. The evidence is in
`qa/FIGSHARE_METADATA_0.1.0-alpha.27-reader.1_20260824T060200+0200_BLOCKED.json`.
After account reactivation, the prepared publisher will create one file-free CC0
metadata/link item and verify project and collection membership. Zenodo remains
the canonical public file host.

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
