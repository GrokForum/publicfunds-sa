# CHG-2026-062: Fruitless and wasteful expenditure metric, Phase 1 (municipalities)

| Field | Value |
|---|---|
| Requested by / date (SAST) | The owner, 15 Nov 2026, as reported to the author (PublicFunds): news reports often quote fruitless and wasteful expenditure, so it is a useful metric if the data exists. Owner GO for **Phase 1 only**, as reported to the author (PublicFunds) by the orchestrator, 16 Nov 2026 00:49 SAST. That GO covers building Phase 1 on a local branch. It is not a merge GO. Exact words are in the private approval record, not in this repo. |
| Status | DEV only. Local branch `chg-2026-062-fw-expenditure` from `ceabf99`. Not pushed. No PR. Nothing on `main`. Commit 1: `180154f7` (reviewer FAIL, see "Review finding on 180154f7"). Commit 2: `22de78d8` (reviewer PASS_WITH_CONCERNS, see "Review finding on 22de78d8"). Commit 3: the high-bound fix in this record. |
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
- Municipalities only. Data already in the warehouse: Municipal Money `uifwexp` (F&W amounts, `curated.uifw_line`), audited actual totals (`curated.muni_total`, amount type AUDA) and, for the completeness check only, adjusted budget totals (`curated.muni_total`, amount type ADJB).
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

## Review finding on 22de78d8 (reviewer PASS_WITH_CONCERNS, 16 Nov 2026)

The reviewer (orchestrator) found the mirror case of the first finding: audited spending that is far too **high** understates the share. Examples: Kagisano-Molopo 2023/24 (audited spending R2,066,448,383.00 against an adjusted budget of R222,171,935.00, 9.3 times; 10.7 times its median; shown 0.0263%) and Ntabankulu 2019/20 (R763,611,541.00 against R201,355,685.00, 3.8 times; 3.5 times its median; shown 0.5504%).

Fix (commit 3):
1. **New status `denominator_implausible_high`.** No share when audited spending is over 2.5 times the median of the other years (the same reference as the 50% rule), or over 2.5 times that year's adjusted budget.
2. **Budget fallback when there is no other year** (option 2 of the review). The 50% and 2.5 times bounds are applied to that year's adjusted budget. `denominator_no_reference` stays only when the budget is also missing, zero or less.
3. The reviewer's answers are recorded under "Decisions made in this build".
4. New columns, data-quality checks, tests, page text and `about` text for all of this.

**Rows that the new rules catch in the local build** (no threshold was tuned to get this list):

| Rule | Municipality and year | Audited spending | Reference | Ratio | Share before |
|---|---|---|---|---|---|
| over 2.5 × median (also over 2.5 × budget) | Kagisano-Molopo 2023/24 | R2,066,448,383.00 | median R193,542,549.50; budget R222,171,935.00 | 10.677 × median; 9.301 × budget | 0.0263% |
| over 2.5 × median (also over 2.5 × budget) | Ntabankulu 2019/20 | R763,611,541.00 | median R215,407,563.50; budget R201,355,685.00 | 3.545 × median; 3.792 × budget | 0.5504% |
| over 2.5 × median only | **Merafong City 2023/24** (not in the reviewer's list) | R3,260,953,182.00 | median R1,257,856,039.00; budget R2,222,591,743.00 | 2.592 × median; 1.467 × budget | 4.8384% |
| budget fallback, under 50% | Nala 2020/21 | R167,888,503.00 | budget R508,097,544.00 | 0.330 × budget | hidden before (no reference) |
| budget fallback, under 50% | Masilonyana 2022/23 | R68,257,592.00 | budget R418,858,370.00 | 0.163 × budget | hidden before (no reference) |
| budget fallback, passes | Mantsopa 2022/23 | R363,771,554.00 | budget R439,597,925.00 | 0.828 × budget | now shown: 4.6960% |
| budget fallback, passes | Kopanong 2023/24 | R580,773,525.00 | budget R559,915,610.00 | 1.037 × budget | now shown: 16.4077% |

No row is caught by the budget bound alone. **Merafong City 2023/24 is an extra catch.** Its median is pulled down by its own incomplete 2021/22 figure (R104,112,173.00, itself hidden as `denominator_incomplete`). Its other years 2019/20 and 2022/23 are R1.26 bn and R2.40 bn, and its budget ratio (1.467) is normal, so its 2023/24 share is probably correct. The rule was not changed to let it through; the owner or the reviewer decides (see "Open questions", Q4). After this fix, `denominator_no_reference` has no rows in the local build.

## What changed

1. **New mart** `thusa/models/marts/110_fw_metric.sql`:
   - `marts.fw_metric`: one row for each municipality and year (2018 to 2024) that has an F&W amount or an audited spending figure. Columns: `fw_cents`, `denom_cents` (audited total operating expenditure), `denom_basis` (`audited_total_expenditure`), `denom_derivation` (published subtotal or sum of line items, KE-008), `denom_ref_years` and `denom_ref_median` (the completeness reference, see below), `denom_budget_cents` (the adjusted budget, see below), `denom_check_basis` (`other_years`, `adjusted_budget` or NULL: which reference the check uses), `share_status`, `fw_share_pct`, `fw_prev_cents`, `fw_change_cents`, and lineage (`source_id`, `source_file`, `source_sha256`, `fetched_at_utc`, `source_locator`, `denom_source_sha256`).
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
     | `denominator_no_reference` | 2020 to 2024, but the municipality has no **other** year from 2020 to 2024 with audited spending above zero, **and** that year's adjusted budget is missing, zero or less, so the check cannot run (no row in the local build) |
     | `denominator_incomplete` | 2020 to 2024, and audited spending is **under 50%** of the reference: the median audited spending of the same municipality in its **other** years from 2020 to 2024 (only years above zero count), or, with no other year, that year's adjusted budget |
     | `denominator_implausible_high` | 2020 to 2024, and audited spending is **over 2.5 times** the reference, or (when the reference is the other years) over 2.5 times that year's adjusted budget above zero |
     | `share_over_100` | fallback: the checks above passed, but F&W is still larger than audited spending |
     | `ok` | a share is shown |

   - **Adjusted budget (source and field):** `curated.muni_total` with `amount_type = 'ADJB'`, column `total_expenditure_cents`. It comes from Municipal Money (National Treasury Municipal Finance Data API), cube `incexp_v2` (Statement of Financial Performance), amount type ADJB (adjusted budget), the same loader and basis as the audited figure (item 4400 Total Expenditure when published, otherwise the sum of items 3000 to 4300, KE-008). In the local build all ADJB rows for 2020 to 2024 (251 to 256 a year) are above zero and summed from line items. It is the same figure the page already shows as "adjusted" spending (`budget.adjusted.exp`).
   - **Missing or zero budget:** a budget that is missing, zero or less is never used. With other years as the reference, only the median bounds apply. With no other year, the status is `denominator_no_reference`. In the local build, 17 shown shares have no ADJB row (15 of them have only an original budget, ORGB; ORGB is not used).
   - **Bounds:** "under 50%" is computed as "audited spending × 2 < reference"; "over 2.5 times" as "audited spending × 2 > reference × 5". Both are exact integer arithmetic. Exactly 50% and exactly 2.5 times pass.
   - **Why the reference uses 2020 to 2024 only:** 2018 and 2019 are the years found to be incomplete, so they would pull the median down and weaken the check. "Other years" means that a year is never compared with itself. The median (not the mean) means one bad other year does not hide a normal year. The median of an even count can end in .5 cent, so `denom_ref_median` is a DECIMAL in cents, and the rule is computed exactly as "audited spending × 2 < median".
3. **National share** (decision): `fw_total_cents` is the sum of **every** known municipal F&W amount, hidden shares included. The share uses **only** municipality-years whose own status is `ok`. A municipality-year whose share is hidden is **left out of both parts**: its F&W is not in `fw_share_base_cents`, and its audited spending is not in `denom_share_base_cents`. `n_share_hidden` counts these rows. `national_share_status` is `denominator_incomplete_year` for 2018 and 2019 (no national share), `no_base` when no row is `ok`, and otherwise `ok`. Reason: adding a hidden row's F&W without its spending (or the other way round) would make the national share wrong in the same way as the hidden row.
4. **Constants** in `thusa/fw_metric.py`: the year range (2018, 2024), the first share year (2020), the 50% and 2.5 ratios (`FW_REF_MIN_RATIO`, `FW_REF_MAX_RATIO`), the status codes (`SHARE_STATUS`, `GUARD_STATUS`, `NATIONAL_STATUS`), the check bases (`CHECK_BASIS`) and the 4 decimal places. A test keeps the SQL numbers equal to them.
5. **Data-quality checks** in `thusa/dq.py` (`fw_checks`, part of every build). Errors: unique rows; years in range; valid status; share only when the status is `ok`; status matches the inputs; **no share for 2018 and 2019**; **2018 and 2019 rows with both figures have `denominator_incomplete_year`**; **the stored reference equals a fresh recomputation from the mart**; **the stored adjusted budget equals the ADJB source row** (`fw_budget_matches_source`); **the completeness rule (both bounds, the budget bound and the budget fallback) gives the stored status and check basis** (`fw_completeness_rule`); **no check basis before 2020** (`fw_check_basis_only_from_2020`); share matches the inputs exactly under the cut rule; no share over 100; change equals the prior-year difference; every F&W line in range is in the mart; the yearly sums equal the source to the cent (T3); the national table equals the mart (totals, counts, hidden count and both share bases); the national share rule; lineage present and resolving (also for the denominator). Warnings (reported, never a build failure): `fw_share_guarded_info` (2020–2024 shares hidden by the completeness rules, `denominator_implausible_high` included) and `fw_agsa_reconcile_info` (T2: the real number of rows outside R50,000.00; before this fix it showed 0 unless more than 2% were outside). `MIN_ROWS` adds `marts.fw_metric` ≥ 1,000.
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

1. **Completeness check:** 50% of the median of the other years 2020–2024, as the reviewer asked. **Reviewer's answer (22de78d8 review): the median uses 2019/20 to 2023/24 only.**
2. **One comparison year is enough** (reviewer's answer). For example !Kai! Garib 2020/21 is compared with one other year.
3. **High bound** (reviewer's request, 22de78d8 review): over 2.5 times the median of the other years, or over 2.5 times that year's adjusted budget. The thresholds are the reviewer's. They were not tuned to the data (see the extra catch, Merafong City 2023/24).
4. **No reference year:** compare with that year's adjusted budget, with the same 50% and 2.5 times bounds (option 2 of the review, taken because it was clean: 4 rows change, all explained above). Hidden as `denominator_no_reference` only when the budget is also missing, zero or less.
5. **No sort in Phase 1** (reviewer's answer). Alphabetical only. A "largest first" order is a later owner decision.
6. **No amounts-only view for 2011/12 to 2016/17 now** (reviewer's answer).
7. **`share_over_100`** stays as an explicit fallback status. In the local build, all 8 former over-100% cases are caught before it: 6 by `denominator_incomplete_year` and 2 (Mogale City 2021/22, Renosterberg 2022/23) by `denominator_incomplete`. A test covers each kind.
8. **National share:** hidden municipality-years, `denominator_implausible_high` included, are left out of both parts (see "National share").
9. **No AGSA figures.** The AGSA cross-check runs only as a warning (T2).
10. **Change from the year before** is in cents and is NULL when either year is unknown. 2017/18 has no prior year in this view.

## Deviations from the draft RFC

- Branch name `chg-2026-062-fw-expenditure` (the draft had `feat/chg-2026-062-fw-metric`), as the task asked.
- No `agsa_fw_cents` / `agsa_diff_cents` columns and no `source_url` column in the mart. The URL resolves through `ops.raw_file` and the export's `sources`.
- No share for 2017/18 and 2018/19, the completeness check, the high bound and the budget fallback are new (review findings).
- The new municipality chart shows the share only. The existing UIF&W bar chart already shows the amounts.
- No `config/public-data.yaml` text change. The explanation is in the `about` lines of `municipalities.json` and on the page.
- The "under 0.0001%" text is new.
- No preview build, no TEST step and no axe scan yet (see "Pending for TEST").

## Testing (evidence, not claims)

- `uv run pytest -q` in the worktree (no warehouse), commit 3: **946 passed, 85 skipped, 0 failed** (commit 2: 924 passed, 83 skipped; baseline on `ceabf99`: 865 passed, 61 skipped). The 24 more skips are the new checks in `tests/test_dq_warehouse.py`, which run only against a real warehouse. The 81 tests in `tests/test_fw_metric.py` cover:
  - T1: each status, no divide by zero, 0 stays 0, cut-not-round cases (2/3 cents gives 66.6666; 0.00005 and 0.0000625 give 0.0000; 0.00015 gives 0.0001), 100% kept, the `share_over_100` fallback, no overflow with very large amounts;
  - 2018 and 2019 keep the amount and never have a share; a missing figure is reported before the year reason;
  - no reference year (Kopanong-like case; 2019, zero and negative years are no reference);
  - the 50% rule at its edges (49 hidden, exactly 50 shown; even-count median 150: 74 hidden, 75 shown), a Merafong-like case (4%), and one low other year that does not hide a normal year;
  - every kind of former over-100% case is hidden;
  - the high bound: exactly 2.5 times passes, over 2.5 times the median is hidden, a Kagisano-Molopo-like case, over 2.5 times the budget only is hidden, exactly 2.5 times the budget passes, a zero, negative or missing budget is not used, and the low bound still uses the other years;
  - the budget fallback: a Kopanong-like case is shown with basis `adjusted_budget`; exactly 50% and exactly 2.5 times pass; under 50% and over 2.5 times are hidden; a zero, negative or missing budget keeps `denominator_no_reference`; no basis before 2020;
  - a `denominator_implausible_high` row is in the national total but out of both share bases;
  - national share: a hidden row is in the total but out of both share bases; no national share for 2019; `no_base`;
  - years 2017 and 2025 and non-municipal bodies left out; change uses the prior year only;
  - T4: the mart never reads irregular or unauthorised rows; the export adds only `share_pct`, `status` and `change`;
  - each data-quality check passes on a clean mart that has every status, and fails on a broken one (18 tamper cases, including the year, completeness, reference, budget, check-basis and national checks);
  - the AG warning reports the real count (1 mismatch in 60 rows gives 1; the old 2% gate gave 0; a gap of exactly R50,000.00 is accepted);
  - the synthetic full build has the mart and its checks pass; the export has plain numbers, no share before 2020, and passes the public-safety scan;
  - page: route, menu and `dashboard_check` mirror; one sort only, alphabetical by name; no ranking words; neutral wording; no irregular or unauthorised field in the new code; central formatters only; the left-out years are stated; every hidden-share reason and national status has page text; the JS share text and axis ticks run in node.
  - The owner-quote and name guard tests pass.
- **Real-data check (read-only).** The new SQL and the full data-quality suite were run on a **fresh copy** of the local warehouse, build B20261115T155921Z (the local build of 15 Nov 2026, not the live nightly). The copy was deleted afterwards. Nothing in `/workspace/publicfunds` changed, and nothing was published.
  - Data-quality suite on the copy (commit 3): **80 pass, 2 warn, 0 fail.** Warnings: `award_buyer_match_rate_info` (207, as before) and `fw_share_guarded_info` (15; commit 2: 14). `fw_agsa_reconcile_info` is **0** (pass): 226 of 226 linked municipalities for 2023/24 are within R50,000.00. The raw-file checksum check was not run on the copy.
  - T3: the yearly F&W sums in the mart equal the source lines to the cent (check passes).
  - `marts.fw_metric` has 1,799 rows; `marts.fw_national` has 7. Statuses (commit 3): `ok` 1,199; `denominator_incomplete_year` 458; `denominator_unknown` 114; `denominator_not_positive` 13; `denominator_incomplete` 12; `denominator_implausible_high` 3; `denominator_no_reference` 0; `share_over_100` 0. (Commit 2: `ok` 1,200; `denominator_incomplete` 10; `denominator_no_reference` 4.)
  - Shares hidden by the completeness rules (2019/20–2023/24), commit 3: 2019/20 Dr Beyers Naudé, Mafikeng (incomplete), Ntabankulu (implausible high); 2020/21 !Kai! Garib, Siyathemba (incomplete), Nala (incomplete, against the budget); 2021/22 Merafong City, Mogale City, Tokologo, Tswaing (incomplete); 2022/23 Renosterberg (incomplete), Masilonyana (incomplete, against the budget); 2023/24 Ratlou (incomplete), Kagisano-Molopo, Merafong City (implausible high). Now shown: Mantsopa 2022/23 and Kopanong 2023/24 (budget fallback).
  - National view:

  | Year | F&W, all municipalities | With a share | Share not available | F&W in the share base | Audited spending in the share base | Share of audited spending |
  |---|---|---|---|---|---|---|
  | 2017/18 | R2,146,762,816.00 | 0 | 257 | not used | not used | not available |
  | 2018/19 | R3,783,551,069.00 | 0 | 257 | not used | not used | not available |
  | 2019/20 | R4,080,800,600.00 | 237 | 20 | R3,778,206,262.00 | R409,818,711,485.00 | 0.9219% |
  | 2020/21 | R1,959,230,789.00 | 240 | 17 | R1,544,896,574.00 | R399,974,245,289.00 | 0.3862% |
  | 2021/22 | R4,915,853,360.00 | 241 | 16 | R3,775,860,997.00 | R425,333,809,781.00 | 0.8877% |
  | 2022/23 | R7,471,621,788.00 | 238 | 19 | R6,984,583,221.00 | R493,575,435,779.00 | 1.4150% |
  | 2023/24 | R5,266,773,348.00 | 243 | 14 | R4,573,584,423.00 | R550,989,000,403.00 | 0.8300% |

  Commit 2 had 2019/20 0.9212% (238 shown, 19 not), 2022/23 1.4126% (237, 20) and 2023/24 0.8343% (244, 13). 2020/21 and 2021/22 do not change.

- `scripts/dashboard_check.py` with a `municipalities.json` made from the copy (put in the worktree for the check only, then restored with `git checkout`): **0 problems**, desktop and mobile, the new page included (run again for commit 3: 0 problems; Kagisano-Molopo and Merafong City 2023/24 show "not available", Kopanong 2023/24 shows 16.4077%). Merafong City shows "not available" for 2017/18, 2018/19, 2020/21 (audited spending below zero) and 2021/22. axe was not run (not installed).
- `municipalities.json` from the copy is 1,645,019 bytes for commit 3 (commit 2: 1,644,551 bytes (now 1,525,551; file budget 2,000,000). The total of all files stays under the 5,000,000-byte budget.

## Pending for TEST (before the owner GO)

1. **T5, by hand:** check these rows against the municipality's audited financial statements (AFS), first: **Naledi (NW) 2019/20 (47.7615%)**, **Maluti-a-Phofung 2019/20 (27.4263%)**, **Ugu 2019/20**, **Albert Luthuli 2019/20**, **Kgetlengrivier 2022/23** and **Lekwa 2022/23**. Then the 10 largest shares in each year from 2019/20 to 2023/24 (including Kopanong 2023/24, 16.4077%, now shown through the budget fallback). Record each result here. A year or a row that fails stays hidden. The reviewer's check against the source API (not the AFS) matched for 9 rows.
2. **axe accessibility scan** of the new page with `scripts/dashboard_check.py` (axe-core is not installed on this computer).
3. A preview build and a check of the page by the reviewers.

## Risk assessment

| Risk | L | I | Score | Mitigation |
|---|---|---|---|---|
| Readers read F&W as theft or corruption, or add it to irregular expenditure (RSK-022) | 3 | 3 | 9 | Definitions and caveats on the page; "not proof of theft or corruption"; no combined total; tests T4 and T7 |
| A list reads as an accusation against a named body (RSK-023) | 2 | 4 | 8 | Alphabetical order only; no ranking; official figures only; no officials named; doubtful shares hidden |
| An incomplete denominator gives a wrong share | 2 | 4 | 8 | No share for 2017/18 and 2018/19; completeness check for later years; hidden rows out of the national base; T5 by hand before the GO |
| The completeness check hides a correct share, or misses a wrong one within the 50% to 2.5 times bounds | 2 | 2 | 4 | Hidden rows are counted in a warning and listed here (one known over-hide: Merafong City 2023/24); T5 by hand on the top shares |
| The adjusted budget used as a check is itself wrong or incomplete | 2 | 2 | 4 | It is only a check, never a share base; the low bound uses the budget only when there is no other year; 4 rows depend on the fallback, all listed |
| The source amount is a balance, not the year's spending | 3 | 2 | 6 | Caveat on the page; the source does not say (as in `040_uifw_line.sql`) |
| The public-data size budget gets closer to its limit | 2 | 2 | 4 | About +119 KB; the export refuses to write over budget |

- Does it change which suppliers or people are flagged publicly? **No.**
- **POPIA:** public bodies at entity level only. No natural person, no official, no ID, no contact detail. popia-review verdict: **PASS** (nothing found; nothing removed). The repo text names no owner account, agent or bot, and quotes no owner words.
- Licence: the same Municipal Money data the site already shows.

## Implementation plan

1. DEV (done): local branch from `ceabf99`, code, tests, records, real-data check on a warehouse copy; review fixes in commits 2 and 3.
2. TEST: the items in "Pending for TEST".
3. Review: two independent reviewer PASSes on the exact head, then the owner's own GO naming that head. A new head needs new reviews.
4. Push and PR only after the owner approves that step.
5. After a merge: tag `snapshot-YYYY-MM-DD-HHMM` (SAST), run `scripts/check_live.py`. The next nightly rebuilds and publishes the new fields.

## How to revert

- Before merge: `git worktree remove /workspace/pf-chg062` and `git branch -D chg-2026-062-fw-expenditure`. Nothing is published.
- After merge: `git revert -m 1 <merge commit>`, then a PR with reviews and the owner's GO. The next nightly then writes `municipalities.json` without the `fw` fields. The mart is rebuilt from nothing on every run, so there is no migration to undo.

## Open questions for the owner

- Q1 to Q3 of commit 2 are answered (see "Decisions made in this build", items 1, 2, 5 and 6).
- **Q4:** Merafong City 2023/24 is hidden by the median bound (2.592 times) because its own incomplete 2021/22 figure lowers its median. Keep it hidden (this build), or leave years that fail the low bound out of the median? Changing the rule needs a new commit and a new review.

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
- Outcome: pending (DEV only). Commit `180154f7`: reviewer FAIL (incomplete denominators), fixed in commit 2. Commit `22de78d8`: reviewer PASS_WITH_CONCERNS (too-high denominators), fixed in commit 3.
