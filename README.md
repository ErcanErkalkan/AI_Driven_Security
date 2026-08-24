# Governance-Aware XAI Cybersecurity — Reproducibility Artifact

Public reproducibility artifact for the manuscript:

**Governance-Aware Explainable AI for Cybersecurity Threat Detection and Risk-Based Response**

## Scope

This branch documents and reproduces the leakage-aware public-sample validation reported in the manuscript. It is **not** presented as a full official CICIDS2017 benchmark.

## Contents

- `scripts/reproduce_protocol.py` — public implementation of the reported duplicate-control, group-aware hold-out, calibrated ML, confidence-interval, CV, SHAP and per-label evaluation protocol.
- `requirements.txt` — Python dependencies.
- `data/README.md` — exact working-sample source, expected file name, size and SHA-256 digest. The dataset itself is not redistributed here.
- `outputs/` — the CSV/JSON artifacts from the reported manuscript run, retained for direct cross-checking.
- `VALIDATION.md` — integrity and manuscript-consistency checks.

## Environment

Python 3.11+ is recommended.

```bash
python -m pip install -r requirements.txt
```

## Dataset

Obtain `CICIDS2017_sample.csv` from the Western-OC2-Lab repository and place it at:

```text
data/CICIDS2017_sample.csv
```

Source:
https://github.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning/blob/main/data/CICIDS2017_sample.csv

Expected working-file integrity:

```text
bytes   = 19,868,205
SHA-256 = 03ba3626a0f9bb73b90c56772893e68b0577285130891cd7d811542c17b032dd
rows    = 56,661
```

## Reproduce the reported protocol

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

A fast preprocessing/split integrity check is available without model fitting:

```bash
python scripts/reproduce_protocol.py \
  --input data/CICIDS2017_sample.csv \
  --label Label \
  --output-dir preflight_outputs \
  --preflight-only
```

Expected preflight values:

- loaded rows: **56,661**
- exact duplicate feature/label rows removed: **12,598**
- rows used: **44,063**
- raw flow features: **77**
- predictors after constant/uninformative-column removal: **69**
- train rows: **33,047**
- test rows: **11,016**
- exact train-test feature-vector overlap: **0**

## Reported Random Forest result

The committed `outputs/model_metrics.csv` records:

- accuracy: 0.992556
- balanced accuracy: 0.992596
- precision: 0.995325
- recall: 0.989984
- F1: 0.992647 (reported as 0.993)
- ROC-AUC: 0.999228 (reported as 0.9992)
- PR-AUC: 0.998961 (reported as 0.9990)
- Brier score: 0.005873 (reported as 0.0059)
- confusion matrix: TN=5399, FP=26, FN=56, TP=5535

The original manuscript working script retained in the author package has SHA-256:

```text
c41a0f86247b1563358f78a49c83d96fd2f90fe71f7b97b95e86d453457fade6
```

The public runner in this branch is a cleaned reproducibility implementation of the same reported protocol; the committed `outputs/` files are the artifacts used for manuscript cross-checking.
