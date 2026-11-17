# CHG-2026-063: Hide the public site from search engines (robots.txt and noindex meta tag)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner instruction to hide the site from search engines, 17 Nov 2026, as reported to the author (PublicFunds). The rule: public watcher sites use a robots.txt with `User-agent: *` and `Disallow: /` until a later combined watcher site exists. This record is not a merge GO. |
| Status | **Built in DEV, not merged.** Local branch `chg-2026-063-robots-noindex` only. Not pushed. No PR. |
| Type | **Normal-high** (`itil/change-enablement.md`: hosting / distribution). The change sets what search engines may crawl and index on the live site. It does not change data, detectors, flags or the publish code. |
| Environment | DEV (local worktree). Pre-change `main` is `7cb9faf53a989f0625c78abd9e24c7e98e4710a3` (the 17 Nov 2026 nightly data commit, B20261117T012014Z). After a merge, GitHub Pages serves the change from `main`, folder `/`. |
| CIs affected | New CI-117 (`robots.txt`, noindex meta tag); CI-111 (Pages site root); CI-105 (`apps/public-dashboard/index.html`); root `index.html`; `thusa/review/templates/base.html`; CI-109 (`scripts/dashboard_check.py`); new `tests/test_robots_noindex.py`; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md` |
| Linked records | CI-111 (GitHub Pages, `main` `/`, `.nojekyll`), CI-105, CI-109, CHG-2026-006 and CHG-2026-007 (publish and hosting), CHG-2026-061 (live check; not touched) |
| Rollback | Before a merge: delete the branch (`git worktree remove /workspace/pf-chg063 && git branch -D chg-2026-063-robots-noindex`). After a merge: `git revert -m 1 <merge commit>`; Pages then serves no robots.txt (HTTP 404, as before) and the pages lose the meta tag. Git is the rollback; no `.bkp` files. |

## Goal

Tell all search engine crawlers not to crawl or index https://publicfunds.grokforum.site/, as the owner instructed. Keep the site public and working for people who have the link.

## What GitHub Pages serves (checked 17 Nov 2026, about 11:22 SAST)

- `GET repos/GrokForum/publicfunds-sa/pages` (read-only): `build_type` `legacy`, source branch `main`, path `/`, `cname` `publicfunds.grokforum.site`, `https_enforced` true, `custom_404` false.
- `CNAME` in the repo root has `publicfunds.grokforum.site`.
- `.nojekyll` is in the repo root and there is no `_config.yml`. Thus Pages does not run Jekyll and copies files as they are. Jekyll cannot exclude `robots.txt`.
- `.gitignore` does not ignore `robots.txt` (`git check-ignore` returns 1).
- Live `https://publicfunds.grokforum.site/robots.txt` before this change: HTTP 404 (GitHub Pages "not found" page). One request out of three gave a transient HTTP 503 from the Pages cache. There is no robots.txt live today.

## What changed

1. New file `robots.txt` at the repo root (the Pages root). Exact content, LF line ends:
   ```
   User-agent: *
   Disallow: /
   ```
2. `<meta name="robots" content="noindex, nofollow">` in the `<head>` of each served HTML document:
   - `index.html` (root redirect page),
   - `apps/public-dashboard/index.html` (the app),
   - `thusa/review/templates/base.html` (the local review app base template; Pages also serves this file as raw template text).
3. `scripts/dashboard_check.py` (CI-109): on the home page in each viewport, it reports a problem if the robots meta tag is not `noindex, nofollow`.
4. New `tests/test_robots_noindex.py` (6 tests):
   - `robots.txt` exists at the served root with the exact bytes;
   - `robots.txt` is tracked by git and not ignored;
   - `.nojekyll` exists, there is no `_config.yml`, and `CNAME` is `publicfunds.grokforum.site`;
   - each tracked `.html` file with a `<head>` has the meta tag exactly once in its head;
   - the publish script only adds, commits or restores paths under `public-data/`, and has no `rm`, `git rm`, `git clean`, `git reset`, `git restore` or `git mv`, and does not name `robots.txt` or HTML pages (the test reads the script; it does not run it);
   - `pf publish-data` (`thusa/publish_data.export`) on the synthetic warehouse leaves a `robots.txt` and an `index.html` at the site root, and a `robots.txt` inside `public-data/v1/`, byte for byte unchanged, and still deletes a stale `*.json` file.
5. This record, a change-log row, CI-117 in the CI register, and a STATUS line.

## Important limit: robots.txt and the meta tag

`Disallow: /` stops a well-behaved crawler from fetching any page. Then the crawler cannot see the `noindex` meta tag. Thus:

- robots.txt stops new crawling. A search engine can still list a bare URL that it finds on another site, without a title or snippet.
- The meta tag mostly helps for pages that a search engine indexed before robots.txt went live, and for crawlers that do not obey robots.txt but do read the tag.
- To remove pages that are already in a search index quickly, the owner can use a search engine's own removal tool (for example, Google Search Console "Removals" or Bing Webmaster Tools "Block URLs"). That is a separate owner step with the owner's own accounts. It is not part of this change.

## Publish safety (why the nightly cannot overwrite or delete these files)

Read from the code at `7cb9faf`:

- `scripts/publish-public-data.sh` runs `uv run pf publish-data`, then `git add -A -- public-data/`, refuses (exit 4) if anything outside `public-data/` is staged, and commits with `-- public-data/`. Its only other git write is `git checkout -- public-data/v1/manifest.json`. It does not delete files. It cannot stage a change to `robots.txt` or an HTML page, and a dirty `robots.txt` would make it refuse, not commit.
- `thusa/publish_data.export` writes only into `out_dir` (default `public-data/v1`). Its only delete is `out_dir.glob("*.json")` for names not in the new set. `robots.txt` is in the repo root and is not a `.json` file.
- `thusa/publish.py` (`dist/public/`) and `thusa/report.py` (`dist/site/`) write and remove only under `dist/`, which `.gitignore` ignores. Pages does not serve them. These generated pages are local only, so this change does not add the meta tag to them.
- The refresh skill says "Never `reset --hard`".

Conclusion: the nightly publish cannot overwrite or delete `robots.txt` or remove the meta tag. No guard in the publish code is necessary. The new tests lock in this behaviour.

## Stays the same

- Public data files, the data pipeline, detectors, flags, the review workflow and the publish code (`scripts/publish-public-data.sh`, `thusa/publish_data.py`).
- `scripts/check_live.py` and the CHG-2026-061 work.
- The canonical link, Open Graph and Twitter meta tags. Link previews in chat apps still work.
- The nightly routine and the bot skills.

## Seen, not touched

- Pages also serves repo files that are not part of the app (for example `docs/`, `itil/`, `thusa/review/templates/*.html` as raw text). robots.txt covers them. Moving the Pages source to a smaller folder is a separate decision.
- The child review templates (`thusa/review/templates/*.html` other than `base.html`) have no `<head>`. In the review app they get the tag from `base.html`. On Pages they are raw template text and only robots.txt covers them.
- `STATUS.md` "Current" still says "as of 2026-11-15" and lists PRs #1 to #4 as open. This change adds one line and does not rewrite that section.

## Risk

- Search engines drop the site over time. This is the intended result. Risk to data correctness, privacy and availability: none found.
- A crawler that ignores robots.txt can still crawl. The meta tag helps only with crawlers that obey it.
- POPIA: the change adds no personal information. It reduces exposure.

## Testing

- Base at `7cb9faf` in this worktree (no warehouse): 865 passed, 61 skipped.
- With this change, same worktree, 17 Nov 2026: `uv run pytest -q` gave 871 passed, 61 skipped (6 new tests in `tests/test_robots_noindex.py`).
- Guard and neighbour tests: `tests/test_no_owner_quotes.py`, `tests/test_popia_names.py`, `tests/test_robots_noindex.py`, `tests/test_review_app.py`, `tests/test_improvements.py`: 39 passed.
- `uv run --group screenshots python scripts/dashboard_check.py --out /tmp/dc063`: exit 0, 31 screenshots, 0 problems (includes the new robots meta check on the home page, desktop and mobile).
- After a merge (TEST/PROD check): `curl -sS https://publicfunds.grokforum.site/robots.txt` must return HTTP 200 with the exact two lines, and `curl -sS https://publicfunds.grokforum.site/apps/public-dashboard/ | grep 'name="robots"'` must show the meta tag. Then run `scripts/check_live.py`.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | pending (needs an owner GO that names the exact head) | |
| Reviewer 1 | reviewer | pending | |
| Reviewer 2 | reviewer | pending | |

## Post-implementation review

- Outcome: pending.
- Follow-up for the owner: optional search engine removal requests (see above).
