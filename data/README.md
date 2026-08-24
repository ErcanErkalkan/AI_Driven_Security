# Data for the reported public-sample validation

The manuscript results use the public `CICIDS2017_sample.csv` working sample obtained from Western-OC2-Lab:

https://github.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning/blob/main/data/CICIDS2017_sample.csv

The file is not redistributed in this GitHub branch. Place it here as:

```text
data/CICIDS2017_sample.csv
```

Integrity values for the working file used in the reported run:

```text
File size: 19,868,205 bytes
SHA-256:   03ba3626a0f9bb73b90c56772893e68b0577285130891cd7d811542c17b032dd
Rows:       56,661
```

The experiment removes exact duplicate feature/label rows before splitting and then performs an exact-feature-vector group-aware hold-out split. The reported run removed 12,598 exact duplicate rows, used 44,063 rows, and produced zero exact feature-vector overlap between train and test partitions.

These results are leakage-aware public-sample validation results, not a full official CICIDS2017 benchmark claim.
