# CHG-2026-062: Fruitless and wasteful expenditure metric, Phase 1 (municipalities)

| Field | Value |
|---|---|
| Requested by / date (SAST) | The owner, 15 Nov 2026, as reported to the author (PublicFunds): news reports often quote fruitless and wasteful expenditure, so it is a useful metric if the data exists. Owner GO for **Phase 1 only**, as reported to the author (PublicFunds) by the orchestrator, 16 Nov 2026 00:49 SAST. That GO covers building Phase 1 on a local branch. It is not a merge GO. Exact words are in the private approval record, not in this repo. |
| Status | DEV only. Local branch `chg-2026-062-fw-expenditure` from `ceabf99`. Not pushed. No PR. Nothing on `main`. Commit 1: `180154f7` (reviewer FAIL, see "Review finding on 180154f7"). Commit 2: the fix in this record. |
| Type | **Normal-medium.** A new mart, new export fields and a new page, all from data that is already in the warehouse. No new source, no download, no detector, no change to `config/publication.yaml` or to the publishing pipeline. |
| Environment | DEV (the worktree of the author's computer). TEST and PROD need their own steps (see "Implementation plan" and "Pending for TEST"). |
| CIs affected | `thusa/models/marts/110_fw_metric.sql` (new, CI-115); `thusa/fw_metric.py` (new); `thusa/dq.py` (new checks); `thusa/build.py` (row counts); `thusa/publish_data.py` (municipalities.json fields); `apps/public-dashboard/index.html` (new page `#/fw` and a section on each municipality page); `scripts/dashboard_check.py` (route and page mirror); `tests/test_fw_metric.py` (new); this record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md` |
| Linked records | CHG-2026-057 and CHG-2026-059 (number format), RSK-022 (public misreading), RSK-023 (defamation), KE-008 (totals summed from line items) |
| Rollback point | `ceabf99` (tag `snapshot-2026-11-15-pr1-4-10`) |
| Rollback | Before merge: delete the branch and the worktree. After merge: `git revert -m 1 <merge commit>`. Git is the rollback; no .bkp files. |

## Goal

Show fruitless and wasteful (F&W) expenditure for each municipality: the amount from 2017/18 to 2023/24, and, where audited spending is complete enough, its **share of audited spending**, as a trend and as a national view. This turns one headline number into figures that a reader can check, each with its source.

## Scope

In scope (Phase 1, approved to build):
- Municipalities only. Data already in the warehouse: Municipal Money `uifwexp` (F&W amounts, `curated.uifw_line`) and audited actual totals (`curated.muni_total`, amount type AUDA).
- Amounts for financial years ending 2018 to 2024 (2017/18 to 2023/24). Shares for financial years ending 2020 to 2024 (2019/20 to 2023/24) only, and only where the completeness check passes.

Out of scope:
- **Years ending 2012 to 2017.** They are left out until a manual spot check passes. The page says so. (No audited-spending denominator is loaded before the year ending 2018, so these years could never have a share.)
- **Phase 2** (national and provincial departments and public entities, AGSA PFMA annexures) and **Phase 3** (2024/25 from the AGSA PDF annexure). These are **not approved**. No AGSA figure is exported by this change.
- A ranking, a "largest first" order or a top-10 list (owner decision D2, not given).
- The existing UIF&W section of the municipality page. It still shows the 2011/12 to 2016/17 amounts, as before.

## Review finding on 180154f7 (reviewer FAIL, 16 Nov 2026)

The reviewer (orchestrator) found that commit `180154f7` reproduced the source correctly, but would publish wrong shares. Audited spending at the source is incomplete for about 100 municipality-years. For the years ending 2018 to 2022 it is summed from line items, and some years have only a few of the about 13 expenditure lines. Example: Merafong City 2021/22 showed 71.2372%, from R104,112,173.00 of audited spending made of 2 lines, while its other years are R1.26 bn to R3.26 bn. The "over 100%" rule caught only the 8 most extreme cases. For 2017/18 and 2018/19 the problem is widespread (pre-mSCOA data). Shares like these, for named public bodies, fail test T5 and RSK-023.

Fix (commit 2):
1. **No share for 2017/18 and 2018/19**, per municipality and nationally. The amounts stay. Status `denominator_incomplete_year`.
2. **Completeness check for 2019/20 to 2023/24.** It replaces the "over 100%" rule as the main guard (see "Share rule").
3. The AG comparison warning now reports the real number of mismatches.
4. New statuses, data-quality checks, tests, page text and `about` text for all of this.

## What changed

1. **New mart** `thusa/models/marts/110_fw_metric.sql`:
   - `marts.fw_metric`: one row for each municipality and year (2018 to 2024) that has an F&W amount or an audited spending figure. Columns: `fw_cents`, `denom_cents` (audited total operating expenditure), `denom_basis` (`audited_total_expenditure`), `denom_derivation` (published subtotal or sum of line items, KE-008), `denom_ref_years` and `denom_ref_median` (the completeness reference, see below), `share_status`, `fw_share_pct`, `fw_prev_cents`, `fw_change_cents`, and lineage (`source_id`, `source_file`, `source_sha256`, `fetched_at_utc`, `source_locator`, `denom_source_sha256`).
   - `marts.fw_national`: one row for each year (see "National share").
2. **Share rule** (a documented calculation, as CHG-2026-057 requires):
   - share = F&W ÷ audited spending × 100, in percentage points;
   - it is **cut** (truncated toward zero) to 4 decimal places with integer arithmetic. **Nothing is rounded**, so a half is never rounded up;
   - a known 0 F&W amount gives a 0 share. A very small non-zero amount can cut to 0.0000; the page then shows "under 0.0001%", never 0%.
   - The share is NULL ("not available", never 0). `share_status` gives the reason. The SQL checks the reasons in this order:

     | Status | When |
     |---|---|
     | `fw_unknown` | no F&W amount |
     | `denominator_unknown` | no audited spending |
     | `denominator_not_positive` | audited spending is zero or less (no divide by zero) |
     | `denominator_incomplete_year` | year ending 2018 or 2019: audited spending at the source is incomplete for many municipalities |
     | `denominator_no_reference` | 2020 to 2024, but the municipality has no **other** year from 2020 to 2024 with audited spending above zero, so the check cannot run (for example Kopanong 2023/24) |
     | `denominator_incomplete` | 2020 to 2024, and audited spending is **under 50%** of the median audited spending of the same municipality in its **other** years from 2020 to 2024 (only years above zero count) |
     | `share_over_100` | fallback: the check above passed, but F&W is still larger than audited spending |
     | `ok` | a share is shown |

   - **Why the reference uses 2020 to 2024 only:** 2018 and 2019 are the years found to be incomplete, so they would pull the median down and weaken the check. "Other years" means that a year is never compared with itself. The median (not the mean) means one bad other year does not hide a normal year. The median of an even count can end in .5 cent, so `denom_ref_median` is a DECIMAL in cents, and the rule is computed exactly as "audited spending × 2 < median".
3. **National share** (decision): `fw_total_cents` is the sum of **every** known municipal F&W amount, hidden shares included. The share uses **only** municipality-years whose own status is `ok`. A municipality-year whose share is hidden is **left out of both parts**: its F&W is not in `fw_share_base_cents`, and its audited spending is not in `denom_share_base_cents`. `n_share_hidden` counts these rows. `national_share_status` is `denominator_incomplete_year` for 2018 and 2019 (no national share), `no_base` when no row is `ok`, and otherwise `ok`. Reason: adding a hidden row's F&W without its spending (or the other way round) would make the national share wrong in the same way as the hidden row.
4. **Constants** in `thusa/fw_metric.py`: the year range (2018, 2024), the first share year (2020), the 50% ratio, the status codes (`SHARE_STATUS`, `GUARD_STATUS`, `NATIONAL_STATUS`) and the 4 decimal places. A test keeps the SQL numbers equal to them.
5. **Data-quality checks** in `thusa/dq.py` (`fw_checks`, part of every build). Errors: unique rows; years in range; valid status; share only when the status is `ok`; status matches the inputs; **no share for 2018 and 2019**; **2018 and 2019 rows with both figures have `denominator_incomplete_year`**; **the stored reference equals a fresh recomputation from the mart**; **the completeness rule gives the stored status**; share matches the inputs exactly under the cut rule; no share over 100; change equals the prior-year difference; every F&W line in range is in the mart; the yearly sums equal the source to the cent (T3); the national table equals the mart (totals, counts, hidden count and both share bases); the national share rule; lineage present and resolving (also for the denominator). Warnings (reported, never a build failure): `fw_share_guarded_info` (2020–2024 shares hidden by the completeness rules) and `fw_agsa_reconcile_info` (T2: the real number of rows outside R50,000.00; before this fix it showed 0 unless more than 2% were outside). `MIN_ROWS` adds `marts.fw_metric` ≥ 1,000.
6. **Export** (`public-data/v1/municipalities.json`, after a merge and the next nightly): each year from 2018 to 2024 gets `fw: {share_pct, status, change}`. The file gets `fw_years`, `fw_national` (with `n_hidden` and `status`) and plain-language `about` lines for the year rule, the completeness check, each status and the national base. The amounts were already in `uifw.fruitless_wasteful` and `audited.exp`; they are not copied. Numbers stay plain decimals (the share is a JSON number such as `0.187`).
7. **Page** (`apps/public-dashboard/index.html`):
   - new menu item and page **Fruitless & wasteful** (`#/fw`): the definitions and caveats (including the 2017/18–2018/19 rule and the completeness check), a national trend line of the share, a national table per year (with the number of municipalities whose share is not available, and "not used" for the share bases in 2017/18 and 2018/19), and a table of all municipalities for a chosen year and province, **in alphabetical order only** (not a ranking), with a CSV download that includes the status of each row;
   - each municipality page gets a section under the existing UIF&W table: a trend line of the share and a table with the amount, audited spending, share, change from the year before and source;
   - "not available" carries its reason as a tooltip, and the CSV has the status;
   - only the central formatters are used: R1,234,567.89 in tables, -R1,234.50 for negative values, the share at its stored precision (0.187%, 5.07%), counts as 1,234;
   - F&W is never added to irregular or unauthorised expenditure. The page says that F&W is not proof of theft or corruption.
8. `scripts/dashboard_check.py`: the new route and page are added to its mirrors.

## Stays the same

- All sources, connectors and raw files. All curated tables. The coverage model and the coverage numbers.
- Detectors, flags, review rules and `config/publication.yaml`. No detector reads `marts.fw_metric`.
- The existing UIF&W section of the municipality page (chart and table), including its 2011/12 to 2016/17 amounts.
- The existing audited-spending figures on the municipality page (see "Seen, not touched").
- All existing fields in `municipalities.json`. Nothing is removed or renamed.

## Decisions made in this build (please check)

1. **Completeness check:** 50% of the median of the other years 2020–2024, as the reviewer asked. The ratio and the reference years are the author's choices within that request.
2. **No reference year:** the share is hidden (`denominator_no_reference`). A single reference year is enough to run the check (for example !Kai! Garib 2020/21 is compared with one other year).
3. **`share_over_100`** stays as an explicit fallback status. In the local build, all 8 former over-100% cases are caught before it: 6 by `denominator_incomplete_year` and 2 (Mogale City 2021/22, Renosterberg 2022/23) by `denominator_incomplete`. A test covers each kind.
4. **National share:** hidden municipality-years are left out of both parts (see "National share").
5. **No AGSA figures.** The AGSA cross-check runs only as a warning (T2).
6. **Change from the year before** is in cents and is NULL when either year is unknown. 2017/18 has no prior year in this view.

## Deviations from the draft RFC

- Branch name `chg-2026-062-fw-expenditure` (the draft had `feat/chg-2026-062-fw-metric`), as the task asked.
- No `agsa_fw_cents` / `agsa_diff_cents` columns and no `source_url` column in the mart. The URL resolves through `ops.raw_file` and the export's `sources`.
- No share for 2017/18 and 2018/19, and the completeness check, are new (review finding).
- The new municipality chart shows the share only. The existing UIF&W bar chart already shows the amounts.
- No `config/public-data.yaml` text change. The explanation is in the `about` lines of `municipalities.json` and on the page.
- The "under 0.0001%" text is new.
- No preview build, no TEST step and no axe scan yet (see "Pending for TEST").

## Testing (evidence, not claims)

- `uv run pytest -q` in the worktree (no warehouse): **924 passed, 83 skipped, 0 failed** (baseline on `ceabf99`: 865 passed, 61 skipped). The 22 more skips are the new checks in `tests/test_dq_warehouse.py`, which run only against a real warehouse. The 59 tests in `tests/test_fw_metric.py` cover:
  - T1: each status, no divide by zero, 0 stays 0, cut-not-round cases (2/3 cents gives 66.6666; 0.00005 and 0.0000625 give 0.0000; 0.00015 gives 0.0001), 100% kept, the `share_over_100` fallback, no overflow with very large amounts;
  - 2018 and 2019 keep the amount and never have a share; a missing figure is reported before the year reason;
  - no reference year (Kopanong-like case; 2019, zero and negative years are no reference);
  - the 50% rule at its edges (49 hidden, exactly 50 shown; even-count median 150: 74 hidden, 75 shown), a Merafong-like case (4%), and one low other year that does not hide a normal year;
  - every kind of former over-100% case is hidden;
  - national share: a hidden row is in the total but out of both share bases; no national share for 2019; `no_base`;
  - years 2017 and 2025 and non-municipal bodies left out; change uses the prior year only;
  - T4: the mart never reads irregular or unauthorised rows; the export adds only `share_pct`, `status` and `change`;
  - each data-quality check passes on a clean mart that has every status, and fails on a broken one (15 tamper cases, including the new year, completeness, reference and national checks);
  - the AG warning reports the real count (1 mismatch in 60 rows gives 1; the old 2% gate gave 0; a gap of exactly R50,000.00 is accepted);
  - the synthetic full build has the mart and its checks pass; the export has plain numbers, no share before 2020, and passes the public-safety scan;
  - page: route, menu and `dashboard_check` mirror; one sort only, alphabetical by name; no ranking words; neutral wording; no irregular or unauthorised field in the new code; central formatters only; the left-out years are stated; every hidden-share reason and national status has page text; the JS share text and axis ticks run in node.
  - The owner-quote and name guard tests pass.
- **Real-data check (read-only).** The new SQL and the full data-quality suite were run on a **fresh copy** of the local warehouse, build B20261115T155921Z (the local build of 15 Nov 2026, not the live nightly). The copy was deleted afterwards. Nothing in `/workspace/publicfunds` changed, and nothing was published.
  - Data-quality suite on the copy: **78 pass, 2 warn, 0 fail.** Warnings: `award_buyer_match_rate_info` (207, as before) and `fw_share_guarded_info` (14). `fw_agsa_reconcile_info` is **0** (pass): 226 of 226 linked municipalities for 2023/24 are within R50,000.00. The raw-file checksum check was not run on the copy.
  - T3: the yearly F&W sums in the mart equal the source lines to the cent (check passes).
  - `marts.fw_metric` has 1,799 rows; `marts.fw_national` has 7. Statuses: `ok` 1,200; `denominator_incomplete_year` 458; `denominator_unknown` 114; `denominator_not_positive` 13; `denominator_incomplete` 10; `denominator_no_reference` 4; `share_over_100` 0.
  - Shares hidden by the completeness rules (2019/20–2023/24): 2019/20 Dr Beyers Naudé, Mafikeng; 2020/21 !Kai! Garib, Siyathemba (incomplete), Nala (no reference); 2021/22 Merafong City, Mogale City, Tokologo, Tswaing; 2022/23 Renosterberg (incomplete), Mantsopa, Masilonyana (no reference); 2023/24 Ratlou (incomplete), Kopanong (no reference).
  - National view:

  | Year | F&W, all municipalities | With a share | Share not available | F&W in the share base | Audited spending in the share base | Share of audited spending |
  |---|---|---|---|---|---|---|
  | 2017/18 | R2,146,762,816.00 | 0 | 257 | not used | not used | not available |
  | 2018/19 | R3,783,551,069.00 | 0 | 257 | not used | not used | not available |
  | 2019/20 | R4,080,800,600.00 | 238 | 19 | R3,782,409,890.00 | R410,582,323,026.00 | 0.9212% |
  | 2020/21 | R1,959,230,789.00 | 240 | 17 | R1,544,896,574.00 | R399,974,245,289.00 | 0.3862% |
  | 2021/22 | R4,915,853,360.00 | 241 | 16 | R3,775,860,997.00 | R425,333,809,781.00 | 0.8877% |
  | 2022/23 | R7,471,621,788.00 | 237 | 20 | R6,967,500,483.00 | R493,211,664,225.00 | 1.4126% |
  | 2023/24 | R5,266,773,348.00 | 244 | 13 | R4,636,615,979.00 | R555,735,628,443.00 | 0.8343% |

- `scripts/dashboard_check.py` with a `municipalities.json` made from the copy (put in the worktree for the check only, then restored with `git checkout`): **0 problems**, desktop and mobile, the new page included. Merafong City shows "not available" for 2017/18, 2018/19, 2020/21 (audited spending below zero) and 2021/22. axe was not run (not installed).
- `municipalities.json` from the copy is 1,644,551 bytes (now 1,525,551; file budget 2,000,000). The total of all files stays under the 5,000,000-byte budget.

## Pending for TEST (before the owner GO)

1. **T5, by hand:** check the 10 largest shares in each year from 2019/20 to 2023/24 against the municipality's audited financial statements (AFS). Start with **Naledi (NW) 2019/20 (47.7615%)** and **Maluti-a-Phofung 2019/20 (27.4263%)**. Record each result here. A year or a row that fails stays hidden. The reviewer's check against the source API (not the AFS) matched for 9 rows.
2. **axe accessibility scan** of the new page with `scripts/dashboard_check.py` (axe-core is not installed on this computer).
3. A preview build and a check of the page by the reviewers.

## Risk assessment

| Risk | L | I | Score | Mitigation |
|---|---|---|---|---|
| Readers read F&W as theft or corruption, or add it to irregular expenditure (RSK-022) | 3 | 3 | 9 | Definitions and caveats on the page; "not proof of theft or corruption"; no combined total; tests T4 and T7 |
| A list reads as an accusation against a named body (RSK-023) | 2 | 4 | 8 | Alphabetical order only; no ranking; official figures only; no officials named; doubtful shares hidden |
| An incomplete denominator gives a wrong share | 2 | 4 | 8 | No share for 2017/18 and 2018/19; completeness check for later years; hidden rows out of the national base; T5 by hand before the GO |
| The completeness check hides a correct share, or misses a wrong one under 50% off | 2 | 2 | 4 | Hidden rows are counted in a warning and listed here; T5 by hand on the top shares |
| The source amount is a balance, not the year's spending | 3 | 2 | 6 | Caveat on the page; the source does not say (as in `040_uifw_line.sql`) |
| The public-data size budget gets closer to its limit | 2 | 2 | 4 | About +119 KB; the export refuses to write over budget |

- Does it change which suppliers or people are flagged publicly? **No.**
- **POPIA:** public bodies at entity level only. No natural person, no official, no ID, no contact detail. popia-review verdict: **PASS** (nothing found; nothing removed). The repo text names no owner account, agent or bot, and quotes no owner words.
- Licence: the same Municipal Money data the site already shows.

## Implementation plan

1. DEV (done): local branch from `ceabf99`, code, tests, records, real-data check on a warehouse copy; review fix in commit 2.
2. TEST: the items in "Pending for TEST".
3. Review: two independent reviewer PASSes on the exact head, then the owner's own GO naming that head. A new head needs new reviews.
4. Push and PR only after the owner approves that step.
5. After a merge: tag `snapshot-YYYY-MM-DD-HHMM` (SAST), run `scripts/check_live.py`. The next nightly rebuilds and publishes the new fields.

## How to revert

- Before merge: `git worktree remove /workspace/pf-chg062` and `git branch -D chg-2026-062-fw-expenditure`. Nothing is published.
- After merge: `git revert -m 1 <merge commit>`, then a PR with reviews and the owner's GO. The next nightly then writes `municipalities.json` without the `fw` fields. The mart is rebuilt from nothing on every run, so there is no migration to undo.

## Open questions for the owner

- **Q1 (D2):** keep alphabetical only (this build), or allow a "largest first" order later? Not in Phase 1.
- **Q2:** is the completeness check right (50% of the median of the other years 2019/20–2023/24; hidden when there is no other year)? Should it need at least two reference years?
- **Q3:** amounts for 2011/12 to 2016/17 on the new page after a spot check? A share is not possible for those years.

## Seen, not touched

- The existing municipality page already shows audited spending for the incomplete years (for example Merafong City 2021/22: R104,112,173.00). This is on `main` already and is a separate known-error or RFC candidate (KE-008 family).
- `STATUS.md` "Current" still lists PRs #1 to #4 as open and does not show the merges of #1 to #4 and #10 (15 Nov 2026 21:25–21:26 SAST). Only a line for this change is added.
- The merges of #1 to #4 and #10 have the tag `snapshot-2026-11-15-pr1-4-10`, not the usual `snapshot-YYYY-MM-DD-HHMM` form.
- `config/sources.yaml` lists `agsa_pfma` (connector `pdf_table`) and `agsa_mfma` (connector `html_list`) with `mvp: true`, but the loaded AGSA data comes from `agsa_annexures`. This is a docs drift.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority (owner) | | | |
| Reviewer 1 | | | |
| Reviewer 2 | | | |

## Post-implementation review
- Outcome: pending (DEV only). Commit `180154f7`: reviewer FAIL (incomplete denominators), fixed in commit 2.
