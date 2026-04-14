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
| Descendants of `DOID:4` (disease), final OWL | 12,078 |

## Phase 9 verification

- `python scripts/verify.py --yaml doid.yaml` — PASS (14,590 terms, 0 broken parent refs).
- `linkml-validate` — run as part of `make build` (target class `OntologyDocument`); no issues found.
