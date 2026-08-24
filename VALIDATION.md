# Validation record

## Dataset / split integrity

The exact working CSV was checked against the manuscript protocol. A fresh preprocessing and split preflight produced:

| Check | Value |
|---|---:|
| Rows loaded | 56,661 |
| Raw features | 77 |
| Constant/uninformative features removed | 8 |
| Features after cleaning | 69 |
| Exact duplicate feature/label rows before control | 12,598 |
| Rows after duplicate control | 44,063 |
| Feature-vector duplicate groups after control | 12 |
| Train rows | 33,047 |
| Test rows | 11,016 |
| Exact train-test feature-vector overlap | 0 |
| Split method | stratified_group_kfold_holdout_4_folds |

The eight removed constant/uninformative fields were:
`Bwd_PSH_Flags`, `Bwd_URG_Flags`, `Fwd_Avg_Bytes_per_Bulk`, `Fwd_Avg_Packets_per_Bulk`, `Fwd_Avg_Bulk_Rate`, `Bwd_Avg_Bytes_per_Bulk`, `Bwd_Avg_Packets_per_Bulk`, and `Bwd_Avg_Bulk_Rate`.

## Reported-output cross-check

The committed output artifacts agree with the manuscript values after the manuscript's displayed rounding:

- Random Forest: accuracy 0.992556 → 0.993; balanced accuracy 0.992596 → 0.993; precision 0.995325 → 0.995; recall 0.989984 → 0.990; F1 0.992647 → 0.993.
- ROC-AUC 0.999228 → 0.9992; PR-AUC 0.998961 → 0.9990; Brier 0.005873 → 0.0059.
- F1 bootstrap 95% CI 0.990814–0.994211 → [0.991, 0.994].
- ROC-AUC bootstrap 95% CI 0.998661–0.999638 → [0.9987, 0.9996].
- Confusion matrix: TN=5399, FP=26, FN=56, TP=5535.
- Three-fold CV Random Forest F1: 0.994156 ± 0.000558 → 0.994 ± 0.001.
- Infiltration: 11 held-out examples, 10 detected, rate 0.909091 → 0.909.

## Execution checks

- Python source syntax check: passed.
- Real-data preprocessing/split preflight: passed with the exact counts above.
- End-to-end synthetic-data smoke test of the manuscript working script: passed, including the SHAP path.
- Secret / credential scan of the working source: no API tokens, passwords, private keys, or hard-coded personal filesystem paths detected.

The committed `outputs/` directory is the reported-run evidence package. A new full model-training rerun can be performed with the command in `README.md`; it is intentionally kept separate from the immutable reported outputs.
