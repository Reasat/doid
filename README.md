# doid

Human Disease Ontology (DOID) preprocessed for Mondo disease-ontology ingest.

## Setup

1. Install dependencies: `uv sync`

## Run

```bash
# OWL pipeline (run inside ODK Docker via odk.sh, or locally with ROBOT installed):
./odk.sh make all          # full pipeline: mirror + build + reports
./odk.sh make MIR=false build   # skip re-downloading
```

## Outputs

| File | Description |
|---|---|
| `doid.yaml` | Primary artefact for Mondo ingest |
| `doid.owl` | Final OWL (LinkML-derived; `tmp/transformed-doid.owl` is the ROBOT intermediate) |
| `reports/` | QC metrics and class counts |

## Docs

| Doc | Contents |
|---|---|
| [`docs/plan.md`](docs/plan.md) | Pipeline architecture, field mappings, ID scheme |
| [`docs/release_notes.md`](docs/release_notes.md) | Ontology stats and verification results per release |
| [`docs/pipeline_incidents.md`](docs/pipeline_incidents.md) | Pipeline incidents: errors, deviations, resolutions |
