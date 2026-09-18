# Changelog

All notable changes to the public reproducibility artifact are documented here.

## Unreleased

### Added
- GitHub Actions reproducibility-integrity workflow.
- Machine-readable Zenodo deposit metadata in `.zenodo.json`.
- Machine-readable citation metadata in `CITATION.cff`.

### Changed
- Promoted the TCSA reproducibility artifact to the repository's default `main` branch.
- Updated README, validation notes, and dataset documentation to reflect the published article rather than a manuscript-stage package.

### Preserved
- Reported-run CSV/JSON artifacts in `outputs/` remain unchanged.
- The public experiment runner remains unchanged from the validated reproducibility implementation.

## Historical branch state

The former `tcsa-governance-aware-xai` branch is retained as a historical safety copy. The current `main` branch contains that history plus publication-metadata and reproducibility-infrastructure updates.
