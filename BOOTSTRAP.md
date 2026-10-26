# Local bootstrap record | v0.3 | 2026-10-26

**Status reported by the owner:** the standalone local `enterprise-security-mirror` directory and its Git repository were initialized on Ubuntu. The tracked contents of the original Lab 12 were imported via `git archive` without changing the source repository.

- Source repository: https://github.com/seezelop/network-security-labs
- Source subdirectory: `labs/12-enterprise-network-security`
- Source commit: `1635767a152fcd9c20e4a78eef9bb5968cb44d7e`
- Imported destination: `infrastructure/containerlab/`
- SHA recorded in `infrastructure/containerlab/SOURCE_COMMIT.txt`
- The original 18-container topology was running at the time of import.

## Current bootstrap step

Extract the accompanying starter ZIP into `~/Projects/enterprise-security-mirror/` (do not overwrite the existing `infrastructure/` tree). This adds project documentation and the first GitHub Actions workflow.

The workflow checks files, their source commit, JSON policy and script syntax on GitHub. It **does not** deploy Containerlab or run the twelve live network tests.

## Before any new local deployment

The copied topology still says `name: lab12`, uses `clab-lab12-*` names, and has OVS bridge lifecycle scripts that can delete bridges in the original runtime. Do **not** deploy the copy while the original is active. Reconcile naming, resource ownership, bridge isolation and validation tests first.

## GitHub publication

The `enterprise-security-mirror` remote repository has not yet been confirmed created. Create it as a separate repository before pushing `main`. The imported source code and documentation should be reviewed for secrets and machine-specific artifacts before publication.
