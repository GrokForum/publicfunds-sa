# CHG-2026-055: Note — offsite MariaDB backup still queued

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner GO for outstanding backlog items, 6 Nov 2026 SAST (message t247u), as reported to the author (PublicFunds) |
| Status | Open PR, not merged. Note only |
| Type | Standard (docs only) |
| Environment | Records only. **No MariaDB build. No offsite copy.** |
| CIs affected | `STATUS.md`, `itil/registers/csi-register.md` (CSI-055), `itil/registers/change-log.md`, this file |
| Linked records | CI-050, CSI-009, RSK-006, CHG-2026-044 |
| Rollback | Close the PR. If merged: `git revert -m 1 <merge commit>` |

## Goal

Record that an offsite MariaDB backup on the domains.co.za host, plus a local `/wd` copy, stay on the queue. The review database needs a POPIA review and encryption before any offsite copy. Do not build MariaDB in this change.

## Change

1. New CSI-055 row (Queued).
2. A short STATUS.md "Queued" note.
3. A change-log row.

## Stays the same

- No database, hosting, DNS, skill or code change.
- Local on-box backups under CHG-2026-044 / CSI-009 continue as they are.

## Testing

- `uv run pytest tests/test_no_owner_quotes.py tests/test_popia_names.py -q`

## Risk

None beyond a stale queue note if priorities change. Update the CSI status when work starts under a new CHG.

## How to revert

`git revert -m 1 <merge commit>`.

## Result

Open for review. Not merged.
