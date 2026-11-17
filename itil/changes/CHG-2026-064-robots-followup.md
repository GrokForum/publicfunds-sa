# CHG-2026-064: Follow-up to the review of CHG-2026-063 (records; robots.txt variant A chosen)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Follow-up to a reviewer PASS_WITH_CONCERNS on PR #12 (CHG-2026-063), 17 Nov 2026, as reported to the author (PublicFunds). This record is not a merge GO. |
| Status | Built in DEV on branch `chg-2026-064-robots-followup` from `main` `de37f666` (tag `snapshot-2026-11-17-1129`). Commits: `e532110` and `1742336b` (commit A: records, robots.txt unchanged), `ea449394` (commit B: robots.txt variant B), `b3cb0ea8` (revert of commit B), then this record update. The branch result is variant A. Draft PR #14 was opened 17 Nov 2026 11:51 SAST by the orchestrator at head `cecd6503`. |
| Decision | **Variant A** (keep `Disallow: /`), chosen by the owner on 17 Nov 2026, as reported to the author (PublicFunds). Variant B was made as commit `ea449394` and reverted by commit `b3cb0ea8` (`git revert ea449394`). |
| Type | **Standard** (records only). The net change from `de37f666` does not change `robots.txt`, the HTML pages, the tests or the CI register. Variant B (Normal-high: hosting / distribution) was reverted on the branch. |
| Environment | DEV (local worktree). Pre-change `main` is `de37f666c12d1d6b7a815860894af0372514ba7f`. After a merge, GitHub Pages serves the result from `main`, folder `/`. |
| CIs affected | None (records only: this record, the CHG-2026-063 record, `itil/registers/change-log.md`, `STATUS.md`). Commit B touched CI-117 (`robots.txt` and its register row) and `tests/test_robots_noindex.py`; the revert put them back as on `main`. |
| Linked records | CHG-2026-063 (PR #12, merge `de37f666`), CI-117, CI-111, CHG-2026-061 (PR #13 also edits the CHG-2026-063 record lines; see "Merge notes") |
| Rollback | Before a merge: delete the branch. After a merge: `git revert -m 1 <merge commit>`. To try variant B later: a new change record that reapplies commit `ea449394`. Git is the rollback; no `.bkp` files. |

## Goal

1. Correct the CHG-2026-063 records on `main`. At `de37f666` they described the DEV branch before its merge. After this change they state, as past-tense facts, the merge of PR #12 and the live check.
2. Give the owner two robots.txt variants to choose from, after the reviewer concern about how robots.txt and the noindex meta tag work together. The owner chose variant A.

## Commit A: records (robots.txt unchanged)

- `STATUS.md`, the CHG-2026-063 record (Status, Environment, Approval, Post-implementation review) and its change-log row now state:
  - merged in PR #12, exact head `3c93c88d`, merge commit `de37f666`, 17 Nov 2026 11:29 SAST, tag `snapshot-2026-11-17-1129`;
  - live check, 17 Nov 2026 11:30 SAST: `robots.txt` HTTP 200 with the exact content, the noindex meta tag present on `/` and `/apps/public-dashboard/`, `check_live` OK;
  - merged by the orchestrator on an owner instruction as reported to the author (PublicFunds);
  - on GitHub, PR #12 shows no review records. The reviews were done outside GitHub: one reviewer PASS, then a second reviewer PASS_WITH_CONCERNS (as reported to the author (PublicFunds)).
- `robots.txt` stays `User-agent: *` / `Disallow: /`.

## The concern

`Disallow: /` (variant A) stops a crawler from fetching any page, so the crawler never sees the `noindex` meta tag. A URL that a search engine already knows, or finds on another site, can stay in results as a bare link without a snippet. The meta tag can only remove a page from an index if the crawler can fetch the page.

## Variant A: `Disallow: /` (commit A; chosen)

- Crawlers that obey robots.txt fetch nothing: HTML, JSON, markdown, PDF and DOCX files alike.
- Limit: URLs that are already known can stay in results as bare links for a long time. The meta tag cannot help with them.

## Variant B: empty `Disallow:` plus the noindex meta tag (commit `ea449394`; reverted by `b3cb0ea8`)

- `robots.txt` is exactly `User-agent: *` and an empty `Disallow:` line (LF line ends). This allows crawling.
- Each served HTML document keeps `<meta name="robots" content="noindex, nofollow">`. Crawlers can now fetch the pages, see the tag, and drop or never add those pages.
- **Limit of B:** GitHub Pages cannot send an `X-Robots-Tag` response header. Thus files that are not HTML documents carry no noindex and could be indexed if crawled. On this site that includes:
  - `public-data/v1/*.json`;
  - markdown in `docs/`, `itil/` and the repo root (Pages serves it as plain files because of `.nojekyll`);
  - `sa_public_funds_landscape.pdf` and `.docx`;
  - the raw review templates in `thusa/review/templates/`. Only `base.html` has the meta tag; the other templates have no `<head>`.
- Under A these files are blocked from crawling, but URLs that are already known can stay in results.

## Options for the owner (not part of this change)

- Search engine removal tools with the owner's own accounts, for example Google Search Console "Removals" and Bing Webmaster Tools "Block URLs". These work with A or B.
- A staged path: use B for some weeks so that crawlers see the noindex tag, then go back to A.
- Serve a smaller Pages root (for example only the app and `public-data/`), or a host that can send `X-Robots-Tag`. This is a hosting change and needs its own change record.

## Merge notes (PR #13, CHG-2026-061)

The PR #13 branch also changes `STATUS.md`, the change-log and the CHG-2026-063 record. The conflicts cannot be avoided. A test merge with `git merge-tree` (17 Nov 2026, this branch against PR #13 head `7a7cd868`, and the reverse) gives 5 conflict blocks in 3 files in either order: `STATUS.md` (1), the CHG-2026-063 record (3: Status row; Reviewer rows; Outcome and Process note) and `itil/registers/change-log.md` (1).

- Order: PR #13 merges first.
- After PR #13 merges, this branch gets a merge of `main` (no rebase) and resolves the conflicts:
  - `STATUS.md`: keep the PR #13 block as it is on `main`, and add the CHG-2026-064 line;
  - the CHG-2026-063 record and `itil/registers/change-log.md`: take the CHG-2026-064 wording (it records the reviews outside GitHub and does not depend on PR #13 being merged).
- Older current-state lines on `main` (for example "Open PRs" in `STATUS.md`, "open PR #2" and "draft PR #10, not merged" in the CHG-2026-061 record, and the change-log rows of CHG-2026-044, CHG-2026-052 to CHG-2026-055 and CHG-2026-061) are corrected by PR #13. This branch does not change them, so that it adds no more conflicts.

## Stays the same

- The noindex meta tag in `index.html`, `apps/public-dashboard/index.html` and `thusa/review/templates/base.html`.
- `scripts/dashboard_check.py`, the publish code, public data, detectors and flags.
- The nightly routine and the bot skills.

## Testing

- `tests/test_robots_noindex.py` expects the robots.txt content of its own commit: `Disallow: /` on commit A and on the result after the revert, an empty `Disallow:` on commit B.
- Commit A (`1742336b`): `uv run pytest -q` 871 passed, 61 skipped; robots and guard tests 12 passed.
- Commit B (`ea449394`): `uv run pytest -q` 871 passed, 61 skipped; robots and guard tests 12 passed; `dashboard_check` exit 0, 0 problems.
- After the revert and this record update: same tests as commit A (results in the commit report to the reviewer).

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | variant A chosen, as reported to the author (PublicFunds) | 17 Nov 2026 |
| Reviewer 1 | reviewer | | |
| Reviewer 2 | reviewer | | |

## Post-implementation review

- Outcome: see the merge record.

## Review of head `cecd6503` and this commit

A reviewer gave PASS_WITH_CONCERNS on `cecd6503` (as reported to the author (PublicFunds)). Nothing blocked. The merge notes said that the conflicts with PR #13 were avoided. The reviewer's test merge showed 5 conflict blocks in 3 files in either order, and `git merge-tree` against PR #13 head `7a7cd868` gave the same result. "Merge notes" now says that the conflicts cannot be avoided and gives the order and the resolution.
