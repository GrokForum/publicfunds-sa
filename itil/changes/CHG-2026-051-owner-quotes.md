# CHG-2026-051: Reword owner chat quotes by role and date

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 1 Nov 2026 20:59 SAST, as reported to the author (PublicFunds) |
| Status | Open PR, not merged. Needs the owner GO, plus a human second reviewer or a 24 h cooling-off |
| Type | Normal-high (POPIA) |
| Depends on | CHG-2026-049, CHG-2026-050 |
| Rollback | `git revert -m 1 <merge commit>` |

## Decision

Public text names an owner decision by role and date only, for example: Owner GO for head 363ae159, 1 Nov 2026 19:41 SAST. Public text does not quote owner chat words. The exact words stay in a private record on the bot computer, outside git (folder 0700, file 0600). Commit messages and merge bodies use the same rule.

## Change

1. 81 word-for-word owner quotes in 29 tracked files are replaced with one of two markers:
   - `[owner GO; exact words in the private approval record]` (62: merge GOs and standing approvals).
   - `[owner instruction; exact words in the private approval record]` (19: other chat text).
   The date and time on each line stay as they were.
2. CHG-2026-050 line 6: the one-letter card answer is now "an answer to a choice card".
3. Three places that showed the author reading of the #36 GO as a quoted GO now say "the GO for #36" without quote marks.
4. CHG-2026-027 line 105 and CHG-2026-029 line 15: the GO wording the author drafted is now a code span, marked as author wording, not owner text.
5. New guard `tests/test_no_owner_quotes.py`:
   - Fails on a double-quoted string that starts with GO or Go (a quoted merge GO).
   - Fails on a double-quoted string whose normalised text has the SHA-256 of a known owner quote. The test keeps hashes only.
6. A change-log row.

Not in scope: author questions to the owner (bot text, not owner words), and the commit messages in the old repo (fixing them needs a history rewrite).

## Testing

- `uv run pytest`: see the PR body for the counts.
- `tests/test_no_owner_quotes.py` (3 tests) and `tests/test_popia_names.py` pass.
- Check after the rewording: no quoted GO marker is left in tracked text.

## Risk

- Records lose the exact words in public. The private record keeps them, with file:line on main f458af9 and the date.
- The guard can false-positive on a new legitimate quote that starts with the word GO. Fix: use a code span or reword.
- Open PRs #1 and #2 hold their own owner decision lines. They are reworded on their branches so the guard passes after this change merges.

## How to revert

`git revert -m 1 <merge commit>`. The private record is not in git and is not changed by a revert.
