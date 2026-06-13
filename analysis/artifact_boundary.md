# Artifact Boundary

Generated artifacts are external by default; evidence anchors are pinned in the main repository.

Chinese summary:

> 生成物默认外置，证据锚点留在主仓库。

## Responsibility Split

| Layer | Responsibility | Examples |
|---|---|---|
| Main repository | Trustworthiness | harness code, schema contracts, tests, fixtures, stable verdicts, minimal evidence anchors |
| Report layer | History | complete generated candidates, full run reports, raw agent notes, trend summaries, large logs |
| Manifest | Traceability | links between run id, harness commit, schema version, hashes, verdict refs, and external artifact locations |

The main repository should stay small enough for agents to read and verify quickly. The report layer may be large, historical, and append-heavy.

## Keep In Main Repository

Keep artifacts here when a test, contract, regression check, or user-confirmed case depends on them.

| Artifact Type | Keep Because |
|---|---|
| Fixtures directly referenced by tests | CI must run without external artifact access. |
| Minimal reproductions for user-confirmed failure cases | Regression anchors must not disappear with generated history. |
| Schema contract examples | Contract changes need local, reviewable examples. |
| Stable verdicts in `analysis/review_ledger.jsonl` | User judgment is the source of truth for regression eligibility. |
| Current active protocol docs | Agents need local rules before reading historical reports. |
| Minimal demo loop | Smoke tests need a small complete artifact chain. |

## Externalize By Default

Move or generate these outside the main repository once they are not required by local tests or regression anchors.

| Artifact Type | Externalize Because |
|---|---|
| Complete candidates for one-off runs | They are historical outputs, not harness source. |
| Raw long-form agent reviews | Keep concise structured claims locally only when they are evidence anchors. |
| Nonessential trend reports | The report layer can preserve dashboards and weekly summaries. |
| Large logs and token streams | They are expensive for repo navigation and usually reproducible. |
| Regenerable intermediate files | Keep commands and manifests, not every transient output. |

## Traceability Contract

Any external report layer should preserve enough metadata for the main repo to verify what it points to:

Current local report layer:

```text
../novel-reports/
```

Main-repo index:

```text
analysis/artifacts_manifest.json
```

```json
{
  "run_id": "round6_codex_full_loop_20260609",
  "harness_commit": "<git-sha>",
  "schema_version": 1,
  "manifest_path": "analysis/reports/candidates/<run_id>/manifest.json",
  "external_artifact_uri": "<report-layer-uri>",
  "artifact_hashes": {
    "candidate_001.md": "<sha256>",
    "candidate_001.json": "<sha256>",
    "candidate_001_gate.json": "<sha256>"
  },
  "ledger_refs": [
    "analysis/review_ledger.jsonl#entry_id=<entry_id>"
  ]
}
```

The exact storage backend can change later. The contract is the important part: `run_id`, harness commit, schema version, artifact hash, and verdict ref must remain recoverable.

## Migration Rule

Do not bulk-move existing reports only to make the tree look clean.

Move a generated artifact out of the main repo only when:

1. It is not required by CI, fixtures, or schema tests.
2. It is not the minimal evidence anchor for a user-confirmed case.
3. Its replacement manifest entry can point back to the run, commit, hash, and verdict ref.
4. `tools/project_doctor.py` and `tools/cleanup_drift_check.py` still pass.

Until an external report layer exists, current active run evidence may remain local.
