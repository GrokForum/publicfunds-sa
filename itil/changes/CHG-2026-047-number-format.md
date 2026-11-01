# CHG-2026-047: Comma thousands and point decimals on every public page; plain decimals in data

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner, 2026-11-01 20:37, as reported to the author (PublicFunds) |
| Environment | Public dashboard (`apps/public-dashboard/index.html`), its Python mirror (`thusa/coverage_ceiling.py`), `scripts/dashboard_check.py`, tests. No pipeline, detector or data change |
| Type | Normal-medium. See "Tier" |
| CIs affected | `apps/public-dashboard/index.html`, `thusa/coverage_ceiling.py`, `scripts/dashboard_check.py`, `tests/test_number_format.py` (new), `tests/test_unknowns_by_type_constant.py`, `tests/test_improvements.py`, `itil/registers/change-log.md`, this file |
| Linked records | Old-repo PR #46 (first version, decimal comma; replaced by this PR under CHG-2026-050), CHG-2026-046 (this PR is based on it) |
| Rollback | Close the PR. If the PR is merged, run `git revert -m 1 <merge commit>` |

## Decision

Owner decision for old PR #46, 1 Nov 2026 20:37 SAST, as reported to the author (PublicFunds): show 1,000,000.00 on screen and keep plain decimal points in data. Exact words are in the private approval record.

This decision supersedes the first version of CHG-2026-047. The first version used a decimal comma on the home page. That version is withdrawn. No decimal comma is used on a public page after this change.

## Tier

Normal-medium. The change alters how every public page shows numbers. It needs the owner and a second reviewer. A bot approval never fills a human slot. No reviewer PASS in this record is owner approval.

## Rules

1. Screen rule. On every public page, a number has a comma thousands separator and a point decimal. Examples: 1,000,000.00, R1,000,000.00, 75.7%, 1,167 of 1,285.
2. Data rule. JSON, CSV and data files keep plain point decimals with no thousands separator. This change does not change any data file.

## Change

1. The page has one number locale, `NUM_LOCALE = "en-US"`. All number helpers (`randText`, `randFull`, `num`, `pct`, new `intg`) use it. The SAST date keeps `en-ZA`, because a date shows no decimals.
2. The two decimal-comma helpers (`dec` in the by-type model, `tenths` in the headline context) now give a point decimal. These two functions use the literal `"en-US"`, because the parity test runs them alone.
3. File sizes on the sources page use `intg` (for example "1,234 KB"), not `toFixed(0)`.
4. Counts in the headline, the headline context lines, the report card, the table row counts and the leads count use `intg` (for example "1,167 of 1,285").
5. The glossary limits are written R750,000, R300,000, R200,000 and R1,000,000. The HHI limit is written 2,500.
6. The Python mirror gives the same text: `dec` gives "1,234.6", the context lines give "90.8% (1,167 of 1,285 municipality-years)".
7. `scripts/dashboard_check.py` scans the text of every public page, on desktop and mobile. It fails on a decimal comma (for example 90,8) and on space thousands (for example 1 000). Text that the page quotes word for word from the manifest (known gaps, known errors, source names) is skipped. The scan does not apply to the footer phone number, which is outside the page view.

## Not changed

- `thusa/review/casepack.py` still writes "R750 000" and "2 500". The case pack is a reviewer file, not a public page. A separate change can align it.
- CSV export: columns shown with `num`, `randFull`, `randText` or `intg` already give the CSV a plain value (`csvValue`). Three share columns give the CSV a whole percent (for example "45%"), with no separator. This is unchanged.

## Testing

- `uv run pytest`: 766 passed, 61 skipped (CHG-2026-046 second head: 757 passed, 61 skipped).
- Skip count. The first head gave 762 passed, 62 skipped on a machine without Playwright: `test_dashboard_check_number_scan` loaded `scripts/dashboard_check.py`, which imported Playwright at the top, and the test skipped on ImportError. Fix: the script imports Playwright inside `main()` (CHG-2026-046 second head), and the test no longer skips. The node test now follows the repo's node policy: it fails without node, and skips only with `PF_SKIP_NODE_PARITY=1`. The 61 remaining skips are the same as on main; they need a built warehouse or fuel source files in `data/`.
- New `tests/test_number_format.py`, 9 tests (the 9th: file sizes on the sources page use comma thousands):
  - Screen rule: page helpers in node give "1,000,000.00", "R1,000,000.00", "75.7%", "1,167"; no decimal comma and no `en-ZA` number locale in the page; no space thousands in page text; the Python mirror gives the same format; the dashboard_check scan finds a decimal comma and space thousands and skips verbatim data text.
  - Data rule: no string in a `public-data/v1/*.json` file is a number with a thousands separator or a decimal comma; the same for any CSV under `public-data/` (none are tracked today, so this test guards future files); a page column shown in screen format gives the CSV a plain value.
- `uv run --group screenshots python scripts/dashboard_check.py`: `"problems": []`.
- POPIA guard `tests/test_popia_names.py`: pass.

## Risk

Low to medium. South African readers often see a decimal comma. The owner chose the point decimal. A reader can misread a number if one page keeps the old format; the dashboard_check scan stops this. No data value changes.

## How to revert

`git revert -m 1 <merge commit>`, then run `uv run pytest` and `scripts/dashboard_check.py`.
