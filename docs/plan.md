# DOID — Mondo source ingest plan

This document is the canonical reference for the DOID preprocessing pipeline: upstream source, versioning, identifier scheme, ROBOT preprocessing, and YAML field mappings.

## Upstream source

- **Publisher:** Human Disease Ontology ([Disease Ontology](https://disease-ontology.org/)), released via the OBO Foundry.
- **Format:** OWL (`http://purl.obolibrary.org/obo/doid.owl`).
- **Authentication:** None for the public PURL.

## Versioning

- The OBO PURL resolves to the current release build. The emitted YAML **`version`** field comes from `owl:versionInfo` on the ontology header after ROBOT preprocessing (`scripts/transform.py` → `extract_ontology_document`).
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

## CI and release

- **Docker:** `obolibrary/odkfull:v1.6` — `make dependencies && make all`.
- **Triggers:** See `.github/workflows/release.yml` — `workflow_dispatch`, weekly cron, push to `main` on pipeline paths.
- **Assets:** `doid.yaml`, `doid.owl` attached to GitHub Releases.

## Schema maintenance

- **`SCHEMA_URL` in `Makefile`:** Placeholder until a shared schema URL is published; the working schema is **`linkml/mondo_source_schema.yaml`** in this repository.

## Related docs

| File | Purpose |
|------|---------|
| [`docs/release_notes.md`](release_notes.md) | Stats and verification summary per release |
| [`docs/pipeline_incidents.md`](pipeline_incidents.md) | Incidents, root causes, resolutions |
