# Draft Release Notes — v1.0.0

> Status: draft only. This file prepares the first formal release; it does not mean that the GitHub Release or Zenodo archive has already been created.

## Governance-Aware XAI Cybersecurity Reproducibility Artifact

This release packages the public reproducibility artifact associated with the published article:

**Governance-Aware Explainable AI for Cybersecurity Threat Detection and Risk-Based Response**

Transactions on Computer Science and Applications (TCSA), 3(1), 14–26, 2026.

## Included in the release

- leakage-aware public-sample reproducibility runner;
- deterministic duplicate-control and group-aware split protocol;
- calibrated Random Forest, Gradient Boosting, and Logistic Regression baselines;
- bootstrap confidence intervals;
- three-fold cross-validation sanity check;
- SHAP-based global/local explanation path;
- per-label held-out evaluation;
- immutable reported-run CSV/JSON evidence under `outputs/`;
- exact dataset provenance and SHA-256 checks;
- GitHub Actions reproducibility-integrity preflight;
- validated CPython 3.11 dependency snapshot;
- machine-readable `CITATION.cff`;
- Zenodo-compatible `.zenodo.json`;
- explicit `REPRODUCIBILITY.md` evidence-level guide.

## Scientific interpretation boundary

The artifact reproduces the leakage-aware validation protocol on the cited public CICIDS2017-derived working sample.

It is **not** a claim of:

- a full official CICIDS2017 benchmark;
- operational deployment performance across security environments;
- organization-specific risk calibration;
- generalization beyond the documented public working sample.

Risk-priority examples remain illustrative unless organization-specific asset/context variables are supplied.

## Reported-run preservation rule

The committed `outputs/` directory is treated as immutable reported-run evidence. Fresh executions must write to a different output directory and should be compared against, not overwrite, the committed artifacts.

## Reproducibility preflight

The automated workflow verifies:

- working-sample byte size;
- SHA-256 digest;
- script syntax;
- duplicate-control counts;
- cleaned feature count;
- train/test row counts;
- exact feature-vector train/test overlap = 0;
- expected group-aware split method.

## Release blockers that must be resolved before publication

1. Select and add an explicit repository/software license.
2. Confirm `v1.0.0` as the desired first formal release tag.
3. Confirm the canonical reproducibility workflow is green on the release commit.
4. Create the GitHub Release.
5. Archive the release in Zenodo.
6. Insert the minted Zenodo DOI only after Zenodo actually returns it.

## Suggested release title

`v1.0.0 — Published TCSA reproducibility artifact`
