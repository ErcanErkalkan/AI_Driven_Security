# Release and archival checklist

This repository is prepared as the public reproducibility artifact associated with:

**Governance-Aware Explainable AI for Cybersecurity Threat Detection and Risk-Based Response**

Use this checklist before creating the first formal GitHub release and Zenodo archive.

## Scientific integrity

- [x] Published article metadata added to `README.md`.
- [x] Machine-readable citation metadata added in `CITATION.cff`.
- [x] Reported-run files in `outputs/` preserved without modification.
- [x] Public runner and interpretation boundary documented.
- [x] Dataset source, byte size, row count, and SHA-256 documented.
- [x] Automated dataset/split preflight added in GitHub Actions.
- [x] Validated CPython 3.11 dependency snapshot recorded in `requirements-ci-lock.txt`.
- [x] Zenodo-compatible metadata prepared in `.zenodo.json`.

## Before the first formal release

- [ ] Select and add an explicit software/repository license. Do not infer a license from repository visibility.
- [ ] Confirm the desired semantic release tag (for example, a chosen `vX.Y.Z`).
- [ ] Confirm the current `main` commit is the exact release commit.
- [ ] Confirm the reproducibility-integrity workflow is green on the release commit.
- [ ] Create a GitHub Release from the selected tag.
- [ ] Archive that GitHub Release in Zenodo.
- [ ] Record the DOI returned by Zenodo in `README.md`, `CITATION.cff`, and `.zenodo.json` only after the DOI actually exists.
- [ ] Re-run citation and link checks after DOI insertion.

## DOI rule

No repository/archive DOI should be claimed before Zenodo actually mints one. The published article links currently recorded in this repository are identifiers for the article, not a DOI for this software artifact.

## License rule

Public visibility does not grant an open-source license by itself. A formal license should be added only after the repository owner chooses one.
