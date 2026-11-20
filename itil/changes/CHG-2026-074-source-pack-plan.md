# CHG-2026-074: Source pack plan for further official sources

| Field | Value |
|---|---|
| Requested by / date (SAST) | The orchestrator, 20 Nov 2026 20:21 SAST, as reported to the author. |
| Status | Built in DEV on branch `docs-source-pack-plan` from `main` `b21990a5f1251841efb52619631b44e76d0cef8d` (20 Nov 2026). |
| Type | Standard (docs only). |
| Environment | Records and planning docs only. No code or data change. No ingest. |
| CIs affected | `docs/roadmap/source-pack-plan-2026-11.md` (new); `docs/roadmap/improvements-2026-10.md` (one pointer); this record; `itil/registers/change-log.md`; `STATUS.md`. |
| Linked records | CSI-026, CSI-029, CSI-030, CSI-035, CSI-037, CSI-039, CSI-046; KE-002, KE-003, KE-006, KE-009, KE-013 |
| Rollback | `git revert -m 1 <merge commit>`. |

## What and why

A source pack dated 20 Nov 2026 listed official public sources that map to items already on the October 2026 improvement backlog. This change records a plan for those sources: licence or terms as stated in the pack, access method, effort, POPIA risk, and a proposed order. It does not ingest new data and does not change a loader.

The first two steps in the proposed order are manual drops the operator can make in a browser: the PPD BAS/LOGIS transaction CSV into the existing `ppd.py` loader (CSI-026, which unlocks CSI-029), and a Census 2022 municipal population table (CSI-037). Later items are SIU and Special Tribunal records at institution level (CSI-035), provincial budgets (CSI-039), AGSA MFMA/PFMA 2024–25 (CSI-030), and major SOE annual reports (CSI-046).

## Changes

| File | Change |
|---|---|
| `docs/roadmap/source-pack-plan-2026-11.md` | New planning document. |
| `docs/roadmap/improvements-2026-10.md` | One "See also" sentence pointing at that document. |

## Stays the same

- No connector, drop, warehouse, or public-data change.
- Four-eyes review and masking rules stay as they are.
- Each later ingest or detector needs its own change record.

## Testing

- `uv run pytest -q` on branch `docs-source-pack-plan` at 20 Nov 2026 20:34 SAST: 1,060 passed, 61 skipped.
- That run includes `tests/test_no_owner_quotes.py` and `tests/test_popia_names.py`.

## Risk

Low. Docs only. Licence and HTTP status notes are as the pack stated on 20 Nov 2026, and are marked as such; they may become stale. A later ingest must confirm the licence and the access path. POPIA: the plan uses role words and tells later work to stay at entity level and to keep named private persons and one-person suppliers out of the public export without review.

## How to revert

`git revert -m 1 <merge commit>`.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | | | |
| Second reviewer | | | |

Reviewers: orchestrator and critic, on the exact head.

## Result

The branch holds the planning document and the pointer from the October 2026 backlog, with the tests listed above.
