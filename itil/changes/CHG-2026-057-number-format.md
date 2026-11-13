# CHG-2026-057: Standard display format for numbers on screen and in reports

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner RFC for number display format, 13 Nov 2026 19:17 SAST; scope confirmed later that evening, as reported to the author (PublicFunds). Main open question closed by owner decision, 13 Nov 2026 19:30 SAST (scope decision, not a merge GO). Exact words are in the private approval record. |
| Status | Open PR, not merged. Needs two independent reviewer PASSes on the exact head, then an owner merge GO that names this head. |
| Type | **Normal-medium**. See "Why this type". |
| Environment | DEV only (branch `feat/chg-2026-057-number-format` from origin/main). Nothing pushed to main. Public data is not changed in this PR. No publish script was run. |
| CIs affected | New `thusa/format.py`; `apps/public-dashboard/index.html`; `thusa/coverage_ceiling.py`; `thusa/review/casepack.py`; `thusa/review/warehouse.py`; `thusa/report.py`; `thusa/publish.py`; `scripts/dashboard_check.py` (comment only); tests listed below; this record; `itil/registers/change-log.md` |
| Linked records | CHG-2026-047 (public-page comma thousands and point decimal; this change extends that rule and tightens amount decimals), old-repo work that was waiting on the comma-versus-point decimal question |
| Rollback | Close the PR unmerged. If ever merged: `git revert -m 1 <merge commit>`. Git history is the rollback; no .bkp files. |

## Why this type is Normal-medium

- **Not Standard.** It changes how the public site, the review app and reports show numbers, not docs or tests alone.
- **Not Normal-high.** It does not change detector thresholds, the publishing pipeline, which named entities are flagged, secrets, hosting, schema, CI workflows, or POPIA handling. Raw data files are not changed.
- **Normal-medium** matches CHG-2026-047: a display-format change on every public page (and, in this change, also in reports). It needs the owner and a second reviewer. A bot approval never fills a human slot. No reviewer PASS in this record is owner approval.

## Goal

Show every number that a person reads in one standard form. Keep machine-readable data files as plain decimals.

## Owner decision (main open question CLOSED)

Owner decision, 13 Nov 2026 19:30 SAST, as reported to the author (PublicFunds). Exact words are in the private approval record. This is a scope decision, not a merge GO.

The main open question is **CLOSED**. It matches what this PR already builds:

- Money and measured amounts (rands, c/l, the numeric part of a percentage, rates) are shown as 1,234,567.89: comma thousands, a point decimal, and exactly two decimals.
- Whole-number counts (flags, rows, entities, cells) are shown as 1,234, with no decimals.
- Years, dates, financial-year labels, IDs, SHAs, build IDs, change and incident numbers, and version numbers are left unchanged.

This replaces space thousands and comma decimals in display text (for example a case pack "R750 000" becomes R750,000.00). The display decimal is a point.

## Still open (related choices)

These related choices in this PR were not explicitly settled and remain open for the owner to confirm or amend:

- Rounding is Decimal ROUND_HALF_UP (half away from zero), not banker's rounding. Example: 1.225 → 1.23 and -1.225 → -1.23.
- A negative number uses a leading ASCII hyphen-minus (U+002D). A rand amount puts the minus before the R: -R1,234.50. Parentheses and en-dashes are not used.
- Compact abbreviations such as "R1.2 m" and "R1.50bn" are withdrawn on screen and in reports. The full form is used instead (R1,200,000.00).
- A percentage already stored in public data with one decimal (for example coverage `complete_pct` 75.7) is shown as 75.70%. The stored file is not recomputed.
- Short prose such as "R10 million", "20%" and "R0" / "R100" in glossary and detector descriptions is left as it was, except where a digit group already used space thousands (the bidding limits and the 2,500 HHI threshold).

## What changed

1. New module `thusa/format.py` with `format_amount`, `format_count`, `format_rand` (from cents), `format_pct` (from a fraction) and `format_pct_parts` (from complete/applicable counts, half-up with integer arithmetic).
2. The public dashboard has a matching JS block (`/* format:begin */` … `/* format:end */` in `apps/public-dashboard/index.html`): `formatAmount`, `formatCount`, `formatRand`, `formatPct`, `formatPctParts`. The existing helpers `num`, `pct`, `intg`, `randFull`, `randText` and `rand` call those functions. The by-type parity block stays self-contained and now uses two decimals.
3. Python report and review paths use the same helpers: case packs, the review-app `rand` filter, the internal HTML report, and the public snapshot HTML. Client CSV values stay plain (`csvValue` / raw numbers), with no thousands separator.
4. Case-pack bidding limits and the HHI threshold use comma thousands and, for rand amounts, two decimals.
5. Tests: new `tests/test_format.py` (negatives, zero, large values, ROUND_HALF_UP versus banker's rounding, None/NaN/infinities, Python/JS parity, and a proof that public-data JSON/CSV stay plain and that `thusa/publish_data.py` does not import the display helpers). Existing number-format, glossary, case-pack and by-type tests were updated for the two-decimal display.

## Stays the same

- Raw data files: CSV, JSON, the database, `public-data/v1` exports and the manifest keep plain point decimals with no thousands separator. `thusa/publish_data.py` is not edited.
- Years, dates, financial-year labels, IDs, SHAs, build IDs, change and incident numbers, and version numbers.
- The official anti-corruption hotline text (0800 701 701) is not treated as a count.
- Detector logic, thresholds and the text they write into the warehouse.
- No change was published, and the publish script was not run.

## Seen, not touched

- `thusa/detectors.py` still formats amounts in stored flag titles and explanations with one helper of its own (`R{cents/100:,.0f}`). Those strings are warehouse (and later export) content. A later change can show them in the standard display form without rewriting stored data, or can change the stored wording after a rebuild. They are left as they are.
- Review-app table cells that are not money columns (`*_cents`) still show the raw value. Counts in those tables are not yet passed through `format_count`. IDs and years in those tables stay unformatted, which is correct.
- CHG-2026-047's unmerged branch on the remote has no merge base with this main and is not used here. Display rules from that earlier work that already sit on main (comma thousands and a point decimal on the public page) are kept and tightened.
- Operator release notes on other open docs PRs are not edited in this change. After a merge they can use the same format in a later change.
- STATUS.md is stale relative to recent changes and is not updated here.
- Open docs PRs #1–#4 and their change-log rows. This PR also adds a change-log row, so a merge conflict in `itil/registers/change-log.md` is expected.

## Testing (evidence, not claims)

- New tests in `tests/test_format.py`, plus updates to `tests/test_number_format.py`, `tests/test_unknowns_by_type_constant.py`, `tests/test_improvements.py` and `tests/test_case_pack.py`.
- Full suite, this checkout: `uv run pytest -q` → **883 passed, 1 skipped** in 86.11 s on the first head. Re-run after this documentation-only follow-up (owner decision closing the main open question, 13 Nov 2026 19:30 SAST): **883 passed, 1 skipped** in 85.54 s. The skip is `tests/test_fuel_xlsx.py` (real November xlsx / history PDF not in `data/`). The previous count on this box, after CHG-2026-056, was 831 passed, 1 skipped. The extra passes are the new formatter tests.
- Before and after text snippets were saved under `/workspace/number-format-samples/` (not in git). Example: the headline context line moves from 90.8% to 90.82%; `randText(120000000)` moves from "R1.2 m" to "R1,200,000.00"; a case pack "R750 000" becomes "R750,000.00".
- `scripts/publish-public-data.sh` was not run.

## Risk

- South African readers often see a decimal comma and space thousands. The owner chose comma thousands and a point decimal, with two decimals for amounts. A reader can misread a number if one page or report keeps the old form. The dashboard_check scan still fails on a decimal comma or space thousands in public page text.
- Showing a stored one-decimal figure as two decimals (75.7 → 75.70%) can hide that the stored value was rounded to one decimal. This remains among the related choices that are still open.
- Withdrawing "R1.2 m" makes some dashboard figures longer. Chart axis labels may wrap. That is accepted in this change so that one format is used.
- Does it change which suppliers or people are flagged publicly? **No.** Only how numbers are written for a reader. No detector or publication rule changes.
- POPIA / licence impact: none. No new personal information. Exact owner words are not in this change.

## How to revert

Close the PR unmerged. If merged: `git revert -m 1 <merge commit>`, then run `uv run pytest`. Git is the rollback.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | the owner (go-ahead to prepare and open the RFC/PR only, 13 Nov 2026; not a merge GO) | — | — |
| Reviewer (independent) | | | |
| Second reviewer (independent) | | | |

## popia-review verdict: PASS

Diff, new CHG record, change-log row, tests, and the PR description were scanned. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key was introduced. The existing official hotline 0800 701 701 in the case pack is unchanged. No person or supplier is newly named. No identity linking. The owner's exact chat words are not in this change; they stay in the private approval record. Nothing was removed from the diff.

## Result

DEV: tests succeeded on this branch. PR open, not merged. No PROD change.
