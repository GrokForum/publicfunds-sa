# CHG-2026-057: Standard display format for numbers on screen and in reports

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner RFC for number display format, 13 Nov 2026 19:17 SAST; scope confirmed later that evening, as reported to the author (PublicFunds). Main open question closed by owner decision, 13 Nov 2026 19:30 SAST. Style choices closed by owner decision, 14 Nov 2026 16:46 SAST. Both are scope/style decisions, not a merge GO. Exact words are in the private approval record. |
| Status | Implemented / closed. Merged 14 Nov 2026 18:05 SAST as `1c6ecda9` (PR #6, exact head `78c30c1d0821f93bfb6b8526c54b62ba9572e5fc`, tag `snapshot-2026-11-14-1806`). Owner GO, 14 Nov 2026 18:05 SAST, as reported to the author (PublicFunds). Exact words are in the private approval record. Post-merge checks are in Result. Q4 and Q5 were answered by the owner on 14 Nov 2026 18:12 SAST, as reported to the author (PublicFunds), and moved to CHG-2026-059 (work in progress, PR to follow). Recorded by CHG-2026-058. |
| Type | **Normal-medium**. See "Why this type". |
| Environment | Merged and live. Merged 14 Nov 2026 18:05 SAST as `1c6ecda9` (PR #6, exact head `78c30c1d`, tag `snapshot-2026-11-14-1806`). GitHub Pages build `43613702790` succeeded for that commit. `scripts/check_live.py` exited 0 at 18:07 SAST on 14 Nov 2026. The format change is display-only; live data remains build B20261114T005655Z. |
| CIs affected | New `thusa/format.py`; `apps/public-dashboard/index.html`; `thusa/review/casepack.py`; `thusa/review/warehouse.py`; `thusa/review/app.py`; review-app templates; `thusa/report.py`; `thusa/publish.py`; `scripts/dashboard_check.py` (comment only); tests listed below; this record; `itil/registers/change-log.md` |
| Linked records | CHG-2026-047 (public-page comma thousands and point decimal; this change extends that rule to reports and the review app), old-repo work that was waiting on the comma-versus-point decimal question |
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

- Money and measured amounts are shown in the 1,234,567.89 style: comma thousands and a point decimal. The number of decimals follows the style decisions below (money in cents: exactly two).
- Whole-number counts (flags, rows, entities, cells) are shown as 1,234, with no decimals.
- Years, dates, financial-year labels, IDs, SHAs, build IDs, change and incident numbers, and version numbers are left unchanged.

This replaces space thousands and comma decimals in display text (for example a case pack "R750 000" becomes R750,000.00). The display decimal is a point.

## Owner style decisions (CLOSED)

Owner decisions, 14 Nov 2026 16:46 SAST, given directly by the owner. Exact words are in the private approval record. These are style decisions, not a merge GO. Every style item that the earlier heads listed as open is now **CLOSED**:

1. **Short forms: CLOSED.** Two contexts. TABLES (figures that are listed or added up: dashboard tables, review-app tables, report and case-pack tables) show the full figure: R1,234,567.89 for rand, 1,234 for counts. PROSE and headline text (sentences, cards, summary lines) may use a readable short form: R1.2 m, R3.45 bn. Where the exact value matters in prose (a flag's evidence amount, a threshold such as the bidding limits), the full figure is shown.
2. **Coverage percentages: CLOSED.** Percentages show the precision the data holds. Coverage stored as 75.7 shows as 75.7%, not 75.70%; Present % 81.9 shows as 81.9%. Percentages are not padded to two decimals.
3. **Rounding: CLOSED.** The formatter adds no rounding. It shows a value at its source precision. Money held in integer cents shows exactly two decimals, because that is the data's precision. A value whose precision is set by the data or by a documented calculation keeps that precision. The ROUND_HALF_UP rule of the earlier heads is removed from the formatter.
4. **Negatives: CLOSED.** A negative rand amount stays -R1,234.50 (ASCII hyphen-minus before the R). Zero is never signed: -0.0 shows as 0.00 (R0.00 for money).
5. **Data files: unchanged.** CSV, JSON, the database, public-data/v1 and the manifest stay plain decimals.
6. **Short prose words** such as "R10 million" and "20%" stay as they are (readability in words).

## For the owner (readings this change was not sure of)

These are explicit questions, not open defects. The PR implements the reading shown; the owner can confirm or amend it.

- **Q1. The short form drops digits.** "R1.2 m" cannot show every digit. The short form keeps the public page's rule from before CHG-2026-057: one decimal for millions, up to two for billions, trailing zeros dropped, and the dropped part rounded half away from zero (as the page's `toLocaleString` did). This is the only place a display helper drops digits, and only in prose; the full figure stays in the table and in the hover title. Is that the intended reading of "keep short forms"?
- **Q2. Amounts under R1 million in prose** are shown in full (R123,456.78), not as whole rand (the page showed R123,457 before). This avoids rounding. Confirm.
- **Q3. "Unless the decimals or integers are important, e.g. space delimited."** Read as: where the exact value matters (thresholds, evidence amounts), show the full figure, with comma thousands, never space thousands. The bidding limits therefore stay R750,000.00. Confirm.
- **Q4. Calculations that already round.** Some figures are computed with an existing, documented rule before any formatter sees them: stored coverage percentages use one decimal (Python `round`); the headline context lines use one decimal with integer half-up arithmetic (CHG-2026-047); the page's by-type and province ratios use `Math.round` to one decimal (CHG-2026-033); computed ratios on the page (spending against budget, CPI change, fuel difference) use one decimal as before; computed rand results (inflation tool, fuel difference) are taken to the cent. This change keeps each existing rule and does not change any data calculation. Should a later change make these calculation rules the same everywhere?
- **Q5. Detector flag text.** `thusa/detectors.py` writes amounts into stored flag titles and explanations as whole rand (`R{cents/100:,.0f}`). That text is data, not display, and is not changed here. A flag's evidence amount is shown in full in the evidence tables. Should a later change store the full figure in the flag text?

**Q4 and Q5 answered and moved.** The owner answered Q4 and Q5 on 14 Nov 2026 18:12 SAST, as reported to the author (PublicFunds). Exact words are in the private approval record. The work has moved to CHG-2026-059 (work in progress, PR to follow). The leftovers named there remain `thusa/review/warehouse.py:137` (share display, for example `share_of_top15` as `:.1%`) and `thusa/detectors.py:25` (flag text via `_rand`, whole rand). They are not implemented in CHG-2026-058.

## What changed

Items 1–5 and the review follow-up describe the earlier heads. Where they say two decimals, half-up rounding, `format_pct_parts` or 81.90%, the owner style follow-up below replaces them.

1. New module `thusa/format.py` with `format_amount`, `format_count`, `format_rand` (from cents), `format_pct` (from a fraction) and `format_pct_parts` (from complete/applicable counts, half-up with integer arithmetic).
2. The public dashboard has a matching JS block (`/* format:begin */` … `/* format:end */` in `apps/public-dashboard/index.html`): `formatAmount`, `formatCount`, `formatRand`, `formatPct`, `formatPctParts`. The existing helpers `num`, `pct`, `intg`, `randFull`, `randText` and `rand` call those functions. The by-type parity block stays self-contained and now uses two decimals.
3. Python report and review paths use the same helpers: case packs, the review-app `rand` filter, the internal HTML report, and the public snapshot HTML. Client CSV values stay plain (`csvValue` / raw numbers), with no thousands separator.
4. Case-pack bidding limits and the HHI threshold use comma thousands and, for rand amounts, two decimals.
5. Tests: new `tests/test_format.py` (negatives, zero, large values, ROUND_HALF_UP versus banker's rounding, None/NaN/infinities, Python/JS parity, and a proof that public-data JSON/CSV stay plain and that `thusa/publish_data.py` does not import the display helpers). Existing number-format, glossary, case-pack and by-type tests were updated for the two-decimal display.

### Review follow-up (head 394b3e4e)

The first reviewer passed the code and asked for a fresh head that covers every displayed number.

1. Coverage-by-type "Present %" uses `pctPoints` (81.9 shows as 81.90%). The CSV still has the plain stored value.
2. The table helper now shows a `num` column with a bare numeric `value` through `formatCount` (for example Awards, Present/Partial/Missing, hidden leads). The CSV path is unchanged. Other leftover counts (confirmed-flags heading, coverage row count, report-card flag and gap counts, "most common gap reason" count) use `intg`. Review-app templates format non-cents count columns and status/coverage counts through the `count` and `amount` filters. Years, dates, IDs, SHAs and versions stay unformatted.
3. Stale second arguments such as `pct(share, 0)` are removed.
4. The change-log row and the `thusa/format.py` module note now state that the main rule is decided (owner decision, 13 Nov 2026 19:30 SAST). Related choices stay open.
5. Optional: `format_amount(-0.0)` and any value that rounds to zero show `0.00`, never `-0.00`, with a test. The CHG-2026-056 change-log row, which still said the PR was not merged, now records the merge of PR #5 at 13 Nov 2026 19:16 SAST (merge 8cdf9ad6). That side fix is documentation only.

### Owner style follow-up (head 0893952b, replaces the rounding and padding above)

Implements the owner style decisions of 14 Nov 2026 16:46 SAST:

1. `thusa/format.py` and the page block (`/* format:begin */` … `/* format:end */`) no longer round. `format_amount(value, places=0)` / `formatAmount` show source precision; `places` only pads with zeros. `format_rand` / `formatRand` show the full figure from cents (two decimals). New `format_rand_short` / `formatRandShort` give the prose short form. `format_pct` / `formatPct` shift a stored fraction exactly (0.9707 → 97.07%, 0.5 → 50%). New `format_pct_points` / `pctPoints` take a percentage-point value and an optional calculation precision. `format_pct_parts` / `formatPctParts` (a rounding helper) are removed. New `is_count_column` is shared by review-app and case-pack tables.
2. Dashboard: tables use `randCell` (full figure); prose and cards use `rand` (short form, full figure in the hover title); chart axis labels use the short form, chart hover titles the full figure. Coverage 75.7%, Present % 81.9% (one decimal, the stored calculation's precision). Computed ratios use `ratioPct` (one decimal, the page's rule before this change); computed rand results use `toCent`. The fuel price is shown from cents without a float division.
3. `thusa/coverage_ceiling.py` and the page's by-type and context-line calculations are back to their documented one-decimal rule (as on main): 90.8%, 64.9%, 83.3%.
4. Reports: `thusa/report.py` tables keep the full figure; the eTenders summary sentence uses `rand_short`. Report, snapshot and review-app coverage percentages use one decimal (75.7%). Case-pack table counts now use 1,234.
5. Thresholds in prose (bidding limits, HHI 2,500) keep the full figure.

### Review finding fix (this head)

Both independent reviewers passed head 0893952b with one required fix: in a text report there is no hover title, so a short form must carry its full figure. `thusa/report.py` `rand_short` now writes "R1.2 m (R1,200,000.00)". When nothing is shortened (under R1 m, or unknown) the full figure is shown once, with no brackets. A search of the Python report paths found no other short form: case packs and other Markdown output already use the full figure. The public dashboard is not changed (it shows the full figure in the hover title). Data files are not changed. Tests: `test_text_report_short_form_carries_full_figure_in_brackets` and `test_rendered_text_report_sentence_has_bracketed_full_figure`.

## Stays the same

- Raw data files: CSV, JSON, the database, `public-data/v1` exports and the manifest keep plain point decimals with no thousands separator. `thusa/publish_data.py` is not edited.
- Years, dates, financial-year labels, IDs, SHAs, build IDs, change and incident numbers, and version numbers.
- The official anti-corruption hotline text (0800 701 701) is not treated as a count.
- Detector logic, thresholds and the text they write into the warehouse.
- No change was published, and the publish script was not run.

## Seen, not touched

- `thusa/detectors.py` still formats amounts in stored flag titles and explanations with one helper of its own (`R{cents/100:,.0f}`). Those strings are warehouse (and later export) content. They are left as they are (see Q5).
- Review-app table cells that are not money columns and not recognised as counts (column names such as `awards`, `n_lines`, `present_n`, or ending in `_n` / `_count` / `_lines`) still show the raw value. IDs, years, scores and text stay unformatted, which is correct.
- CHG-2026-047's unmerged branch on the remote has no merge base with this main and is not used here. Display rules from that earlier work that already sit on main (comma thousands and a point decimal on the public page) are kept and tightened.
- Operator release notes on other open docs PRs are not edited in this change. After a merge they can use the same format in a later change.
- STATUS.md is stale relative to recent changes and is not updated here.
- Open docs PRs #1–#4 and their change-log rows. This PR also adds a change-log row, so a merge conflict in `itil/registers/change-log.md` is expected.

## Testing (evidence, not claims)

- New tests in `tests/test_format.py`, plus updates to `tests/test_number_format.py`, `tests/test_unknowns_by_type_constant.py`, `tests/test_improvements.py` and `tests/test_case_pack.py`.
- Full suite, this checkout: `uv run pytest -q` → **883 passed, 1 skipped** on the first head (86.11 s) and on the documentation follow-up (85.54 s); **888 passed, 1 skipped** on the review follow-up (89.40 s); **905 passed, 1 skipped** (83.82 s) on the owner-style head; **907 passed, 1 skipped** (88.47 s) on this review-fix head. The skip is `tests/test_fuel_xlsx.py` (real November xlsx / history PDF not in `data/`). The previous count on this box, after CHG-2026-056, was 831 passed, 1 skipped.
- This head's tests: no rounding in the formatter (Python source scan and JS block scan, the short form excepted), source precision and pad-only `places`, signed zero, full rand in tables (every table column with a rand CSV value renders `randCell`), short form in prose, coverage 75.7% and no 75.70% / 81.90% left, stored shares at stored precision, Python/JS parity for all helpers including the short form, report tables full and report prose short, and the count-column rule.
- `scripts/dashboard_check.py` (headless browser check) was not run on this box: the optional Playwright group is not installed. Its number scan is covered by `tests/test_number_format.py::test_dashboard_check_number_scan`.
- Before and after text snippets were saved under `/workspace/number-format-samples/` (not in git). This head (`style-before-after.txt`): table R1,200,000.00 (unchanged); prose R1,200,000.00 → R1.2 m and R3,450,000,000.00 → R3.45 bn; coverage 75.70% → 75.7%; Present % 81.90% → 81.9%; share 50.00% → 50%; negative -R1,234.50 (unchanged); headline context 90.82% → 90.8% (as on main). A case pack "R750 000" still becomes "R750,000.00".
- `scripts/publish-public-data.sh` was not run.

## Risk

- South African readers often see a decimal comma and space thousands. The owner chose comma thousands and a point decimal. A reader can misread a number if one page or report keeps the old form. The dashboard_check scan still fails on a decimal comma or space thousands in public page text.
- The same amount can appear as R1,200,000.00 in a table and R1.2 m in a sentence on the same page. That is the owner's decision (tables full, prose readable); the hover title on the page shows the full figure.
- Showing source precision means two figures in one column can have different numbers of decimals (for example a share of 50% next to 97.07%). That follows the owner's decision not to pad percentages.
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

The first heads, the review-follow-up diff, and this owner-style diff (formatters, dashboard, reports, review app, case pack, tests, change log, this record and the updated PR description) were scanned. The owner's 14 Nov 2026 words are only in the private approval record. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key was introduced. The existing official hotline 0800 701 701 in the case pack is unchanged. No person or supplier is newly named. No identity linking. The owner's exact chat words are not in this change; they stay in the private approval record. Nothing was removed from the diff.

## Result

Implemented / closed. Merged as PR #6 on 14 Nov 2026 18:05 SAST at exact head `78c30c1d0821f93bfb6b8526c54b62ba9572e5fc`, merge commit `1c6ecda931463bf2af9723f3da6fa80e5d3360fd`, tag `snapshot-2026-11-14-1806`. Owner GO, 14 Nov 2026 18:05 SAST, as reported to the author (PublicFunds). Exact words are in the private approval record.

Post-merge checks, 14 Nov 2026 18:06–18:10 SAST, as recorded by CHG-2026-058:

- GitHub Pages build `43613702790` succeeded for head `1c6ecda9` (18:05:40–18:06:07 SAST).
- `scripts/check_live.py` exited 0 at 18:07 SAST. Live data is still build B20261114T005655Z (generated 2026-11-14 02:57 SAST). The format change is display-only; raw public-data files were not part of this merge.
- The live file `https://publicfunds.grokforum.site/apps/public-dashboard/index.html` is byte-identical to `apps/public-dashboard/index.html` on `1c6ecda9`, including the `/* format:begin */` … `/* format:end */` block.
- Headless Chromium on the live dashboard showed the new formats: table money as `R48,227,444,496.00` (and the same row's audited spending `R74,870,489,318.00`); card/prose short form `R74.87 bn` and `R1.98 bn`; the same card's `title` attribute `R74,870,489,318.00`; coverage `75.7%`; counts `1,167` and `1,542`. A native `title` tooltip does not always paint in headless Chrome; the attribute was read from the DOM. Evidence files were kept outside git.
- Local `uv run thusa report` regenerated the internal text report. `thusa.report.rand_short(120000000)` returns `R1.2 m (R1,200,000.00)`. A typical report line is `total known value R526.8 m (R526,826,020.00)`.
- `uv run pytest -q tests/test_format.py tests/test_number_format.py` → 85 passed.

Q4 and Q5 were answered by the owner on 14 Nov 2026 18:12 SAST, as reported to the author (PublicFunds), and moved to CHG-2026-059 (work in progress, PR to follow).
