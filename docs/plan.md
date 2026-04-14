# DOID — Mondo source ingest plan

This document is the canonical reference for the DOID preprocessing pipeline: upstream source, intake answers, versioning, identifier scheme, ROBOT preprocessing, YAML field mappings, and CI/release policy.

## Phase 1 — Intake (recorded)

| Question | Answer |
|---|---|
| **Q1 — Source location** | `http://purl.obolibrary.org/obo/doid.owl` (OBO Foundry PURL for the Human Disease Ontology release). |
| **Q2 — Source format** | OWL (RDF/XML via PURL). |
| **Q3 — Authentication** | None. |
| **Q4 — Versioning** | Release identifier is carried in the ontology as `owl:versionInfo` (e.g. `2026-03-31`). The PURL resolves to the current build; pin with `DOID_URL` or `acquire.py --url` when a specific file is required. |

## Upstream source

- **Publisher:** Human Disease Ontology ([Disease Ontology](https://disease-ontology.org/)), released via the OBO Foundry.
- **Format:** OWL (`http://purl.obolibrary.org/obo/doid.owl`).
- **Authentication:** None for the public PURL.
- **Authority:** Production ingest uses the official OBO PURL only (not unofficial mirrors as the canonical artefact).

## Versioning

- The emitted YAML **`version`** field comes from `owl:versionInfo` on the ontology header after ROBOT preprocessing (`scripts/transform.py` → `extract_ontology_document`).
- **`project.Makefile`** sets `DOID_URL` (default: `http://purl.obolibrary.org/obo/doid.owl`). Override when pinning a specific artifact for reproducibility.
- **`scripts/acquire.py`** downloads the same default URL; use `--url` to pin.

## Identifier scheme (CURIEs)

- **Namespace:** `http://purl.obolibrary.org/obo/DOID_<digits>`
- **CURIE prefix:** `DOID:` (declared in `linkml/mondo_source_schema.yaml`).
- **Example:** `DOID:4` for the `disease` root class.

## Pipeline shape (OWL source)

1. **`make mirror`** — Download raw OWL to `tmp/doid_raw.owl`, merge + `odk:normalize` → `tmp/mirror-doid.owl`.
2. **ROBOT component** (`project.Makefile` → `tmp/transformed-doid.owl`) — remove imports; SPARQL `fix_xref_prefixes.ru`; property allowlist `config/properties.txt`; ontology/version IRI annotation.
3. **`scripts/transform.py`** — rdflib read of `tmp/transformed-doid.owl` → `doid.yaml`.
4. **Validate** — `linkml.validator.cli` against `linkml/mondo_source_schema.yaml`, target class `OntologyDocument`.
5. **`scripts/verify.py`** — Structural checks on `doid.yaml` (duplicate IDs, labels, parent resolution).
6. **`linkml-owl`** — `doid.yaml` → top-level **`doid.owl`** (release OWL artefact).

Intermediate: `tmp/transformed-doid.owl` is ROBOT-only and gitignored. Release artefacts: **`doid.yaml`**, **`doid.owl`**.

### Phase 6 — Validate and iterate

- Tight loop: `./odk.sh make MIR=false build` (skips re-download when mirror inputs exist).
- Proceed to release documentation only when `linkml-validate` exits 0 and `verify.py` exits 0.

### Phase 7 — Derive OWL

- **OWL source:** Per mondo-source-ingest, Phase 7 is **skipped** as a separate step: the released OWL is the **LinkML-derived** top-level `doid.owl`, not the ROBOT intermediate. The ROBOT file is `tmp/transformed-doid.owl` (preprocessing only).

### Phase 8 — CI and release

- **Docker:** `obolibrary/odkfull:v1.6` — `make dependencies && make all`.
- **Release triggers:** `workflow_dispatch`, **weekly** cron (`0 0 * * 1`, Monday 00:00 UTC), and **push to `main`** when pipeline paths change. Rationale: DOID tracks the OBO PURL; a weekly run picks up upstream releases without tying every commit to a release; `workflow_dispatch` allows on-demand builds.
- **Assets:** `doid.yaml`, `doid.owl` attached to GitHub Releases.

### Phase 9 — Verify

- Automated: `scripts/verify.py`; optional `--expected-version` against upstream `owl:versionInfo`.
- Results: recorded in [`docs/release_notes.md`](release_notes.md).

## Field mappings (OWL → YAML)

| Source | Slot / notes |
|--------|----------------|
| `dc:title` or `rdfs:label` on `owl:Ontology` | `title` |
| `owl:versionInfo` | `version` |
| `owl:Class` + DOID numeric IRI | term `id` / `label` |
| `obo:IAO_0000115` | `definition` |
| `oboInOwl:hasExactSynonym` (and related/narrow/broad) | synonym lists as inlined `Synonym` objects |
| `rdfs:subClassOf` to another DOID class | `parents` (external superclass targets omitted) |
| `owl:deprecated` | `deprecated` |
| `oboInOwl:hasDbXref` + `skos:notation` | merged into `skos_exact_match` (no `hasDbXref` in output) |
| `skos:exactMatch` / related / broad / narrow | respective `skos_*_match` slots |

**Not extracted:** OWL class restrictions using object properties (e.g. RO `someValuesFrom`) are not serialised to LinkML slots; only asserted is-a parents between DOID classes are represented.

## QC and reports

- **`make reports`** — `robot measure` (extended JSON) on final `doid.owl`; `sparql/count_classes_by_top_level.sparql` on mirror, transformed, and final OWL (`reports/`). The SPARQL report uses root `DOID:4` (`disease`) as the top-level grouping term.

## Schema maintenance

- **`SCHEMA_URL` in `Makefile`:** Placeholder until a shared schema URL is published; the working schema is **`linkml/mondo_source_schema.yaml`** in this repository.

## Related docs

| File | Purpose |
|------|---------|
| [`docs/release_notes.md`](release_notes.md) | Stats and Phase 9 verification per release |
| [`docs/pipeline_incidents.md`](pipeline_incidents.md) | Incidents, tool workarounds, resolutions |
