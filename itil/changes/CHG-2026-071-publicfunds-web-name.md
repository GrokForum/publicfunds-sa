# CHG-2026-071: Name the site-only fresh repository publicfunds-web

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 19 Nov 2026 21:18 SAST, given by the owner in the orchestrator's chat. The author verified the decision in that chat. |
| Status | **Draft record.** This record states the name decision of 19 Nov 2026 and the seed method. It is not an execution GO. |
| Type | Standard (docs only). Creation of the repository, and a seed push, are a later Normal-high change. Those steps take place only after an owner GO that names the seed tree. |
| Environment | Records only. This change does not create a GitHub repository and does not push. |
| CIs affected | This record; `itil/registers/change-log.md`; `STATUS.md`. GrokForum/publicfunds-site is unchanged. A CI row for GrokForum/publicfunds-web is added when that repository is created under an owner GO. |
| Linked records | CHG-2026-069 (current site-only repository GrokForum/publicfunds-site); CHG-2026-070 (nightly publish into that repository, PR #23); CHG-2026-050 (earlier fresh data repository). |
| Rollback | `git revert -m 1 <merge commit>`. |

## 1. What and why

The owner named the site-only fresh repository `publicfunds-web` on 19 Nov 2026 at 21:18 SAST. The decision was given in the orchestrator's chat. The author verified it there.

This is the site-only half of a two-repository plan: a code and pipeline repository, and a site-only repository. The name of the fresh code and pipeline repository is not decided. This record writes that name as `<code-repo, name to be decided>` and does not invent one.

The plan seeds a fresh repository after about 14 nights of stability. The Phase 0 streak is counted from 14 Nov 2026 and is due about 27 Nov 2026 if every nightly stays green. The owner may restart that count after the first green nightly on the site repository that will serve the custom domain. This record is the name and the method. It is not the seed push.

GrokForum/publicfunds-site remains the live site-only repository under CHG-2026-069 and CHG-2026-070. This record does not rename that repository. Whether `publicfunds-web` later replaces GrokForum/publicfunds-site, or sits beside it, is not decided in this record.

Repository creation and a seed push take place only after an owner GO that names the seed tree.

## 2. Seed method

The site-only fresh repository is seeded with one clean root commit and no parent. The commit is built with `git commit-tree <tree>` from an allowlisted tree only. Author and committer are `PublicFunds publisher` `<noreply@publicfunds.grokforum.site>`.

The tree is built with the same method as the CHG-2026-069 step S3 tool: the section 3 allowlist, without `CNAME`, and gates 3 to 5.

1. Read the allowlisted site files from the current masked published data commit (not from a dirty work tree).
2. Run gate 3 (mask scan against the private titled-values list, held off git).
3. Run gate 4 (POPIA check against the warehouse banned-name list).
4. Run gate 5 (allowlist: only the listed files, required files present, no symlinks, no `CNAME`).
5. Write the tree and make a root commit. Check that the commit's tree hash matches the scanned tree, and that the commit has no parent.
6. Push plainly to `https://github.com/GrokForum/publicfunds-web.git`, and only if `git ls-remote` of that remote prints no refs. If any ref exists, stop. Do not force-push. Do not copy tags from GrokForum/publicfunds-sa or GrokForum/publicfunds-site.
7. Record the new tip privately (mode 0600).

If the published data commit has moved on before the GO, rebuild the seed from the then-current masked build. The owner GO must name the tree that is pushed.

## 3. Allowlist

The first-publish allowlist is the same as CHG-2026-069 section 3 and the S3 tool (no `CNAME`):

- `index.html`
- `apps/public-dashboard/index.html`
- `apps/public-dashboard/og-card.png`
- `robots.txt`
- `.nojekyll`
- `privacy/index.html`
- `404.html`
- every file under `public-data/v1/` that the export writes

A later export may add a file under `public-data/v1/`. That file is then allowed. A file outside `public-data/v1/` is not allowed unless it is named above. `CNAME` is not in the first seed tree.

## 4. What must not carry over

The fresh site-only repository must not receive:

- git history or `snapshot-*` tags from GrokForum/publicfunds-sa or GrokForum/publicfunds-site
- any commit whose author or committer is a bot identity or a personal mailbox
- historical `itil/changes/*` records or `STATUS.md` as they stand
- `.popia-names.local`
- warehouse and review state (`data/`, DuckDB, the review database)
- backups, secrets and env files (`.env`, `.env.*`, `*.pem`, `*.key`, `secrets/`)
- private publish state held only on the author's computer (titled-values file, site-publish config, recorded tip file, site bundles)
- workflow secrets
- local virtualenvs and caches
- any file that is not on the allowlist in section 3, including `CNAME` in the first seed

The tree that should carry is the allowlisted site pages and `public-data/v1` at the current masked build, after the gates in section 2 pass.

The fresh code and pipeline repository, `<code-repo, name to be decided>`, is a separate seed. That seed is not part of this record.

## 5. Rehearsal seed, 19 Nov 2026

A rehearsal seed was built on 19 Nov 2026 at 21:23 SAST from data commit `59c4d81c830ae87ea796716d24242b7c3b0c85d6` (then `main` of GrokForum/publicfunds-sa). Gates 3 to 5 passed, with 0 problems each. The tree had 26 files and no `CNAME`.

- Tree: `0b0e1c13ee32a766c868db6bd082b51bc70cdd5b`
- Root commit: `904bc36a37cc1726af9d02546e70dfc4ddb2afa2`

That tree matches the tree of GrokForum/publicfunds-site `main` at root commit `5b08c9b7a84a047215a0c91763e5e37f232e8762`. That live root commit was also a first publish with no `CNAME`, from the same data commit. The rehearsal commit hash differs, because `git commit-tree` includes the commit dates. Data `main` was not newer than `59c4d81c` at the check, so a tree from today's data `main` is the same tree.

The rehearsal is held privately off git. An owner GO for a seed push must name the seed tree that is current at that time.

## 6. Questions for the owner

1. What is the name of the fresh code and pipeline repository (`<code-repo, name to be decided>`)?
2. Does `publicfunds-web` replace GrokForum/publicfunds-site after the stability streak, or does it sit beside it?

## 7. Change

1. This record.
2. A change-log row.
3. A short STATUS.md note.

No other document on `main` named this future site-only repository, so no further rename was made. References to the live repository GrokForum/publicfunds-site in CHG-2026-069 and CHG-2026-070 are left as they are.

## 8. Stays the same

- No code, pipeline, skill or routine change.
- No GitHub repository is created, and no push is made, in this change.
- GrokForum/publicfunds-site, GrokForum/publicfunds-sa, DNS and Pages settings are unchanged.

## 9. Testing

- `uv run pytest -q` on branch `docs-publicfunds-web-name` at 19 Nov 2026 21:25 SAST: 1,060 passed, 61 skipped.
- That run includes `tests/test_no_owner_quotes.py` and `tests/test_popia_names.py`.

## 10. Risk

Docs only. A stale name note if the owner later chooses a different site-only name. Update this record in that case. There is no publication risk from this change.

## 11. How to revert

`git revert -m 1 <merge commit>`.

## 12. Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | | | |
| Second reviewer | | | |

Reviewers: orchestrator and critic, on the exact head.

## 13. Result

This record states the name decision of 19 Nov 2026 21:18 SAST and the seed method.
