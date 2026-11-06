# CHG-2026-054: Draft — easy-to-find operator release notes (docs)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner GO for outstanding backlog items, 6 Nov 2026 SAST (message t247u), as reported to the author (PublicFunds) |
| Status | **RFC + draft page.** Open PR for review. Not merged |
| Type | Standard (docs only) |
| Environment | Records and draft operator docs only. No code or data change |
| CIs affected | `docs/operator/release-notes.md` (new), `itil/changes/CHG-2026-054-operator-release-notes.md`, `itil/registers/change-log.md`, `STATUS.md` (one pointer line) |
| Rollback | Close the PR. If merged: `git revert -m 1 <merge commit>` |

## Goal

Give the operator one easy-to-find page of plain release notes: date, what they will notice, what can break the routine, what to do on failure. Keep GitHub Releases from each `snapshot-*` tag as the backup of the same facts.

## Change (this PR)

1. Add draft `docs/operator/release-notes.md` with a reading guide, a copy template, and two starter entries (DNS restore; GrokForum cutover).
2. Point `STATUS.md` at that file in one short line under a "Operator notes" heading.
3. A change-log row.

## Proposed later (not in this PR)

- After each merge that cuts a `snapshot-*` tag, append one entry to `docs/operator/release-notes.md` and cut a matching GitHub Release body.
- Optionally link the page from the dashboard operator tools area. That UI change needs its own CHG.

## Stays the same

- Public dashboard "What's new" (`#/changes`) for visitors. This page is for the operator, not a second visitor feed.
- No agent or private-person names in the public text. Use role words (operator, author, owner).

## Testing

- `uv run pytest tests/test_no_owner_quotes.py tests/test_popia_names.py -q`
- Manual read: every entry has the four fields; no owner chat quotes; no private-person or agent names.

## Risk

Low. Docs only. Starter entries may lag the full history; they are marked DRAFT.

## How to revert

`git revert -m 1 <merge commit>`.

## Result

Open for review. Not merged.
