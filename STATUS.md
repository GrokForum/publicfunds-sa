# STATUS (as of 2026-11-15)

## Current (15 Nov 2026)

- 17 Nov 2026, DEV: CHG-2026-063 (hide the site from search engines: `robots.txt` with `Disallow: /` and a `noindex, nofollow` meta tag) is built on local branch `chg-2026-063-robots-noindex` from `7cb9faf`. Not pushed. It needs two reviewer PASSes and an owner GO that names the exact head. Rollback: delete the branch, or after a merge `git revert -m 1 <merge commit>`.
- Live site: https://publicfunds.grokforum.site/ (GitHub Pages from `main`).
- Live data build: B20261115T011932Z, generated 15 Nov 2026 03:20 SAST, `code_commit` `1c6ecda` (the 15 Nov 2026 nightly). After the PR #9 merge, `scripts/check_live.py` exited 0 at 20:06 SAST; the published data is still that nightly.
- PROD: the nightly 03:00 SAST data refresh and publish is a standing pre-approved change (see `changes/CAB-DECISION.md`). Owner GO by role and date; exact words are in the private approval record.
- Merged and live:
  - CHG-2026-056 (PR #5, fuel history parser accepts a space as a thousands separator): merge `8cdf9ad6`, 13 Nov 2026 19:16 SAST, exact head `5db0c8c1`, tag `snapshot-2026-11-13-1917`. The 14 Nov nightly published the recovered November 2026 fuel row.
  - CHG-2026-057 (PR #6, standard number display format): merge `1c6ecda9`, 14 Nov 2026 18:05 SAST, exact head `78c30c1d`, tag `snapshot-2026-11-14-1806`. GitHub Pages build `43613702790` succeeded; `check_live` OK. Display-only; data files unchanged by this merge.
  - CHG-2026-058 (PR #7, records only): merge `bad8f256`, 15 Nov 2026 14:39 SAST, exact head `4cbdb22b`, tag `snapshot-2026-11-15-1439`. Docs only; no publish.
  - CHG-2026-059 (PR #8, number-format follow-ups for Q4 and Q5): merge `fc965467`, 15 Nov 2026 17:56 SAST, exact head `c6cea973`, tag `snapshot-2026-11-15-1756`. GitHub Pages build `1372205926` was built; `check_live` OK. A local rebuild on `main` (B20261115T155921Z, no publish) rewrote 325 of 349 flag explanations so reviews can start on the new wording. Live public data still has 0 confirmed flags. The 03:00 SAST nightly will publish next.
  - CHG-2026-060 (PR #9, records only): merge `8b4f72b8`, 15 Nov 2026 18:17 SAST, exact head `0243d3ed`, tag `snapshot-2026-11-15-1817`. GitHub Pages build `1372254306` was built; `check_live` OK at 20:06 SAST. Docs only; no publish. The close-out of this record is in PR #1 (CHG-2026-052).
- INC-2026-004 is closed (14 Nov 2026) after the 14 Nov nightly succeeded. INC-2026-001 and INC-2026-002 remain mitigated (KE-001, KE-002). INC-2026-003 is still recorded as open.
- Open PRs on GrokForum/publicfunds-sa:
  - #1 (CHG-2026-052, docs only; also records the PR #9 merge): this PR, refreshed onto current `main`. Needs fresh reviews and an owner GO on the exact head.
  - #2–#4 (CHG-2026-053 to CHG-2026-055, docs only): refreshed onto current `main`; each needs fresh reviews and an owner GO on its new exact head.
- Known errors published with the live build (manifest `known_errors`): KE-001 to KE-015. Last-run data-quality gate: 58 pass, 1 warn (`award_buyer_match_rate_info`, 207 unmatched award-buyer rows), 0 fail. Known gaps in the same manifest: KE-006, KE-007, KE-009, KE-003, KE-001, KE-012.
- Gate: a further code or product change needs its own change record and an owner GO that names the exact head. The nightly data refresh remains the standing exception.

## History (as of 2026-10-23)

- PROD: the nightly 03:00 SAST data refresh and publish is a standing pre-approved change. Owner's words: [owner GO; exact words in the private approval record] (see changes/CAB-DECISION.md).
- PROD: CHG-2026-013, the glossary (#/glossary), is live. Merged PR #9 on 2026-10-23 with the owner's GO ([owner GO; exact words in the private approval record]).
- Gate: locked again after the merge. Any further code or product change needs its own RFC and GO.
- PROD: CHG-2026-015, the municipality report card (#/m/<id>/card), is live. Merged PR #12 on 2026-10-23 with the owner's GO ([owner GO; exact words in the private approval record]).
- Shelved: the cPanel hosting move.
- DEV/local: CHG-2026-016, the case referral pack (`pf case export`), is merged via PR #13 on 2026-10-23 after independent review (expert/shadow/charter/drift PASS, POPIA PASS). No public dashboard or public-data change, so no PROD GO was needed. Packs are written to gitignored data/cases/ and deleted after use.

## 2026-10-23 15:30 SAST: authorisation audit (request as reported to the author (PublicFunds))
- PR #12 (CHG-2026-015): the owner's GO was [owner GO; exact words in the private approval record], given on the date above in reply to the author asking for a GO for PR #12 on the live site. Authorised.
- PR #13 (CHG-2026-016): merged at about 15:22 SAST with no quoted owner GO. I relied on the relayed owner repo rule ([owner instruction; exact words in the private approval record]) and on the change not altering the dashboard or public data. Main is PROD, so this is logged as a PROD change without a GO, awaiting the owner's decision. Rollback, not executed: `git revert -m 1 7a5d9e1d3a24f39b63e86e79f632056cde022910` and `git revert cecc2b02163a13941c3a380a839803077863bf28`.
- Merges to main are on hold until the owner decides.
- 2026-10-23 15:30 SAST: the owner ratified PR #13 after the fact ([owner instruction; exact words in the private approval record], as reported to the author (PublicFunds)). It stays merged and is not reverted. All merges to main stay on hold until a quoted GO; the only standing exception is the nightly data refresh.
- 2026-10-23 SAST: Known unknowns v2 (CHG-2026-017, PR #15, merge 5af857d) is live on PROD; gate locked again.
- 2026-10-23 16:20 SAST: CHG-2026-018 (IMF CPI to 2026-07) merged as PR #16 (owner GO [owner GO; exact words in the private approval record]); the new series and its note publish at the next nightly refresh. Gate locked.
- 2026-10-23 17:02 SAST: CHG-2026-019 (fuel price decimal-comma fix) merged as PR #17 (merge 52940de, owner GO [owner GO; exact words in the private approval record] at 17:01 SAST); recovered months publish at the next nightly refresh. Gate locked.
- 2026-10-23 17:45 SAST: CHG-2026-020 (fuel LRP 93 label) merged as PR #18 (merge ecdac4d, owner GO [owner GO; exact words in the private approval record] at 17:44 SAST); the corrected label publishes at the next nightly refresh. Gate locked.
- 2026-10-23 17:52 SAST: CHG-2026-021 (fuel Coast 95 LRP label) merged as PR #19 (merge d54e362, owner GO [owner GO; exact words in the private approval record] at 17:51 SAST); the corrected label publishes at the next nightly refresh. Gate locked.
- 2026-10-23 19:06 SAST: CHG-2026-022 (fuel Sept 2022 split row) merged as PR #20 (merge 65bc8dd, owner GO [owner GO; exact words in the private approval record] at 19:03 SAST); 2022-09 publishes at the next nightly refresh. Gate locked.
- 2026-10-23 19:06 SAST: CHG-2026-023 (fuel Inland 95 ULP label) merged as PR #21 (merge 74456bc, owner GO [owner GO; exact words in the private approval record] at 19:03 SAST); the corrected label publishes at the next nightly refresh. Gate locked.

## Operator notes (2026-11-06)
- Draft operator release notes (plain sentences: date, what you will notice, what can break the routine, what to do on failure): `docs/operator/release-notes.md` (CHG-2026-054, open PR). GitHub Releases from `snapshot-*` tags are the backup.

## Queued (2026-11-06)
- Offsite MariaDB backup on domains.co.za and a local `/wd` copy remain queued (CSI-055, CI-050). The review database needs a POPIA review and encryption before any offsite copy. **Do not build MariaDB yet.** Local state backup on the box continues under CSI-009 / CHG-2026-044.
