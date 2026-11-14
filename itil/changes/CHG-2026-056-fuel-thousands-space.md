# CHG-2026-056: Fuel history DOCX parser accepts a space as a thousands separator

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner go-ahead to prepare the fix PR, 12 Nov 2026 07:28 SAST, as reported to the author (PublicFunds). This is not a merge GO. |
| Status | Implemented / closed. Merged 13 Nov 2026 19:16 SAST as `8cdf9ad6` (PR #5, exact head `5db0c8c1`, tag `snapshot-2026-11-13-1917`). Owner GO, 13 Nov 2026, confirmed 14 Nov 2026, as reported to the author (PublicFunds). Exact words are in the private approval record. The 14 Nov 2026 nightly succeeded (B20261114T005655Z). INC-2026-004 is closed. Recorded by CHG-2026-058. |
| Type | **Normal** (parser change). After a merge, the next successful nightly will publish the November 2026 fuel row that now crashes the build. |
| Environment | DEV only (branch `fix/chg-2026-056-fuel-thousands-space` from origin/main). Nothing pushed to main. Public data is not changed in this PR. |
| CIs affected | `thusa/parsers.py` (`fuel_history_rows`, new `_fuel_history_number`); `tests/test_publish_data.py`; this record; `itil/registers/change-log.md`; INC-2026-004 |
| Linked records | INC-2026-004 |
| Rollback | Close the PR unmerged. If ever merged: `git revert -m 1 <merge commit>`. Git history is the rollback; no .bkp files. |

## Why this type is Normal, not Emergency or Normal-high

- **Not Emergency.** In this repo, Emergency is for a take-down of a wrong or defamatory figure, a leaked secret, or a broken routine that must be disabled. The live site still serves build B20261111T005910Z. The 12 Nov 2026 nightly failed and published nothing. That is a failed refresh, not a take-down. The owner approved only that a fix PR be prepared and opened for review.
- **Not Normal-high.** The change does not alter detector thresholds, the publishing pipeline, which named entities are flagged, secrets, hosting, schema, CI workflows, or POPIA handling.
- **Not Standard.** It is a parser code change, not docs or tests alone.
- **Normal** matches earlier fuel-parser fixes (CHG-2026-019, CHG-2026-022): a small parse-rule change that can add or correct public price figures after a merge and a nightly publish. One owner approval is required, after the reviewer PASSes, and only for the exact head.

## Goal

Stop the nightly build crash on a DMPR fuel-history cell that uses a space as a thousands separator (INC-2026-004). Keep every other parse rule the same, including the comma-versus-point decimal rule, which the owner has not decided yet.

## What changed

1. New helper `_fuel_history_number` in `thusa/parsers.py`. It strips a comma (as the old `float(cell.replace(",", ""))` did), and also strips a normal space, a no-break space (U+00A0) and a narrow no-break space (U+202F). It then calls `float`.
2. `fuel_history_rows` uses that helper for each price cell.
3. Two regression tests in `tests/test_publish_data.py`: the helper itself, and the DOCX parser, with `'3 085.67'`, the same digits with U+00A0 and U+202F, `'2 112.00'`, a value with no thousands separator, and a comma thousands value (`'1,234.50'`), which must still read as before.
4. This record, a change-log row, and a link from INC-2026-004.

## Stays the same

- The comma-versus-point decimal rule. A comma is still stripped, not turned into a decimal point. That question is not part of this change.
- `fuel_history_pdf_rows`, `_split_row_by_columns`, and the fuel-regulations XLSX parser.
- `_docx_tables` whitespace collapse (`re.sub` of one or more whitespace characters to a single space).
- Detector logic, the publishing scripts, public-data files, and the live site.

## Seen, not touched

- In today's DOCX, `_docx_tables` already turns the no-break space into a normal space before the number helper runs. The helper still strips U+00A0 and U+202F itself, so a cell that did not go through `_docx_tables` is also safe.
- The PDF parser already joins a thousands gap such as `'2 112.00'`. That code is left as it is.
- Offsite backup, check_live in the nightly, and other open docs PRs.

## Evidence (today's source, 12 Nov 2026)

The 12 Nov raw file `data/raw/dmpr_fuel/2026-11-12/fuel-price-adjustment-documents-november-2026.zip` contains `History of Fuel Prices November 2026.docx`. In the November row, the Inland diesel 0.05% cell is stored as the text nodes `'3'` + U+00A0 + `'085'` + `'.'` + `'67'`. After `_docx_tables` the cell is `'3 085.67'`. Before this change, `float(cell.replace(",", ""))` raised `ValueError: could not convert string to float: '3 085.67'`. After this change the value is 3085.67 c/l.

The other November 2026 grades in the same row have no thousands space and still read as printed: 2987.00, 2937.00, 3024.00, 2998.47, 2616.698, 2722.098. The DOCX yields 77 rows (January to November, 7 grades). The December cells are blank and stay skipped.

## Testing (evidence, not claims)

- New tests: `test_fuel_history_number_strips_space_thousands` and `test_fuel_history_rows_accepts_space_thousands`.
- Full suite, this checkout: `uv run pytest -q` → **831 passed, 1 skipped** in 87.44 s. The skip is `tests/test_fuel_xlsx.py:153` (real November xlsx / history PDF not in `data/`). An earlier count of 750 passed / 61 skipped was from a slimmer checkout; this box has the warehouse and the raw store, so the warehouse tests ran.
- Dry pipeline, no publish: `uv run thusa build` (12 Nov 2026 07:34:37 SAST) exited 0. `build_id` B20261112T053437Z. `staging.fuel_price` 735 rows; `curated.fuel_price` 665 rows; DQ pass 58, warn 1, fail none. Staging has November 2026 inland diesel 0.05% as 3085.670. `scripts/publish-public-data.sh` was not run.

## Risk

- A price cell with a space that is not a thousands separator would also lose its spaces and could be misread. In this DMPR history table the price cells are figures only; blank cells are still skipped. The November 2026 inland diesel cell is the first case seen in the raw store.
- After a merge, the next successful nightly will publish the November 2026 fuel figures (and any later month that uses the same format). A wrong parse would publish a wrong price. The new tests and the dry build on today's file are the check.
- Does it change which suppliers or people are flagged publicly? **No.** These are national regulated fuel prices from the official DMPR history table. No person or supplier is named in this change.
- POPIA / licence impact: none. Official public fuel prices only.

## How to revert

Close the PR unmerged. If merged: `git revert -m 1 <merge commit>`. The next nightly would crash again on the same cell unless the source format changes. Git is the rollback.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | the owner (go-ahead to prepare and open the PR only, 12 Nov 2026 07:28 SAST; not a merge GO) | — | — |
| Reviewer (independent) | | | |
| Second reviewer (independent) | | | |

## popia-review verdict: PASS

Diff, new CHG record, incident update, change-log row, and the PR description were scanned. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key was introduced. (Existing test fixtures in `tests/test_publish_data.py` already use sample ID numbers to prove the scrubber; those lines were not edited.) No person or supplier is named: official national fuel prices only. No identity linking. The owner's exact chat words are not in this change; they stay in the private approval record. Nothing was removed from the diff.

## Result

Implemented / closed. Merged as PR #5 on 13 Nov 2026 19:16 SAST at exact head `5db0c8c1aa46ae39f1fb71cfc616e90beb2c93d1`, merge commit `8cdf9ad6cb9e51bdc1d36a6d391696ce1f5f8123`, tag `snapshot-2026-11-13-1917`. Owner GO, 13 Nov 2026, confirmed 14 Nov 2026, as reported to the author (PublicFunds). Exact words are in the private approval record.

A manual refresh after the merge published build B20261113T172029Z (13 Nov 2026 19:21 SAST). The 14 Nov 2026 nightly then succeeded by itself: build B20261114T005655Z, generated 2026-11-14 02:57 SAST, `code_commit` `7a792ba` (which includes this merge). INC-2026-004 is closed. Recorded by CHG-2026-058.
