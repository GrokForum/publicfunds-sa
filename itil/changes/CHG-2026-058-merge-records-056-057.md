# CHG-2026-058: Record the merges of #5 and #6, close INC-2026-004, and note the CHG-2026-057 leftovers (docs only)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Post-merge record update after PR #6, 14 Nov 2026 18:05 SAST, as reported to the author (PublicFunds). |
| Environment | Docs only. Nothing is built, run as a publish, or deployed by this change. |
| Type | Standard (`itil/change-enablement.md`: "Docs/copy"); only markdown under `itil/` changes, same as CHG-2026-042. |
| CIs affected | `itil/registers/change-log.md` (CHG-2026-056 and -057 rows, one new row); `itil/registers/incident-log.md` (INC-2026-004); `itil/changes/CHG-2026-056-fuel-thousands-space.md`; `itil/changes/CHG-2026-057-number-format.md`; `itil/incidents/INC-2026-004.md`; this record |
| Linked records | PRs #5 and #6; CHG-2026-056, CHG-2026-057; INC-2026-004 |
| Rollback | Close the PR unmerged. If merged: `git revert -m 1 <merge commit>` (git is the rollback) |

## Problem

PR #5 (CHG-2026-056) was merged as `8cdf9ad6` on 13 Nov 2026 19:16 SAST (tag `snapshot-2026-11-13-1917`) and PR #6 (CHG-2026-057) as `1c6ecda9` on 14 Nov 2026 18:05 SAST (tag `snapshot-2026-11-14-1806`). The CHG-2026-056 record, the CHG-2026-057 record and its change-log row, and INC-2026-004 still read as open. INC-2026-004 was to stay open until a nightly publish succeeded on its own.

## Change

1. CHG-2026-056 record and change-log row: status set to implemented / closed (merge commit, exact head, date, tag). The 14 Nov 2026 nightly success is recorded.
2. CHG-2026-057 record and change-log row: status set to implemented / closed (merge commit, exact head, date, tag). The post-merge live-format checks are recorded in its Result. Q4 and Q5 are marked as left open for a later change.
3. INC-2026-004: status set to closed, with the merge and the 14 Nov 2026 nightly in the timeline and the Resolution.
4. New change-log row for this change. No new CSI row: docs-only record changes add none.

## Not changed

Code, data, config, `public-data/`, tests, the live site, and `STATUS.md` (that file is stale and is not part of this record update). Q4 and Q5 leftovers are only named, not fixed: `thusa/review/warehouse.py:137` (share display) and `thusa/detectors.py:25` (flag text).

## Testing

`git diff --stat origin/main` shows only markdown under `itil/`. `uv run pytest -q tests/test_popia_names.py tests/test_no_owner_quotes.py` on this branch (result in the PR).

## Risk

Low: wording only. No published output changes. Does not change which suppliers or people are flagged publicly.

## Facts and how they were checked

- PR #6: GitHub state MERGED; `headRefOid` `78c30c1d0821f93bfb6b8526c54b62ba9572e5fc`; merge commit `1c6ecda931463bf2af9723f3da6fa80e5d3360fd`; `mergedAt` 2026-11-14T16:05:37Z (18:05:37 SAST). `git merge-base --is-ancestor` confirms that commit is on `origin/main`. Second parent of the merge is the exact head.
- PR #5: already on main as `8cdf9ad6` (13 Nov 2026 19:16 SAST), exact head `5db0c8c1`, tag `snapshot-2026-11-13-1917`.
- Tag `snapshot-2026-11-14-1806` points at `1c6ecda9` and was pushed after the merge.
- GitHub Pages run `43613702790` (`pages-build-deployment`) concluded success for head `1c6ecda9` at 18:06:07 SAST.
- `scripts/check_live.py` exited 0 at 18:07 SAST; live build B20261114T005655Z, generated 2026-11-14 02:57 SAST.
- Live `apps/public-dashboard/index.html` is byte-identical to the file on `1c6ecda9`, including the formatter block.
- Headless Chromium confirmed table full figures, card short forms, the hover `title` attribute, coverage `75.7%`, and comma thousands on counts. Evidence kept outside git.
- `uv run thusa report` produced the bracketed short form, including `R1.2 m (R1,200,000.00)` from `rand_short(120000000)`.
- **Not verifiable from the repo:** the owner GOs themselves. They are recorded by role and date, as reported to the author (PublicFunds). Exact words stay in the private approval record. A reviewer PASS is not an owner approval.

## popia-review verdict: PASS

Docs-only status wording. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key. No person or supplier is newly named. Role words only; no owner or agent names; no owner chat quotes. The live-format evidence cited in the CHG-2026-057 Result uses official public municipality figures already on the site. Nothing was removed from the diff.

## How to revert

Close the PR unmerged. If merged: `git revert -m 1 <merge commit of this PR>`.

## Result

DEV: docs-only PR open, not merged. No PROD change from this record update.
