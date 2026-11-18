# CHG-2026-068: Rewrite the git history of GrokForum/publicfunds-sa to remove the 5 titled supplier values (DRAFT)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 18 Nov 2026 07:37 SAST: rewrite the history after PR #18 (CHG-2026-067 code: the title masks and `doc` null on masked rows) merges, and draft the plan first. This record is that plan. |
| Status | **DRAFT RFC.** Drafted on 18 Nov 2026 on branch `chg-2026-068-history-rewrite-rfc` from `main` `76688eca`. Nothing was rewritten, force-pushed or deleted, and nobody contacted GitHub. This record is not an execution GO. |
| Type | **Normal-high** (`itil/change-enablement.md`: distribution, POPIA, published history). Two independent reviewer PASSes on the exact RFC head, then the owner's GO naming that head. The force-push needs a second, separate owner GO at execution time (section 12). The nightly data-refresh exemption does not cover this change. |
| Environment | DEV: a fresh mirror clone, held privately on the author's computer (all rewrite work and all checks). PROD: the GitHub repo GrokForum/publicfunds-sa and its GitHub Pages site (https://publicfunds.grokforum.site/). There is no TEST host for a history rewrite; the full check of the rewritten mirror (section 7) is the test. |
| Depends on | PR #18 (CHG-2026-067 code) merged, and the first nightly publish after that merge masked the live data (pre-check P1). |
| CIs affected | The GitHub repo (all branches, tags and commit SHAs); `public-data/v1/awards-2021.json`, `awards-2023.json`, `awards-2024.json`, `awards-2025.json` in every historic commit; GitHub Pages (rebuild); the production checkout of the nightly and every local clone and worktree; this record; `itil/registers/change-log.md`; `STATUS.md`. |
| Linked records | CHG-2026-067 (title masks, Q4 and Q6); CHG-2026-050 and CHG-2026-051 (fresh repo, first public commit `b063190`); CHG-2026-066 (nightly duties, account and origin guard, `incidents/local`); CHG-2026-044 (state backup); CHG-2026-061 (live check); CHG-2026-063 (robots); RSK-021, RSK-023 |
| Rollback | Force-push the private mirror backup back to GitHub, inside the window and before the GitHub Support purge. After the purge there is no rollback. See section 10. |

## 1. What and why

The published award files hold 5 supplier values that start with a personal title (the 5 titled supplier values; the list is held privately off git). CHG-2026-067 masks them in the export from the first nightly after PR #18 merges. At Q4 of CHG-2026-067 the owner first decided not to rewrite the history. On 18 Nov 2026 at 07:37 SAST the owner decided to rewrite it after PR #18 merges (owner decision, 18 Nov 2026 07:37 SAST).

The masks alone do not remove the values from the public repo. Every commit holds a full tree, so all old commits keep the values. This change replaces the values in every commit of the public history with the same masks that the export writes, and replaces the `doc` link of those 5 rows with `null` (CHG-2026-067 Q6). It then asks GitHub Support to purge the old commits that GitHub still keeps.

The values come from eTenders, an official public source that still publishes them. The masks are POPIA caution on our side. This change is not a finding about any person.

Precedent: on 17 Nov 2026 the histories of two sister public-data repos of the same owner were rewritten and force-pushed under an owner GO, as reported to the author by the orchestrator.

## 2. Evidence (measured by the author, 18 Nov 2026 07:37 to 07:45 SAST)

All checks ran read-only on a temporary mirror clone of the repo (deleted after the checks) and with read-only `gh api` calls. The values were matched with `grep -F -f` and `git grep -F -f` on the private list. No command printed a value.

| Item | Result |
|---|---|
| Commits on `origin/main` | 97 (`git rev-list --count origin/main`, head `76688eca`). |
| Commits reachable from all remote refs (branches, tags, `refs/pull/*`) | 109. |
| Commits that hold one or more of the 5 values | **109 of 109** (`git grep -l -F -f <private list> $(git rev-list --all)`). Case-insensitive: the same 109. |
| Paths that hold the values, over all history | Only 4: `public-data/v1/awards-2021.json` (1 value), `awards-2023.json` (2), `awards-2024.json` (1), `awards-2025.json` (1). No other path in any commit. |
| Where the values came in | Only in `b063190` (1 Nov 2026 21:30 SAST, CHG-2026-051, the first public commit). The 5 rows and their `doc` links are the same in `b063190` and in `76688eca`. |
| Commit messages, author and committer names, tag messages | 0 hits. |
| Binary files in history (`.docx`, `.pdf`, `.png`) | The text of all versions of the two `.docx` and two `.pdf` files: 0 hits. `og-card.png`: not text. No Git LFS. No database file was ever tracked. The review database is in `data/`, which is git-ignored. |
| The 5 rows | Each value is the whole `supplier` cell of 1 row (5 rows in total). No other cell in those rows holds a name word of the values (0 of 5 rows). |
| The 5 `doc` links | Each is a string (59 to 138 characters). None holds a name word of the values (0 of 5). Each occurs once in its file and in no other path, in all 109 commits. |
| Name words seen elsewhere | The name words of 2 of the 5 values also occur in other supplier cells (in `awards-2021.json` to `awards-2025.json`) that have no title and are not one of the 5 values. These cells are not in scope (section 3.2). |
| Remote refs | 19 branches (`main` and 18 others), 18 tags (`snapshot-*`: 10 annotated, 8 lightweight), 20 `refs/pull/*` refs (`refs/pull/1/head` to `refs/pull/18/head`, plus `refs/pull/11/merge` and `refs/pull/18/merge`). |
| Open PRs | #18 (`chg-2026-067-impl`, draft) and #11 (`chg-2026-062-fw-expenditure`, draft). |
| Branches already merged into `main` | 15 by ancestry. `chg-2026-067-site-draft-privacy` (PR #17) was squash-merged, so it is merged in content but not by ancestry. |
| Branch protection and rulesets | `main` is not protected (HTTP 404 "Branch not protected"); rulesets: none; branch rules on `main`: none. So no setting blocks a force-push today. |
| Pages | Legacy build from `main`, path `/`, custom domain `publicfunds.grokforum.site`, HTTPS enforced, status built. |
| Other GitHub items | Forks: 0. Releases: 0. Webhooks: 0. Workflows: only GitHub's own `pages-build-deployment`. Collaborators: 1 (the owner account). |
| Commit signatures | 18 commits (the GitHub web merges) carry GitHub's signature. 91 commits and all tags are unsigned. |
| `git filter-repo` on the author's computer | Version 2.47.0, which has `--sensitive-data-removal`. |
| Local copies on the author's computer | A scan found 12 git repos and 27 worktrees of this repo or of its earlier private repo. The 5 samples checked all hold the values. One local tag (`snapshot-2026-11-01-1944`) is not on GitHub. The local branch `incidents/local` did not exist at the check. |
| The earlier private repo (before CHG-2026-050) | Not reachable with the GrokForum token (HTTP 404). Whether it is private or deleted is **[unverified]**. Its local clone holds the values in 245 of 283 commits. |

GitHub's guide "Removing sensitive data from a repository" (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository, read 18 Nov 2026) says:
- After a rewrite and force-push, old commits can still be reached in clones and forks, by SHA in cached views on GitHub, and through pull requests that reference them.
- `refs/pull/*` are read-only, so a push cannot change them. Only GitHub Support can dereference or delete the affected PRs, run a garbage collection and remove cached views.
- Support needs the repo name, the number of affected PRs (from `filter-repo/changed-refs`) and the "First Changed Commit(s)" that `git filter-repo` prints.
- Support "won't remove non-sensitive data" and helps only where the risk cannot be removed by rotating credentials. These values are personal data from a public record, not a credential. Whether Support accepts this request is **[unverified]**.
- `git filter-repo` drops commit and tag signatures, and the diff view of closed PRs breaks.

## 3. Scope

### 3.1 In scope

1. In every blob of every commit on every branch and tag that is pushed: replace each of the 5 quoted `supplier` values with its quoted mask, exactly as the first nightly after PR #18 wrote it (first letter or digit in upper case, `*****`, last letter or digit in lower case; 7 characters; CHG-2026-067 `mask_value`).
2. In the same 5 rows: replace the quoted `doc` string with `null`. The `doc` strings hold no name words (section 2). But each link opens the tender document that names the supplier, and CHG-2026-067 Q6 dropped `doc` on masked rows. So the old commits must match the masked live rows. `ocid`, `award_id`, `reference` and `src` stay, as in Q6.
3. Paths: only the 4 award files hold the values. The replacement still runs on all blobs, so a copy in an unexpected path is also replaced.
4. GitHub: `main`, the 18 tags, the open branches, and deletion of the merged branches. A Support request (drafted in Appendix A; the owner sends it) for `refs/pull/*` and cached views.
5. Local: the production checkout of the nightly and every worktree of it (re-cloned), and `incidents/local` if it exists then.

### 3.2 Out of scope (noted, not touched)

- About 2,000 short supplier strings that may be private persons. They get a separate review later. The 2 sets of name words in section 2 belong to that review.
- The earlier private repo and its local clones (section 2). It is not public. The owner decides what to do with it (Q5).
- The other local repos and worktrees on the author's computer that are not part of the nightly. They are listed at P5, and the owner decides about them (Q6).
- Old records that cite old SHAs. They stay as history (section 8).

### 3.3 How the 5 rows are found without naming anyone

The author builds the replacements file on the author's computer and never prints it:

1. Read the old rows from `main` before PR #18 (`76688eca` or the last nightly before the merge) and the new rows from `main` after the first masked nightly.
2. Join the rows by (`ocid`, `award_id`) in each award file.
3. Keep only the rows where the old `supplier` is one of the 5 values in the private list and the new `supplier` is a 7-character mask and the new `doc` is `null`. Stop unless exactly 5 rows match.
4. For each row write two lines: `"<old supplier>"==>"<new supplier>"` and `"<old doc>"==>null`. The quotes make each match a whole JSON string. JSON escaping is the same as in the files (checked: each quoted value and each quoted `doc` occurs exactly once in its file).
5. Store the file with mode 0600, held privately on the author's computer, outside every git worktree.

## 4. Method

`git filter-repo` (2.47.0) on a fresh mirror clone, as in GitHub's guide:

```
git filter-repo --sensitive-data-removal --replace-text <private replacements file> \
  --prune-empty never --prune-degenerate never
```

- `--sensitive-data-removal` fetches all refs including `refs/pull/*`, rewrites them all, and writes `filter-repo/changed-refs` and the "First Changed Commit(s)" note that Support needs.
- `--replace-text` changes blob content only. Messages hold no values, so `--replace-message` is not used.
- `--prune-empty never` and `--prune-degenerate never` keep one new commit for each old commit. Without them, a nightly commit whose only change was the masks would become empty and be dropped, and the commit map would not be 1 to 1.
- `filter-repo/commit-map` and `filter-repo/ref-map` are copied to the private store (section 8).
- After PR #18's first nightly, `main` already holds the masks, so the tree of the new `main` is the same as the tree of the old `main`. Only the commit SHAs change.

## 5. Pre-checks (all must pass; stop on any failure)

| # | Check | How |
|---|---|---|
| P1 | PR #18 is merged and the first nightly after it masked the live data. | `main` has the PR #18 merge. The award files on `main` and on the live site have 0 hits for the private list (`grep -c -F -f`) and exactly 5 masked rows with `doc` `null`. The nightly report passed (data gate, POPIA check, `check_live` OK). |
| P2 | No nightly runs, and the routine is paused for the window. | The orchestrator pauses the nightly refresh routine and confirms it. `pgrep -f '[t]husa run'` prints nothing. The window ends at least 2 hours before 03:00 SAST. |
| P3 | A full mirror backup exists in two places, and a restore check passed. | `git clone --mirror` of GitHub into the private store on the author's computer; `git fsck --full` clean; a clone of the backup has the same `main` tree, the same 19 branches, 18 tags and 20 `refs/pull/*` as `git ls-remote`. A second copy (a git bundle of all refs) goes to the owner's backups (Q3). The backup holds the values, so it stays private and is deleted at the end of the retention period (Q4). |
| P4 | Every open branch and PR is listed. | `gh pr list --state open` and `git ls-remote --heads`, each marked merged or open. Today: open #18 (merged at P1) and #11. The owner decides for #11 (Q2). |
| P5 | Every local copy is listed. | The production checkout and its worktrees; `incidents/local` if it exists (list its commits); every other local clone of this repo. Uncommitted work in a worktree is committed or saved as a patch first. |
| P6 | GitHub settings allow the push. | Branch protection and rulesets on `main` read-only with `gh api`. If any blocks a force-push, the owner allows it for the window and restores it after (section 9, R6). The Pages `cname` is recorded. |
| P7 | The account and origin are correct. | The CHG-2026-066 guard: `GH_TOKEN` from `gh auth token --user GrokForum`, `gh auth setup-git`, and `git remote get-url origin` must match `github.com/GrokForum/publicfunds-sa`. |
| P8 | The replacements file is correct. | Exactly 10 lines (5 values, 5 `doc` lines); every left side occurs exactly once in the pre-PR #18 tree; every right side is a 7-character mask or `null`. |

## 6. Steps (window)

| # | Step | Stop if |
|---|---|---|
| S0 | The owner gives the execution GO for the force-push. The author records the time. | No GO. |
| S1 | Take a fresh mirror (`git clone --mirror`) of GitHub. Record the SHAs of `main` and of each branch and tag (`git show-ref`). | `main` differs from P1. |
| S2 | Run the filter-repo command of section 4 in the mirror. Save the "First Changed Commit(s)" line and the count of `refs/pull/*/head` in `filter-repo/changed-refs`. | Any error. |
| S3 | Verify (section 7). | Any check fails. Then discard the mirror; nothing on GitHub changed. |
| S4 | Tags: `git filter-repo` moved the 8 lightweight tags and wrote new annotated tag objects for the 10 annotated tags (same names, tagger and message). Check that each of the 18 tags points to the commit that `commit-map` gives for its old commit. | Any tag is missing or wrong. |
| S5 | Run the P7 guard. Force-push `main` with a lease: `git push --force-with-lease=main:<old main SHA> origin refs/heads/main:refs/heads/main`. | The lease fails (`main` moved). Then stop and find out why. |
| S6 | Force-push the tags: `git push --force origin 'refs/tags/*:refs/tags/*'`. | Any tag push fails. |
| S7 | Open branches: force-push each rewritten open branch with a lease (today only `chg-2026-062-fw-expenditure`, if the owner keeps PR #11 open). Merged branches: delete them on GitHub (`git push origin --delete <branch>`). The list comes from P4. | Any push fails. |
| S8 | Check GitHub: `git ls-remote` shows only the expected refs and the new SHAs. A new mirror clone has 0 hits for the private list in all revs, except in `refs/pull/*`, which are read-only until Support acts. | Any hit outside `refs/pull/*`. |
| S9 | Pages: wait for the Pages build of the new `main` (`gh api repos/GrokForum/publicfunds-sa/pages/builds/latest` status `built`). Run `scripts/check_live.py`. Check that `/CNAME` and `/robots.txt` on the live site are the same bytes as before and that the Pages `cname` setting is unchanged. | Build fails or `check_live` is not OK. Then decide between rollback (section 10) and a fix. |
| S10 | Re-clone the production checkout: move it aside, clone the new repo to the same place, move the git-ignored `data/` and other git-ignored state across, and check the CHG-2026-066 guard and `git status`. Re-create the worktrees that are still needed from the new clone. Start the review app again and check its health. | The guard fails or `data/` is not complete. |
| S11 | `incidents/local` (never pushed): if it exists, export its commits with `git format-patch main..incidents/local` before S10, check the patches with `grep -c -F -f` (0 hits expected), and apply them in the new clone on a new `incidents/local` from the new `main`, in its own worktree. If it does not exist, the nightly creates it when it needs it. | Patches do not apply or hold a value. |
| S12 | The orchestrator resumes the nightly routine. The next nightly must pass step 0 (fast-forward from the new `origin/main`). | The routine stays paused until S10 passes. |
| S13 | The author commits one records change (section 8): Result of this record, change-log row, STATUS line and the SHA mapping note. It goes through the normal PR process. | — |
| S14 | The owner sends the GitHub Support request (Appendix A) with the private list attached privately. After Support confirms, the author checks that `refs/pull/*` and the old SHAs no longer resolve on GitHub. | — |

The window from S1 to S12 is short: the repo is about 3.3 MB, so the rewrite itself takes seconds. Plan 2 hours, in daytime, not within 2 hours of 03:00 SAST.

## 7. Verification of the rewritten mirror (S3)

All checks run on the mirror before any push.

1. `git grep -c -F -f <private list> $(git rev-list --branches --tags)`: 0 hits. Also with `-i`: 0 hits.
2. The tree of the new `main` is byte-identical to the tree of the old `main`: `git rev-parse <new main>^{tree}` equals `git rev-parse <old main>^{tree}`. The live data is already masked, so nothing at the tip changes.
3. For each pair in `commit-map`, `git diff --name-only <old> <new>` lists only the 4 award files (or nothing). A JSON check of those files shows that only the `supplier` and `doc` cells of the 5 rows differ, and that they equal the values of the masked tip.
4. The number of commits on `main` and on each branch is the same as before. Author, committer, dates and messages are the same.
5. `git fsck --full` is clean.
6. The full test suite on a checkout of the new `main` gives the same counts as on the old `main`.
7. `CNAME`, `robots.txt` and `public-data/v1/manifest.json` are the same bytes as on the old `main` (follows from check 2).

## 8. Commit map and old SHAs in records

- `filter-repo/commit-map` (old SHA to new SHA) and `filter-repo/ref-map` are copied to the private store, held privately on the author's computer, with the mirror backup. They do not go into git, because the old SHAs point to commits that GitHub keeps until the purge.
- Records that cite old SHAs (change records, the change-log, STATUS, PR texts, the private approval record) stay as they are. They are history.
- S13 adds one mapping note to this record and to STATUS: SHAs cited in records before the rewrite date refer to the history before CHG-2026-068; the private commit map gives the new SHA of each one. The snapshot tags keep their names, so a record that cites a tag still works.
- The live manifest's `build.code_commit` cites an old SHA until the next nightly writes a new one. This is expected; `check_live` does not check it.

## 9. Risks

| # | Risk | Likelihood × impact | Mitigation |
|---|---|---|---|
| R1 | Links to old commits break (records, PR pages, chats, the old `code_commit`). | 5 × 2 = 10 | Accepted. Tags keep their names; the private commit map and the S13 note map old to new. PR diff views break after the purge (GitHub's guide). |
| R2 | The nightly runs in the window and pushes a commit that the force-push then removes, or it starts from the old history. | 2 × 4 = 8 | P2 pauses the routine. S5 uses `--force-with-lease`. A nightly that starts on the old checkout stops at step 0 with `ACTION: checkout update failed`, because `--ff-only` fails on the rewritten `origin/main`, so it cannot publish or push. |
| R3 | A clone made before the rewrite pushes the old history back (recontamination). | 2 × 5 = 10 | The repo has 1 collaborator and 0 forks. All local copies are listed (P5) and re-cloned or retired (Q6). No push from an old clone. S8 and the next week's checks look for hits again. |
| R4 | The live site is down or stale during the Pages rebuild. | 2 × 2 = 4 | The tree is unchanged, so the build has the same files. The rebuild takes minutes. S9 runs `check_live`. Rollback if the site does not come back. |
| R5 | The custom domain is lost. | 1 × 4 = 4 | `CNAME` is in the tree and does not change (section 7, check 7). S9 checks the Pages `cname` setting and `/CNAME` on the live site. |
| R6 | Branch protection or a ruleset blocks the force-push. | 1 × 2 = 2 | Today there is none (section 2). If one exists at P6, the owner allows force-pushes on `main` for the window (Settings, Branches or Rules) and restores the setting after S9. |
| R7 | A replacement hits text that is not one of the 5 cells. | 1 × 3 = 3 | Quoted whole-string matches; each left side occurs once (P8); section 7 check 3 limits the diff to the 5 rows. |
| R8 | GitHub Support declines, because the data is not a credential. | 3 × 3 = 9 | The rewrite still removes the values from all branches and tags. The old commits stay reachable only by SHA and through PR refs. The owner decides whether to accept that or to move to a fresh repo (CHG-2026-050 route). |
| R9 | GitHub's signatures on 18 web-merge commits are lost. | 5 × 1 = 5 | Accepted (GitHub's guide). |
| R10 | Open PR #11 loses review comments on the old diff. | 3 × 1 = 3 | The owner decides at Q2: keep it open on the rewritten branch, or close it and open a new PR. |
| R11 | The private backup keeps the values longer than needed. | 2 × 3 = 6 | Mode 0600, off git, deleted at the end of the retention period (Q4). |

## 10. How to revert

- **In the window, before the Support purge:** from the private mirror backup of P3, run the P7 guard and `git push --force --mirror origin`. GitHub refuses the `refs/pull/*` updates (read-only); that is expected and harmless. Then check `git ls-remote` against the P3 ref list, wait for the Pages build and run `check_live`. Re-clone the production checkout from GitHub again. A nightly commit made after the force-push would be lost, so the revert is only for the window, while the routine is paused.
- **After the GitHub Support purge, there is no rollback.** The purge cannot be undone. A push of the old history would publish the values again and undo this change.
- The rollback of the S13 records commit is `git revert` of that commit.

## 11. Duties kept

| Duty | After the rewrite |
|---|---|
| Nightly refresh and publish (03:00 SAST) | Works on the re-cloned checkout at the same place. Step 0 fast-forwards from the new `origin/main`. The publish pushes to the same `main`. The routine is resumed at S12 only after S10 passes. |
| `robots.txt` (`Disallow: /`) and the `noindex, nofollow` meta tags | Same bytes (section 7, checks 2 and 7). |
| `CNAME` and the custom domain | Same bytes; Pages `cname` setting unchanged (S9). |
| `public-data/v1/manifest.json` and all public data | Same bytes. `build.code_commit` updates at the next nightly (section 8). |
| `check_live` | Run at S9 and by the next nightly. |
| State backup (CHG-2026-044) | Its files are outside the repo; the next nightly runs it. |
| Review app | Restarted at S10 from the re-cloned checkout with the same git-ignored `data/`. |
| `incidents/local` (never pushed) | Recreated at S11 if it exists. |
| Masks and the export-blocking scan (CHG-2026-067) | Unchanged; they keep the values out of every new publish. |

## 12. Approval

1. Two independent reviewer PASSes on the exact head of this RFC.
2. The owner's GO naming that head. This approves the plan only.
3. At execution time, a separate explicit owner GO for the force-push (S0), because it overwrites published history. The author never force-pushes without it.
4. The owner sends the GitHub Support request (S14). The author does not contact GitHub.

## 13. Open questions for the owner

| # | Question | Author's recommendation |
|---|---|---|
| Q1 | When is the window? | The first day after the first masked nightly, in daytime. |
| Q2 | PR #11 (open draft): keep it open on the rewritten branch, or close it and open a new PR after the rewrite? | Close and reopen, so no review comment hangs on an old diff. |
| Q3 | Where do the owner's backups of the mirror go? | A git bundle in the owner's private backup store, not in any repo. |
| Q4 | How long are the mirror backup and the commit map kept? | Until GitHub Support confirms the purge, plus 7 days. Then delete the backup; keep only the commit map (SHAs only). |
| Q5 | The earlier private repo (before CHG-2026-050) also holds the values. Leave it, clean it, or delete it? | Out of scope here; decide in a separate change. |
| Q6 | Retire the other local repos and worktrees of this repo and of the earlier repo on the author's computer? | Yes, after S10, as a separate step with its own GO, because it deletes local data. |
| Q7 | If GitHub Support declines (R8), accept the SHA-only exposure, or move to a fresh repo? | Accept, and record it as a known limit. |

## 14. Seen, not touched

- The name words of 2 of the 5 values also occur in other untitled supplier cells. They belong to the later review of short supplier strings.
- One local tag (`snapshot-2026-11-01-1944`) is not on GitHub. It is local only and goes away with the re-clone.

## 15. Testing of this record

- Docs only. The full test suite ran on the branch (counts in the Revisions section).
- The added lines were checked for the 5 values (`grep -c -F -f` on the private list: 0 hits), for names, ids, e-mail addresses, private paths and stale words.

## Appendix A. Draft GitHub Support request (the owner sends it)

> Subject: Sensitive data removal: GrokForum/publicfunds-sa
>
> Repository: GrokForum/publicfunds-sa (public).
>
> We rewrote the history of this repository with `git filter-repo --sensitive-data-removal` to remove personal data: five supplier values that hold a person's title and name, in public procurement data files. We force-pushed all branches and tags. No forks exist.
>
> Please dereference the affected pull requests (keep their conversations), run a garbage collection, and remove cached views of the old commits.
>
> - Number of affected pull requests: <N from `filter-repo/changed-refs`>.
> - First Changed Commit(s): <SHA from the `git filter-repo` output>.
> - LFS objects orphaned: none.
>
> The five values are in an attached file that is sent privately with this request. They are not in this message.

## Revisions

- Draft (18 Nov 2026): first version. Full test suite on the branch: 961 passed, 61 skipped. Added lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.

## Post-implementation review

- Outcome: not started (draft).
