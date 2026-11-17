# CHG-2026-064: Follow-up to the review of CHG-2026-063 (records; robots.txt variant A or B)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Follow-up to a reviewer PASS_WITH_CONCERNS on PR #12 (CHG-2026-063), 17 Nov 2026, as reported to the author (PublicFunds). This record is not a merge GO. |
| Status | Built in DEV on branch `chg-2026-064-robots-followup` from `main` `de37f666` (tag `snapshot-2026-11-17-1129`). Commit A (records, robots.txt unchanged; two commits from `de37f666`, the second is commit A) and commit B (robots.txt variant B, one commit after A). |
| Decision | **The owner chooses A or B before a merge.** The merged `robots.txt` shows the choice: `Disallow: /` means A; an empty `Disallow:` means B. |
| Type | Commit A: **Standard** (records only). Commit B: **Normal-high** (`itil/change-enablement.md`: hosting / distribution), because it changes what crawlers may fetch. |
| Environment | DEV (local worktree). Pre-change `main` is `de37f666c12d1d6b7a815860894af0372514ba7f`. After a merge, GitHub Pages serves the result from `main`, folder `/`. |
| CIs affected | Commit A: none (records only: this record, the CHG-2026-063 record, `itil/registers/change-log.md`, `STATUS.md`). Commit B: CI-117 (`robots.txt` and its register row), `tests/test_robots_noindex.py`, this record. |
| Linked records | CHG-2026-063 (PR #12, merge `de37f666`), CI-117, CI-111, CHG-2026-061 (PR #13 also edits the CHG-2026-063 record lines; see "Merge notes") |
| Rollback | Before a merge: delete the branch. To get A from B: `git revert <commit B>`. After a merge: `git revert -m 1 <merge commit>`. Git is the rollback; no `.bkp` files. |

## Goal

1. Correct the CHG-2026-063 records on `main`. They still describe a DEV branch that is not merged. After this change they state, as past-tense facts, the merge of PR #12 and the live check.
2. Give the owner two robots.txt variants to choose from, after the reviewer concern about how robots.txt and the noindex meta tag work together.

## Commit A: records (robots.txt unchanged)

- `STATUS.md`, the CHG-2026-063 record (Status, Environment, Approval, Post-implementation review) and its change-log row now state:
  - merged in PR #12, exact head `3c93c88d`, merge commit `de37f666`, 17 Nov 2026 11:29 SAST, tag `snapshot-2026-11-17-1129`;
  - live check, 17 Nov 2026 11:30 SAST: `robots.txt` HTTP 200 with the exact content, the noindex meta tag present on `/` and `/apps/public-dashboard/`, `check_live` OK;
  - merged by the orchestrator on an owner instruction as reported to the author (PublicFunds);
  - on GitHub, PR #12 shows no review records. The reviews were done outside GitHub: one reviewer PASS, then a second reviewer PASS_WITH_CONCERNS (as reported to the author (PublicFunds)).
- `robots.txt` stays `User-agent: *` / `Disallow: /`.

## The concern

`Disallow: /` (variant A) stops a crawler from fetching any page, so the crawler never sees the `noindex` meta tag. A URL that a search engine already knows, or finds on another site, can stay in results as a bare link without a snippet. The meta tag can only remove a page from an index if the crawler can fetch the page.

## Variant A: `Disallow: /` (commit A, as live today)

- Crawlers that obey robots.txt fetch nothing: HTML, JSON, markdown, PDF and DOCX files alike.
- Limit: URLs that are already known can stay in results as bare links for a long time. The meta tag cannot help with them.

## Variant B: empty `Disallow:` plus the noindex meta tag (commit B, branch head)

- `robots.txt` is exactly `User-agent: *` and an empty `Disallow:` line (LF line ends). This allows crawling.
- Each served HTML document keeps `<meta name="robots" content="noindex, nofollow">`. Crawlers can now fetch the pages, see the tag, and drop or never add those pages.
- **Limit of B:** GitHub Pages cannot send an `X-Robots-Tag` response header. Thus files that are not HTML documents carry no noindex and could be indexed if crawled. On this site that includes:
  - `public-data/v1/*.json`;
  - markdown in `docs/`, `itil/` and the repo root (Pages serves it as plain files because of `.nojekyll`);
  - `sa_public_funds_landscape.pdf` and `.docx`;
  - the raw review templates in `thusa/review/templates/`. Only `base.html` has the meta tag; the other templates have no `<head>`.
- Under A these files are blocked from crawling, but URLs that are already known can stay in results.

## Options for the owner (not done in this change)

- Search engine removal tools with the owner's own accounts, for example Google Search Console "Removals" and Bing Webmaster Tools "Block URLs". These work with A or B.
- A staged path: use B for some weeks so that crawlers see the noindex tag, then go back to A.
- Serve a smaller Pages root (for example only the app and `public-data/`), or a host that can send `X-Robots-Tag`. This is a hosting change and needs its own change record.

## Merge notes (PR #13, CHG-2026-061)

The PR #13 branch also updates the same CHG-2026-063 lines (its commit `8385edb`). This change uses the same text where the facts allow:

- the same text: the `STATUS.md` CHG-2026-063 line, the CHG-2026-063 Environment and Change authority rows and Outcome line. The CHG-2026-064 `STATUS.md` line is placed away from the lines that PR #13 changes. Commit A does not change the CI register, so PR #13's CI-116 and CI-117 rows merge without a conflict;
- different text, because the reviews outside GitHub are now recorded and "Recorded by CHG-2026-061" is only true if PR #13 merges: the CHG-2026-063 Status row, the Reviewer 1 and 2 rows, the Process note and the change-log row. Whichever PR merges second takes the CHG-2026-064 text for these lines.

## Stays the same

- The noindex meta tag in `index.html`, `apps/public-dashboard/index.html` and `thusa/review/templates/base.html`.
- `scripts/dashboard_check.py`, the publish code, public data, detectors and flags.
- The nightly routine and the bot skills.

## Testing

- Commit A and commit B results are in the commit report to the reviewer. `tests/test_robots_noindex.py` expects the robots.txt content of its own commit.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | owner chooses A or B; GO must name the exact head | |
| Reviewer 1 | reviewer | | |
| Reviewer 2 | reviewer | | |

## Post-implementation review

- Outcome: see the merge record.
