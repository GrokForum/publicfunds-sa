# CHG-2026-059: Number-format follow-ups (share of top 15, rand amounts in flag text)

| Field | Value |
|---|---|
| Requested by / date (SAST) | The owner, 14 Nov 2026 18:12 SAST, as relayed to the author (PublicFunds). The owner answered Q4 and Q5, which CHG-2026-057 left open: use the conventional standard, the one that is most readable for a wide audience, the same as for the other numbers. This is approval to prepare the RFC and PR only. It is not a merge GO. |
| Status | Open PR, not merged. Needs two independent reviewer PASSes on the exact head, then an owner merge GO that names this head. |
| Type | **Normal-medium**, the same as CHG-2026-057. The change alters display text only. It does not change detector thresholds or logic, which flags are made, `config/publication.yaml`, or the publishing pipeline. It does change the text that the review fingerprint covers (see "Effect on stored flags and reviews"). |
| Environment | DEV only (branch `feat/chg-2026-059-format-followups` from origin/main at `1c6ecda9`). Nothing pushed to main. No publish. |
| CIs affected | `thusa/format.py` (new `format_rand_prose`); `thusa/report.py` (`rand_short` uses it); `thusa/detectors.py` (`_rand`, new `_rand_evidence`, two wording edits); `thusa/review/warehouse.py` (`share_of_top15`, new `share_pct_1dp`); `tests/test_format_followups_059.py` (new); `tests/test_number_format.py` (one guard line); this record; `itil/registers/change-log.md` |
| Linked records | CHG-2026-057 (Q4, Q5) |
| Rollback | Close the PR unmerged. If merged: `git revert -m 1 <merge commit>`. The next build then makes the old text again. Git is the rollback; no .bkp files. |

## Goal

Two places still showed numbers outside the CHG-2026-057 rules. Bring them in line:

1. **Q4.** The review app's "Largest suppliers" table (D4 flags) shows `share_of_top15` from a raw `f"{share:.1%}"` string. Make it come from the shared formatter, with the same style as coverage (42.3%).
2. **Q5.** Flag titles and explanations show rand amounts as whole rands with no cents (`R4,000,000`, `R393,570,966`). Use the report's prose rule: R1 m and over is the short form with the full figure in brackets (`R1.2 m (R1,200,000.00)`); under R1 m is the full figure with cents (`R123,456.78`).

## What changed

1. `thusa/format.py`: new `format_rand_prose(cents)`. It is the bracket rule that CHG-2026-057 put in `report.rand_short`, moved to the shared module so that the report and the detectors use one helper. No new rounding: the short form is the only part that drops digits, as before.
2. `thusa/report.py`: `rand_short` now calls `format_rand_prose`. Output is the same.
3. `thusa/detectors.py`:
   - `_rand` (used only in flag titles and explanations) now returns `format_rand_prose(cents)`. `None` still shows as `unknown`.
   - New `_rand_evidence` keeps the old whole-rand string. `_award_ev` uses it for the `value` field in `evidence_json`, so stored evidence does not change.
   - D17: the lower band edge is `round(t * (1 - band))` cents, so a float product cannot show sub-cent digits. With the current config the values are exact (R270,000.00, R675,000.00, R180,000.00, R900,000.00); no figure changes.
   - D4 and D16: "with a known value (R… in total)" now reads "with a known total value of R…". Without this, the new bracket would sit inside another bracket: `(R393.6 m (R393,570,966.00))`. The meaning is the same.
4. `thusa/review/warehouse.py`: new `share_pct_1dp(part, total)` does the calculation to one decimal (the existing precision rule), and `format_pct_points(…, 1)` shows it. The digits are the same as the old string; a test proves this for every part/total pair up to 400 and for large values.
5. Tests: `tests/test_format_followups_059.py` (new, see Testing). In `tests/test_number_format.py`, one guard line now checks that `report.py` uses `format_rand_prose` once and `format_rand_short` zero times, because the helper moved. The intent of the guard ("only through the bracketed helper") is the same.

## Effect on stored flags and reviews (the owner asked for a plain answer)

**Short answer: after a merge, the next build rewrites the text of existing flags, not only new ones. No review is invalidated today, because no review decision exists. No public-data file changes today.**

Evidence (checked 14 Nov 2026, about 18:15 SAST, on a copy of the current warehouse, build B20261114T005655Z):

- **Where flag text is stored.** Titles and explanations are made at build time and written to `marts.flag` in the warehouse. `detectors.build` runs `CREATE OR REPLACE TABLE marts.flag` on each build. There is no other copy of the text that survives a rebuild. So "existing" flags get the new text at the next build. Nothing is migrated in place.
- **How many flags.** Running the new detectors on the copy: 349 flags before and after, with the same 349 flag IDs. 325 explanations change (all D1, D3, D4, D8 and D16 flags). 0 titles change (the only titles with rand amounts are D6 and D17, and the current build has 0 of those). The 24 D5 flags do not change (their text has fixed words such as "below R100", not computed amounts). `flag_id`, `score`, `severity`, `detector_version` and `evidence_json` are the same for all 349.
- **Review fingerprint.** `workflow.evidence_hash` covers `title` and `explanation` (ADR-0008). So the 325 changed flags get a new evidence hash. If a flag had a review decision, the review app would show it as "evidence changed", and a confirmed flag would stop being publishable until it is confirmed again. Stored decisions are append-only and are never rewritten; their `flag_snapshot` keeps the old title.
- **Reviews today.** The live review store `data/review/review.sqlite` has **0 decisions**. The 13 daily backups in the backup folder (1 Nov to 14 Nov 2026) also have 0 decisions. So no review is invalidated now.
- **Public data.** `public-data/v1/flags.json` exports `title` and `explanation` only for review-confirmed flags. Today it has 0 confirmed flags and counts 349 hidden leads. The hidden-lead counts do not change. D6, D16 and D17 are `never_publish`. So no public-data file changes now. Later, a confirmed flag's `explanation` string in `flags.json` will use the new prose format. That is a text field. No numeric field changes, so the plain-data rule (CSV, JSON and DB numbers stay plain decimals) is kept.
- **evidence_guard.** The publish guard compares coverage counts, not flag text. It is not affected.
- **Review CSV export.** `EXPORT_COLS` has `title` but no `explanation` and no rand column. It gets new titles only for D6 and D17 flags (0 today).

### Design choice: format when the flag is made, not when it is shown

Option A (chosen): make the new text in the detectors. Option B: keep the old stored text and change the amounts only when the text is shown.

B was rejected because:
- The old text has whole rands only. The cents are not in the text, so a display-time rewrite cannot show "R123,456.78". It would have to show a rounded figure, which is against the owner's no-rounding rule.
- B needs a text rewrite (a regular expression on free text) on five surfaces: the review app, case packs, the internal report, the public snapshot, and the public dashboard (which reads `flags.json`). It also cannot reliably tell a computed amount from fixed wording such as "R10 placeholders" or "R20bn". That is fragile and harder to review.

A is the smaller and safer change. Its one cost is the new evidence hash on rebuild. That cost is zero now, because there are no review decisions.

**Owner item (real trade-off):** merge this change before the first review decision is recorded. If reviews start before the merge, each reviewed flag with a rand amount will show "evidence changed" after the next build and will need a new review. A confirmed flag would leave `flags.json` until it is confirmed again.

## Stays the same

- All CSV, JSON and DB numeric fields. `evidence_json` is byte-for-byte the same.
- Detector thresholds, logic, versions and `config/detectors.yaml`. Flag IDs, scores and severities.
- Percent and ratio wording in flag titles (`998%`, `89%`, `HHI 8,007`), D13 per-litre prices, and D5 fixed wording.
- `format_rand_short` and every other CHG-2026-057 helper. The public dashboard code.

## Seen, not touched

- `evidence_json` award `value` strings still show whole rands (`R4,000,000`). This is stored evidence. Changing it would also change the evidence hash. A later change could store the cents number and format it at display time. Owner item if wanted.
- `detector_version` was not bumped for the text change. A bump would change `config/detectors.yaml` (Normal-high) and the evidence hash again; the text change already changes the hash.
- D13 explanations show per-litre prices with `:,.2f`, which rounds the implied price. D1, D4 and D8 titles show ratios with `:.0%`. These are percent and price rules, not rand amounts, and are not in Q4 or Q5.

## Testing (evidence, not claims)

- New tests in `tests/test_format_followups_059.py`:
  - prose rule: 999,999.99 vs 1,000,000.00, R1.2 m, R2.03 bn, negatives, zero, -0.0 and None, for `detectors._rand`, `format_rand_prose` and `report.rand_short`;
  - `_rand_evidence` gives the old string;
  - D17 (under R1 m: `R300,000.00`, `R270,000.00`), D16 and D6 (R1 m and over, with brackets) on a small test warehouse; the evidence `value` strings are unchanged;
  - flag ID, score, severity, evidence and detector version do not depend on the text, and the evidence hash does (documents the review effect);
  - `share_of_top15`: same digits as the old string for every part/total pair up to 400 and for large values; 42.3%, 50.0%, 100.0%, 0.0%; no raw `:.1%` string left;
  - the public-data and review-export field lists are unchanged.
- Full suite on this branch (14 Nov 2026, about 18:25 SAST): `.venv/bin/python -m pytest -q` → **925 passed, 1 skipped** (main before this change: 907 passed, 1 skipped; 18 new tests). The skip is the same real-file fuel test as before.
- Warehouse-copy run (no publish): 349 flags, 325 new explanations, 0 new titles, 0 changes to IDs, scores or evidence (see above).

## Risk

- Low. Display text only. A mistake would show a wrong figure in a flag's text, while the stored cents stay correct. The tests compare against the shared helpers that CHG-2026-057 already tested.
- Review state: see the owner item above.
- Does it change which suppliers or people are flagged publicly? **No.** The same flags, with the same IDs, are made. Publication rules are not changed.
- POPIA / licence impact: none. No new personal information. Test data uses made-up names.

## How to revert

Close the PR unmerged. If merged: `git revert -m 1 <merge commit>`. The next build makes the old text again, and the evidence hash goes back to the old value.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | the owner (approval to prepare and open the PR only, 14 Nov 2026 18:12 SAST; not a merge GO) | — | — |
| Reviewer (independent) | | | |
| Second reviewer (independent) | | | |

## popia-review verdict: PASS

The diff, this record, the change-log row and the PR description were scanned for SA ID and passport numbers, phone numbers, emails, addresses, account numbers, plates, precise locations, credentials and keys. None was found. No real supplier, person or body name is added: the tests use made-up names ("ACME (PTY) LTD", "Test LM"). No identity linking. The owner is named by role only; the owner's exact chat words are not in git, only in the private approval record. Nothing had to be removed.

## Result

DEV: tests succeeded on this branch. PR open, not merged. No publish and no PROD change.
