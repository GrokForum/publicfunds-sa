# CHG-2026-073: Check-only GitHub Actions nightly with the data-quality gate

| Field | Value |
|---|---|
| Requested by / date (SAST) | The orchestrator, 20 Nov 2026 20:21 SAST, as reported to the author (PublicFunds). |
| Status | Built in DEV on branch `ci-nightly-dq-gate` from `main` `b21990a5f1251841efb52619631b44e76d0cef8d` (20 Nov 2026). |
| Type | **Normal-high** (`itil/change-enablement.md`: CI workflow files). |
| Environment | DEV (worktree). Pre-change `main` is `b21990a5f1251841efb52619631b44e76d0cef8d`. The workflow runs on GitHub Actions only after a merge. It does not publish and does not push. |
| CIs affected | CI-121 (new); `scripts/check_live.py`; this record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md`. |
| Linked records | CHG-2026-032 (live-site check), CHG-2026-061 (nightly after-publish wrapper CI-116), CSI-036 |
| Rollback | `git revert -m 1 <merge commit>`. Git is the rollback. |

## What and why

The box nightly at 03:00 SAST already builds, publishes on a green data-quality gate, and can run a live check. There was no check-only GitHub Actions run that repeated the tests, the published-data gate and the live-site check after that publish, without a push or a publish of its own.

This change adds workflow `nightly-dq-gate`. It runs at 04:30 SAST (02:30 UTC) and on `workflow_dispatch`. It checks out the repository with `persist-credentials: false`, installs pinned dependencies with `uv` 0.13.9 and Python 3.13, runs `uv run pytest -q`, runs `scripts/ci_published_dq_gate.py --live`, and runs `scripts/ci_check_live.py`. The job fails when the recorded or live data-quality gate reports a failure, when a published file does not match the manifest, or when the live check reports a BREACH. Workflow permissions are `contents: read`. Actions are pinned by full SHA. The workflow does not use stored credentials, does not push, and does not run `scripts/publish-public-data.sh`. It does not replace the box nightly.

The published-data gate reads `public-data/v1` in the checkout (recorded `build.data_quality.fail` must be 0; listed files must exist and match size and sha256) and, with `--live`, the live manifest at `https://publicfunds.grokforum.site/public-data/v1/manifest.json`. The warehouse DQ SQL suite is not run in Actions, because raw data and the warehouse are not in git. Those checks stay on the box nightly.

## Changes

| File | Change |
|---|---|
| `.github/workflows/nightly-dq-gate.yml` | New check-only workflow. |
| `scripts/ci_published_dq_gate.py` | New published-data gate. |
| `scripts/ci_check_live.py` | Wrapper around `scripts/check_live.py` that fails on a BREACH or a non-zero exit. |
| `tests/test_ci_nightly_dq_gate.py` | Workflow hygiene, gate pass and fail cases, BREACH wrapper, and a check of the committed export. |
| `itil/registers/ci-register.md` | CI-121. |

## Stays the same

- The box 03:00 SAST refresh and publish path is unchanged.
- No Pages deploy, no data push, and no routine text change.

## Testing

- `uv run pytest tests/test_ci_nightly_dq_gate.py -q` (20 Nov 2026): 7 passed.
- `uv run pytest -q` on branch `ci-nightly-dq-gate` at 20 Nov 2026 20:34 SAST: 1,067 passed, 61 skipped.

## Risk

Medium in the change-enablement sense (a new workflow file), low in operation: the job is read-only and cannot publish. A false failure can raise a GitHub Actions alert; it does not stop the box nightly. A missed failure would be a silent Actions skip only if the workflow were disabled. Blast radius: CI on this repository. It does not change which suppliers or people are flagged publicly. POPIA: the scripts print problem types and file names, not personal data.

## How to revert

`git revert -m 1 <merge commit>`.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | | | |
| Second reviewer (high-risk) | | | |

Reviewers: orchestrator and critic, on the exact head. A merge of this change also needs the owner's GO naming that exact head.

## Result

The branch holds the check-only workflow, the two scripts, the tests, and CI-121, with the tests listed above.
