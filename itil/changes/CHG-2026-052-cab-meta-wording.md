# CHG-2026-052: Soften CAB meta phrasing (docs only)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner GO for outstanding backlog items, 6 Nov 2026 SAST (message t247u), as reported to the author (PublicFunds) |
| Status | Open PR, not merged. Needs second review PASSes on the exact head, then an owner merge GO naming this head |
| Type | Standard (docs only) |
| Environment | Records only. No code, test or data change |
| CIs affected | `changes/CAB-DECISION.md`, `itil/registers/change-log.md`, this file |
| Rollback | Close the PR. If merged: `git revert -m 1 <merge commit>` |

## Goal

Remove leftover meta phrasing in `changes/CAB-DECISION.md` that still says "Owner's words, quoted" / "Owner's GO, quoted", and remove the two author-question strings that sat in double quotes on the 23 Oct 19:03 entries. Public text keeps the private-approval marker and the date. Exact owner words stay in the private approval record only.

## Change

1. Line for PR #15 (23 Oct 15:54): "Owner's words, quoted:" → "Owner's GO recorded by role and date:".
2. Lines for PR #20 and PR #21 (23 Oct 19:03): drop the double-quoted author question; say the GO was in reply to the author's question whether to merge both open PublicFunds PRs to the live site.
3. Lines for 24 Oct 10:39, 11:07 and 16:06: "Owner's GO, quoted (...)" → "Owner's GO (...)".
4. Two later "owner GO, quoted from the owner's chat message" clauses → "recorded by PublicFunds from the owner chat by role and date".
5. A change-log row.

## Stays the same

- Every `[owner GO; exact words in the private approval record]` marker.
- Dates, PR numbers, merge SHAs, reviewer PASS lines, rollback lines.
- No code, tests, skills, public-data or dashboard change.

## Seen, not touched

- Other uses of the words "quoted GO" as a rule phrase (for example the PR #13 audit lines).
- Historical CHG-2026-048 text that still names the old author question as an example of what that change left untouched.
- Stale remote branches from before the history rewrite.

## Testing

- `uv run pytest tests/test_no_owner_quotes.py tests/test_popia_names.py -q`
- `rg` shows no `Owner's words, quoted`, no `Owner's GO, quoted`, and no `question asked: "Merge both` in `changes/CAB-DECISION.md`.

## Risk

Low. Docs only. A reader loses the author-question string in public text; the private approval record still has the owner GO words.

## How to revert

`git revert -m 1 <merge commit>`.

## Result

Open for review. Not merged.
