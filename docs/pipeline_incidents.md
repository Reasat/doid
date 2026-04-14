# DOID Ingest — Unanticipated Events Report

This document records events during the ingest that deviated from the expected workflow, the root cause, and the resolution.

---

## 1. `linkml-runtime` inlining bug — Makefile pins bleeding-edge LinkML

**Phase:** 5–6 (build / validate)  
**Context:** The shared mondo-source-ingest workflow installs `linkml`, `linkml-runtime`, and `linkml-owl` versions that avoid a known issue: string values containing commas in `inlined_as_list` slots (e.g. synonym text) can trigger `ValueError` during YAML normalisation when using stock PyPI `linkml-runtime` (see mondo-source-ingest skill, “Robustness rules”).  
**Resolution:** `make dependencies` installs `linkml-owl==0.5.0` plus `linkml` and `linkml-runtime` from the `linkml/linkml` monorepo `main` branch. CI runs `make dependencies && make all` inside `obolibrary/odkfull:v1.6` before validation and `linkml-owl` dumping.  
**Status:** Documented; keep until upstream fixes land in a stable PyPI release and the Makefile is updated accordingly.

---

_No other incidents recorded for the initial scaffold._
