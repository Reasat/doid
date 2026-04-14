# DOID Ingest — Release Notes

**DOID release (from source `owl:versionInfo`):** 2026-03-31  
**Build date:** 2026-04-14 (local verification build)

---

## Ontology statistics

| Metric | Count |
|---|---|
| Total terms | 14,590 |
| Active terms | 12,079 |
| Deprecated terms | 2,511 |
| Active terms with definition (`obo:IAO_0000115`) | 1,606 (13%) |
| Active terms with exact synonyms | 7,030 (58%) |
| Active root terms (no `parents`) | 1 |
| Descendants of `DOID:4` (disease), final OWL | 12,078 |

---

## Phase 9 verification

Automated checks (see `scripts/verify.py`):

| Check | Result |
|---|---|
| `title` and `version` present and non-empty | PASS |
| No duplicate term IDs | PASS (14,590 unique) |
| Non-empty `label` on every term | PASS |
| Every `parents` entry resolves to a term ID in the file | PASS (0 broken refs) |
| `linkml-validate` — target class `OntologyDocument` | PASS (no issues) |

Commands used for this release:

```bash
./odk.sh make MIR=false build
# After build, from repo root (same Python env as `make dependencies` in Docker):
python scripts/verify.py --yaml doid.yaml --expected-version "2026-03-31"
# Local venv outside Docker:
# uv run python scripts/verify.py --yaml doid.yaml --expected-version "2026-03-31"
```

Optional upstream version pin:

- `verify.py --expected-version` must match the `version` field emitted in `doid.yaml` (from `owl:versionInfo` on the ontology header).

Manual / spot checks:

| Check | Result |
|---|---|
| Final `doid.owl` (LinkML-derived) loads with ROBOT | PASS (`robot convert` in `odkfull:v1.6`) |
| `robot diff` vs mondo-ingest reference | N/A (not a migration) |
| `tmp/transformed-doid.owl` sanity | Built during `make build` (gitignored intermediate) |
