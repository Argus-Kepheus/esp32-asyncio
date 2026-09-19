# Documentation governance

The documentation is multilingual, but it does not have multiple independent
sources of truth.

## Authority

- **English (EN)** is the canonical language for narrative technical
  documentation.
- **Portuguese (PT-BR)** is a maintained translation.
- Hardware/runtime facts are not owned by either language; their canonical
  sources are `config/hardware.json` and `config/runtime.json`.
- `docs/metadata.json` defines document IDs, semantic section contracts, and
  content revisions.

This avoids a translation becoming a competing technical specification.

## Current languages

| Code | Locale | Role | Status |
|---|---|---|---|
| EN | English | canonical narrative | current |
| PT | Português do Brasil | translation | current |

A future third language (for example ES) should only be added after creating
the same document IDs and semantic section set declared in
`docs/metadata.json`.

## Revision rule

Every document has one shared `content_revision` across languages.

A translation is **current** only when:

1. its file exists;
2. it implements all required semantic sections for that document ID; and
3. its declared revision equals the canonical revision.

The validator checks this contract. Stylistic differences are allowed; missing
normative content is not.

## Semantic sections

Translations do not need identical visible headings. They do need the same
semantic section IDs.

Each document therefore contains markers such as:

```text
<!-- doc-id: technical-specification -->
<!-- language: EN -->
<!-- content-revision: 3 -->
<!-- section: functional-requirements -->
```

These markers are intentionally language-neutral and machine-readable.

## Relationship with generated technical data

Wave 3 establishes semantic/document revision parity. It does **not** yet
generate every Markdown table from `config/`.

Until the documentation-deduplication wave:

- technical facts repeated in prose/tables remain subject to review;
- the validator checks selected high-value canonical facts;
- later waves may replace repeated tables with generated content or links.

## Adding another language

To add a language:

1. register it in `docs/metadata.json`;
2. create every translated document listed in the metadata;
3. use the same document IDs and content revisions;
4. implement the same required semantic section markers;
5. run `python tools/validate_repository.py`;
6. do not mark the language current while any document is stale or incomplete.

The canonical language remains EN unless an explicit repository-wide
governance change is made.


## Document roles

The documentation is intentionally split by responsibility:

| Document | Responsibility |
|---|---|
| root `README.md` | onboarding, quick start, repository navigation |
| `docs/<LANG>/README.md` | concise project overview; hardware inventory is generated |
| `technical-specification.md` | functional behavior, architecture, rationale, acceptance/validation semantics |
| `hardware-reference.md` | human-readable hardware view; canonical tables are generated from `config/hardware.json` |
| `component-specifications.md` | component identity, interface type, software role and component-specific notes; no duplicate wiring table |
| `docs/metadata.json` | multilingual document/revision/section contract |
| `report/` | academic/report snapshot; not an operational source of truth |

Concrete hardware/runtime values should not be introduced manually into a
document merely for convenience. Prefer, in order:

1. a generated block derived from `config/`;
2. a link/reference to an existing generated view; or
3. validation against the canonical configuration when repetition is
   unavoidable for a specific engineering reason.

## Generated documentation blocks

Wave 4 introduces `tools/generate_docs.py`. Generated regions are marked:

```text
<!-- BEGIN GENERATED: block-name -->
...
<!-- END GENERATED: block-name -->
```

Current generated views include:

- EN/PT hardware inventories;
- EN/PT board summaries;
- EN/PT GPIO-to-header maps;
- EN/PT GPIO-constraint tables;
- EN/PT runtime-parameter summaries.

Use:

```text
python tools/generate_docs.py --write
python tools/generate_docs.py --check
```

Do not edit the contents between generated markers manually.


## Diagnostics and tests

| Path | Role |
|---|---|
| `diagnostics/` | ordered manual checks for Wokwi or physical ESP32 hardware |
| `tests/` | reserved for future automated software tests |

Manual diagnostic evidence requires observation of simulator or physical
hardware behavior. It is deliberately kept separate from any future host-side
automated test suite.
