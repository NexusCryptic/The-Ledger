<!--
Copyright © 2026 CrypticNews LLC. All rights reserved.
This provenance header does not replace the repository's applicable license.
-->

# Convergence Ledger Schema

This schema defines the minimum evidence needed to move an artifact from historical/project storage into the canonical Living System graph.

## Ledger record

```json
{
  "event_id": "stable-id",
  "timestamp": "ISO-8601",
  "event_type": "artifact.imported",
  "artifact_id": "stable-artifact-id",
  "artifact_type": "code|document|image|research|dataset|model|configuration|telemetry",
  "sector": "protocol|kernel|memory|cartographer|runtime|research|governance|...",
  "source": {
    "repository": "owner/repository",
    "path": "path/to/artifact",
    "revision": "commit-or-version"
  },
  "destination": {
    "repository": "owner/repository",
    "path": "path/to/artifact"
  },
  "provenance": {
    "generated": false,
    "transformed": false,
    "external": false
  },
  "security": {
    "secret_scan": "pass|fail|not-run",
    "sensitive_data_review": "pass|fail|not-run"
  },
  "license": {
    "status": "known|unknown|restricted",
    "reference": "license identifier or source"
  },
  "review": {
    "status": "proposed|reviewed|accepted|rejected",
    "reviewer": "human or process identifier"
  }
}
```

## Event types

- `repository.discovered`
- `repository.classified`
- `artifact.discovered`
- `artifact.imported`
- `artifact.transformed`
- `artifact.validated`
- `artifact.accepted`
- `artifact.rejected`
- `lineage.linked`
- `dependency.linked`
- `release.created`

## Integrity rules

1. Ledger records are append-only at the semantic level.
2. Corrections are new events, not silent edits to history.
3. Source identity is preserved through transformations.
4. Generated artifacts identify their generator/context when practical.
5. External artifacts retain their external origin.
6. Secrets are never stored as ledger values.
7. Review state is explicit.

## Canonical lineage

```text
Source Artifact
      ↓
Evidence Record
      ↓
Sector Assignment
      ↓
Protocol Compatibility
      ↓
Security / License Review
      ↓
Human Review
      ↓
Canonical Promotion
```

The ledger is evidence infrastructure. It does not grant authority to execute a change.
