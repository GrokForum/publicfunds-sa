# CHG-2026-046: Label the projection line "Projection, not data" wherever it is shown

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner, 2026-11-01 20:37, as reported to the author (PublicFunds) |
| Environment | Public dashboard (`apps/public-dashboard/index.html`), its Python mirror (`thusa/coverage_ceiling.py`), `scripts/dashboard_check.py`, tests. No pipeline, detector or data change |
| Type | Normal-medium. See "Tier" |
| CIs affected | `apps/public-dashboard/index.html`, `thusa/coverage_ceiling.py`, `scripts/dashboard_check.py`, `tests/test_unknowns_by_type_constant.py`, `tests/test_projection_label.py` (new), `itil/registers/change-log.md`, this file |
| Linked records | Old-repo PR #45 (this change, first version; replaced by this PR under CHG-2026-050), CHG-2026-034, CHG-2026-047 |
| Rollback | Close the PR. If the PR is merged, run `git revert -m 1 <merge commit>` |

## Decision

Owner decision for old PR #45, 1 Nov 2026 20:37 SAST, as reported to the author (PublicFunds): fix the labels on a new head, then run both review passes. Exact words are in the private approval record.

## Tier

Normal-medium. The change alters public wording. It needs the owner and a second reviewer. A bot approval never fills a human slot. No reviewer PASS in this record is owner approval.

## Change

1. The projection line under the headline now starts with "Projection, not data: ". The old start, "Prediction, not a result: ", is removed. The Python mirror has the same change.
2. The gap note marks each projection line with `data-kind="projection"`.
3. Fix for the second reviewer's FAIL on the first version: the coverage page and the report card now also show the projection line, with the same label and mark. The home page still shows all context lines. The coverage page and the report card show the projection line only.
4. `scripts/dashboard_check.py` checks the projection line on all three places (home, coverage page, report card), on desktop and mobile. It fails if the line is missing, if the line has no label, or if the line has no projection mark.
5. Review fix (second head): the check no longer passes in silence when the data has no projection line. `projection_status()` decides from `coverage.json` alone whether a line is expected (the year after the headline window is in `by_year` with `all_core_due` false, and the window has a gap year). If a line is expected and the page or the reference gives none, the check fails. If no line is expected, the check writes the reason ("SKIP projection check: ...") to `checks.<viewport>_projection` in its output.
6. `dashboard_check.py` now imports Playwright inside `main()`. Tests can load the module without the screenshots group, so these tests never skip for a missing Playwright.

This change does not change the number format. CHG-2026-047 changes the number format. The two PRs touch the same lines in `tests/test_unknowns_by_type_constant.py` and `thusa/coverage_ceiling.py`. Merge this PR first. Then rebase CHG-2026-047 only on owner GO.

## Testing

- `uv run pytest`: 757 passed, 61 skipped (main: 750 passed, 61 skipped). The 61 skips are the same as on main: they need a built warehouse or fuel source files in `data/`.
- New `tests/test_projection_label.py`: 7 tests (projection_status on real and changed data, fail-when-absent wiring, label in the Python mirror, old label gone, three gap notes get the labelled line, projection mark, dashboard_check covers three places).
- `uv run --group screenshots python scripts/dashboard_check.py`: `"problems": []`; `desktop_projection` and `mobile_projection` read "projection line expected".
- POPIA guard `tests/test_popia_names.py`: pass.

## Risk

Low. Wording and markup only. The numbers do not change. If the label is wrong, a reader can take a projection for data. The check and the tests stop this.

## How to revert

`git revert -m 1 <merge commit>`, then run `uv run pytest` and `scripts/dashboard_check.py`.
