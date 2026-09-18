# Reproducibility Guide

This document separates three different evidence levels so that reruns are not confused with the immutable results reported in the published article.

## 1. Immutable reported-run evidence

The `outputs/` directory contains the CSV/JSON artifacts used for cross-checking the published article:

- `model_metrics.csv`
- `confusion_matrices.csv`
- `cv_metrics.csv`
- `feature_importance.csv`
- `local_explanations.csv`
- `per_label_detection.csv`
- `risk_examples.csv`
- `run_metadata.json`
- `train_test_distribution.csv`

These files are retained as reported-run evidence and should not be overwritten by a fresh execution.

## 2. Deterministic preflight

The automated GitHub Actions workflow performs the reproducibility preflight.

It verifies:

1. the cited public working-sample download;
2. exact file byte size;
3. SHA-256 integrity;
4. Python syntax of the public runner;
5. duplicate-control counts;
6. cleaned feature count;
7. group-aware train/test split sizes;
8. zero exact feature-vector overlap between train and test;
9. the expected split method.

Run the same check locally with:

```bash
python -m pip install -r requirements-ci-lock.txt

python scripts/reproduce_protocol.py \
  --input data/CICIDS2017_sample.csv \
  --label Label \
  --output-dir preflight_outputs \
  --preflight-only
```

Expected invariants:

| Check | Expected value |
|---|---:|
| Rows loaded | 56,661 |
| Exact duplicate feature/label rows removed | 12,598 |
| Rows used | 44,063 |
| Raw features | 77 |
| Features after cleaning | 69 |
| Train rows | 33,047 |
| Test rows | 11,016 |
| Exact train-test feature overlap | 0 |
| Split method | `stratified_group_kfold_holdout_4_folds` |

## 3. Fresh full rerun

A fresh model-training run must use a new output directory:

```bash
python scripts/reproduce_protocol.py \
  --input data/CICIDS2017_sample.csv \
  --label Label \
  --output-dir reproduced_outputs \
  --use-shap \
  --cv-folds 3 \
  --bootstrap-iterations 300 \
  --shap-sample-size 1000
```

Do not point a fresh rerun at `outputs/`.

A fresh rerun is new computational evidence. It should be compared against the committed reported-run artifacts rather than silently replacing them.

## Environment levels

### Ordinary local environment

```bash
python -m pip install -r requirements.txt
```

This uses minimum dependency constraints.

### Validated CI environment

```bash
python -m pip install -r requirements-ci-lock.txt
```

This uses the exact dependency snapshot recorded after a successful CPython 3.11 / Ubuntu 24.04 reproducibility-integrity run.

## Dataset provenance

The working sample is not redistributed in this repository.

Source:

https://github.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning/blob/main/data/CICIDS2017_sample.csv

Expected integrity:

```text
File size: 19,868,205 bytes
SHA-256:   03ba3626a0f9bb73b90c56772893e68b0577285130891cd7d811542c17b032dd
Rows:       56,661
```

## Interpretation boundary

The repository reproduces the leakage-aware validation protocol on the cited public CICIDS2017-derived working sample. It is not a claim of a full official CICIDS2017 benchmark.

The public sample does not supply organization-specific asset criticality. Therefore, risk-priority examples are illustrative unless operational asset/context variables are supplied externally.

## Citation and archival metadata

- `CITATION.cff` provides GitHub-compatible citation metadata.
- `.zenodo.json` provides deposit metadata for a future Zenodo archive.
- No software/archive DOI should be inserted until a real Zenodo deposit mints one.
