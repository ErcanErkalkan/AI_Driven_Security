# Changelog

All notable changes to the public reproducibility artifact are documented here.

## Unreleased

### Added
- GitHub Actions reproducibility-integrity workflow.
- Explicit `REPRODUCIBILITY.md` evidence-level and rerun guide.
- Draft `v1.0.0` release notes in `RELEASE_NOTES_DRAFT.md`.
- Machine-readable Zenodo deposit metadata in `.zenodo.json`.
- Machine-readable citation metadata in `CITATION.cff`.

### Changed
- Promoted the TCSA reproducibility artifact to the repository's default `main` branch.
- Consolidated reproducibility automation to one canonical workflow: `.github/workflows/reproducibility.yml`.
- Updated README, validation notes, and dataset documentation to reflect the published article rather than a manuscript-stage package.

### Preserved
- Reported-run CSV/JSON artifacts in `outputs/` remain unchanged.
- The public experiment runner remains unchanged from the validated reproducibility implementation.

## Historical branch state

The former `tcsa-governance-aware-xai` branch is retained as a historical safety copy. The current `main` branch contains that history plus publication-metadata and reproducibility-infrastructure updates.
