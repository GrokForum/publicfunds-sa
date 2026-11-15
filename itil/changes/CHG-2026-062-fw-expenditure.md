# CHG-2026-062: Fruitless and wasteful expenditure metric, Phase 1 (municipalities)

| Field | Value |
|---|---|
| Requested by / date (SAST) | The owner, 15 Nov 2026, as reported to the author (PublicFunds): news reports often quote fruitless and wasteful expenditure, so it is a useful metric if the data exists. Owner GO for **Phase 1 only**, as reported to the author (PublicFunds) by the orchestrator, 16 Nov 2026 00:49 SAST. That GO covers building Phase 1 on a local branch. It is not a merge GO. Exact words are in the private approval record, not in this repo. |
| Status | DEV only. Local branch `chg-2026-062-fw-expenditure` from `ceabf99`. Not pushed. No PR. Nothing on `main`. |
| Type | **Normal-medium.** A new mart, new export fields and a new page, all from data that is already in the warehouse. No new source, no download, no detector, no change to `config/publication.yaml` or to the publishing pipeline. |
| Environment | DEV (the worktree of the author's computer). TEST and PROD need their own steps (see "Implementation plan"). |
| CIs affected | `thusa/models/marts/110_fw_metric.sql` (new, CI-115); `thusa/fw_metric.py` (new); `thusa/dq.py` (new checks); `thusa/build.py` (row counts); `thusa/publish_data.py` (municipalities.json fields); `apps/public-dashboard/index.html` (new page `#/fw` and a section on each municipality page); `scripts/dashboard_check.py` (route and page mirror); `tests/test_fw_metric.py` (new); this record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md` |
| Linked records | CHG-2026-057 and CHG-2026-059 (number format), RSK-022 (public misreading), RSK-023 (defamation), KE-008 (totals summed from line items) |
| Rollback point | `ceabf99` (tag `snapshot-2026-11-15-pr1-4-10`) |
| Rollback | Before merge: delete the branch and the worktree. After merge: `git revert -m 1 <merge commit>`. Git is the rollback; no .bkp files. |

## Goal

Show fruitless and wasteful (F&W) expenditure for each municipality as a **share of its audited spending**, as a trend from 2017/18 to 2023/24, and as a national view. This turns one headline number into figures that a reader can check, each with its source.

## Scope

In scope (Phase 1, approved to build):
- Municipalities only. Data already in the warehouse: Municipal Money `uifwexp` (F&W amounts, `curated.uifw_line`) and audited actual totals (`curated.muni_total`, amount type AUDA).
- Financial years ending 2018 to 2024 (2017/18 to 2023/24).

Out of scope:
- **Years ending 2012 to 2017.** They are left out until a manual spot check (test T5) passes. The page says so.
- **Phase 2** (national and provincial departments and public entities, AGSA PFMA annexures) and **Phase 3** (2024/25 from the AGSA PDF annexure). These are **not approved**. No AGSA figure is exported by this change.
- A ranking, a "largest first" order or a top-10 list (owner decision D2, not given).

## What changed

1. **New mart** `thusa/models/marts/110_fw_metric.sql`:
   - `marts.fw_metric`: one row for each municipality and year (2018 to 2024) that has an F&W amount or an audited spending figure. Columns: `fw_cents`, `denom_cents` (audited total operating expenditure), `denom_basis` (`audited_total_expenditure`), `denom_derivation` (published subtotal or sum of line items, KE-008), `share_status`, `fw_share_pct`, `fw_prev_cents`, `fw_change_cents`, and lineage (`source_id`, `source_file`, `source_sha256`, `fetched_at_utc`, `source_locator`, `denom_source_sha256`).
   - `marts.fw_national`: one row for each year. `fw_total_cents` is the sum of all known municipal F&W amounts. `national_share_pct` is the F&W sum divided by the audited spending sum, over the municipalities whose `share_status` is `ok` only. The two bases are kept in separate columns (`fw_share_base_cents`, `denom_share_base_cents`).
2. **Share rule** (a documented calculation, as CHG-2026-057 requires):
   - share = F&W ÷ audited spending × 100, in percentage points;
   - it is **cut** (truncated toward zero) to 4 decimal places with integer arithmetic. **Nothing is rounded**, so a half is never rounded up;
   - `share_status` tells why a share is not available: `fw_unknown`, `denominator_unknown`, `denominator_not_positive` (zero or less: no divide by zero) or `share_over_100` (see "Decisions made in this build"). Only `ok` has a share. "Not available" is never 0. A known 0 F&W amount gives a 0 share.
   - a very small non-zero amount can cut to 0.0000. The page then shows "under 0.0001%", never 0%.
3. **Constants** in `thusa/fw_metric.py`: the year range (2018, 2024), the status codes and the 4 decimal places. A test keeps the SQL and Python year range equal.
4. **Data-quality checks** in `thusa/dq.py` (`fw_checks`, part of every build). Errors: unique rows, years in range, valid status, share only when the status is `ok`, status matches the inputs, share matches the inputs exactly under the cut rule, no share over 100, change equals the prior-year difference, every F&W line in range is in the mart, the yearly sums equal the source to the cent (T3), the national table equals the mart, lineage present and resolving (also for the denominator). Warnings (reported, never a build failure): `fw_share_over_100_info` and `fw_agsa_reconcile_info` (T2, see Testing). `MIN_ROWS` adds `marts.fw_metric` ≥ 1,000.
5. **Export** (`public-data/v1/municipalities.json`, after a merge and the next nightly): each year from 2018 to 2024 gets `fw: {share_pct, status, change}`. The file gets `fw_years` and `fw_national`, and plain-language `about` lines. The amounts were already in `uifw.fruitless_wasteful` and `audited.exp`; they are not copied. Numbers stay plain decimals (the share is a JSON number such as `0.187`).
6. **Page** (`apps/public-dashboard/index.html`):
   - new menu item and page **Fruitless & wasteful** (`#/fw`): the definitions and caveats, a national trend line of the share, a national table per year, and a table of all municipalities for a chosen year and province, **in alphabetical order only** (not a ranking), with a CSV download;
   - each municipality page gets a section under the existing UIFW table: a trend line of the share and a table with the amount, audited spending, share, change from the year before and source;
   - only the central formatters are used: R1,234,567.89 in tables, -R1,234.50 for negative changes, the share at its stored precision (0.187%, 5.07%), counts as 1,234;
   - F&W is never added to irregular or unauthorised expenditure. The page says that F&W is not proof of theft or corruption.
7. `scripts/dashboard_check.py`: the new route and page are added to its mirrors, so the headless check opens the page.

## Stays the same

- All sources, connectors and raw files. All curated tables. The coverage model and the coverage numbers.
- Detectors, flags, review rules and `config/publication.yaml`. No detector reads `marts.fw_metric`.
- The existing UIFW section of the municipality page (chart and table) is unchanged. It still shows all loaded years, as before.
- All existing fields in `municipalities.json`. Nothing is removed or renamed.

## Decisions made in this build (please check)

1. **`share_over_100`.** On the local warehouse, 8 municipality-years have an F&W amount larger than audited spending (5 in 2017/18, 1 each in 2018/19, 2021/22 and 2022/23). Most have a denominator summed from a few line items (for example R35,126.00 of audited spending for a whole year). The share would read as more than 1,000% in some cases. This build hides those shares ("not available") and counts them in a warning. It does not hide shares from 25% to 100%. The 100% limit is the author's choice, not an owner decision.
2. **No AGSA figures.** The draft RFC put AGSA cross-check columns in the mart and an AGSA headline quote beside the national view. Both are left out, so Phase 1 exports no AGSA-sourced figure. The cross-check runs only as a warning (T2).
3. **The share uses `ok` rows only** for the national figure. The F&W total uses every known amount. The page and the data file name both bases.
4. **Change from the year before** is in cents and is NULL when either year is unknown. 2017/18 has no prior year in this view.

## Deviations from the draft RFC

- Branch name `chg-2026-062-fw-expenditure` (the draft had `feat/chg-2026-062-fw-metric`), as the task asked.
- No `agsa_fw_cents` / `agsa_diff_cents` columns and no `source_url` column in the mart. The URL resolves through `ops.raw_file` and the export's `sources`.
- The new municipality chart shows the share for 2017/18 to 2023/24 only, not F&W amounts for 2011/12 to 2023/24. The existing UIFW bar chart already shows the amounts.
- No `config/public-data.yaml` text change. The explanation is in the `about` lines of `municipalities.json` and on the page.
- `share_over_100` and the "under 0.0001%" text are new (see above).
- No preview build, no TEST step and no axe scan yet (axe-core is not installed on this computer).

## Testing (evidence, not claims)

- `uv run pytest -q` in the worktree (no warehouse): **905 passed, 78 skipped, 0 failed** (baseline before this change on `ceabf99`: 865 passed, 61 skipped). The 17 more skips are the new checks in `tests/test_dq_warehouse.py`, which run only against a real warehouse. The 40 new tests are in `tests/test_fw_metric.py`:
  - T1: each status, no divide by zero, 0 stays 0, cut-not-round cases (2/3 cents gives 66.6666; 0.00005 and 0.0000625 give 0.0000; 0.00015 gives 0.0001), 100% kept and 101% hidden, no overflow with very large amounts;
  - years 2017 and 2025 and non-municipal bodies left out; change uses the prior year only; national sums and share;
  - T4: the mart never reads irregular or unauthorised rows; the export adds only `share_pct`, `status` and `change`;
  - each new data-quality check passes on a clean mart and fails on a broken one (8 tamper cases);
  - the synthetic full build has the mart and its checks pass; the export is plain numbers and passes the public-safety scan;
  - page: route, menu and `dashboard_check` mirror; one sort only, alphabetical by name; no ranking words; neutral wording; no irregular or unauthorised field in the new code; central formatters only; the left-out years are stated; the JS share text and axis ticks run in node.
  - The owner-quote and name guard tests pass.
- **Real-data check (read-only).** The new SQL and checks were run on a **copy** of the local warehouse, build B20261115T155921Z (the local build of 15 Nov 2026, not the live nightly). Nothing in `/workspace/publicfunds` changed, and nothing was published.
  - Data-quality suite on the copy: **73 pass, 2 warn, 0 fail.** Warnings: `award_buyer_match_rate_info` (207, as before) and `fw_share_over_100_info` (8). The raw-file checksum check was not run on the copy.
  - T2 (warning only): for 2023/24, 226 municipalities linked to AGSA MFMA Annexure 1 (financial audits) have both values. 226 of 226 are within R50,000.00 (AGSA shows R million); 37 are equal.
  - T3: the yearly F&W sums in the mart equal the source lines to the cent (check passes).
  - `marts.fw_metric` has 1,799 rows; `marts.fw_national` has 7.

  | Year | F&W, all municipalities | With an amount | With a share | Share of audited spending |
  |---|---|---|---|---|
  | 2017/18 | R2,146,762,816.00 | 257 | 223 | 0.5075% |
  | 2018/19 | R3,783,551,069.00 | 257 | 229 | 1.2255% |
  | 2019/20 | R4,080,800,600.00 | 257 | 240 | 0.9271% |
  | 2020/21 | R1,959,230,789.00 | 257 | 243 | 0.386% |
  | 2021/22 | R4,915,853,360.00 | 257 | 244 | 0.9097% |
  | 2022/23 | R7,471,621,788.00 | 257 | 239 | 1.4149% |
  | 2023/24 | R5,266,773,348.00 | 257 | 246 | 0.8505% |

- `scripts/dashboard_check.py` with a `municipalities.json` made from the copy (put in the worktree for the check only, then restored with `git checkout`): **0 problems**, desktop and mobile, the new page included. axe was not run (not installed).
- `municipalities.json` from the copy is 1,632,402 bytes (now 1,525,551; file budget 2,000,000). The total of all files stays under the 5,000,000-byte budget (about 4.49 MB).
- **T5 (manual spot check) is not done.** It is a reviewer task before a merge.

## Risk assessment

| Risk | L | I | Score | Mitigation |
|---|---|---|---|---|
| Readers read F&W as theft or corruption, or add it to irregular expenditure (RSK-022) | 3 | 3 | 9 | Definitions and caveats on the page; "not proof of theft or corruption"; no combined total; tests T4 and T7 |
| A list reads as an accusation against a named body (RSK-023) | 2 | 4 | 8 | Alphabetical order only; no ranking; official figures only; no officials named |
| An incomplete denominator gives a wrong share | 3 | 3 | 9 | Shares over 100% hidden and counted; denominator derivation kept; T5 spot check before merge; open question Q2 |
| The source amount is a balance, not the year's spending | 3 | 2 | 6 | Caveat on the page; the source does not say (as in `040_uifw_line.sql`) |
| The public-data size budget gets closer to its limit | 2 | 2 | 4 | About +107 KB; the export refuses to write over budget |

- Does it change which suppliers or people are flagged publicly? **No.**
- **POPIA:** public bodies at entity level only. No natural person, no official, no ID, no contact detail. popia-review verdict: **PASS** (nothing found; nothing removed). The repo text names no owner account, agent or bot, and quotes no owner words.
- Licence: the same Municipal Money data the site already shows.

## Implementation plan

1. DEV (done): local branch from `ceabf99`, code, tests, records, real-data check on a warehouse copy.
2. Review: two independent reviewer PASSes on the exact head, then the owner's own GO naming that head. A new head needs new reviews.
3. Push and PR only after the owner approves that step.
4. After a merge: tag `snapshot-YYYY-MM-DD-HHMM` (SAST), run `scripts/check_live.py`. The next nightly rebuilds and publishes the new fields.

## How to revert

- Before merge: `git worktree remove /workspace/pf-chg062` and `git branch -D chg-2026-062-fw-expenditure`. Nothing is published.
- After merge: `git revert -m 1 <merge commit>`, then a PR with reviews and the owner's GO. The next nightly then writes `municipalities.json` without the `fw` fields. The mart is rebuilt from nothing on every run, so there is no migration to undo.

## Open questions for the owner

- **Q1 (D2):** keep alphabetical only (this build), or allow a "largest first" order later? Not in Phase 1.
- **Q2:** is hiding shares over 100% the right rule? Should more be hidden (for example where the denominator is summed from line items and is much smaller than the next year's)? In 2017/18 and 2018/19 the national audited-spending base is R275.7 bn and R261.6 bn, against R411.2 bn in 2019/20, so many denominators in those two years look partial.
- **Q3 (D4):** after T5, show 2011/12 to 2016/17?
- **Q4:** the existing UIFW section still shows amounts for 2011/12 to 2016/17, as before this change. Keep it as it is?

## Seen, not touched

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
- Outcome: pending (DEV only).
