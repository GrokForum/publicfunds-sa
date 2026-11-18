# CHG-2026-068: Rewrite the git history of GrokForum/publicfunds-sa so that the 5 titled supplier values are in no branch or tag (DRAFT)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 18 Nov 2026 07:37 SAST: rewrite the history after PR #18 (CHG-2026-067 code: the title masks and `doc` null on masked rows) merges, and draft the plan first. This record is that plan. That decision supersedes the CHG-2026-067 Q4 answer (see section 1). |
| Status | **Withdrawn (not executed).** Drafted on 18 Nov 2026 on branch `chg-2026-068-history-rewrite-rfc` from `main` `76688eca`. PR #19 is the RFC. Owner answers of 18 Nov 2026 09:48 SAST, given in the orchestrator's chat and relayed to the author; the author did not see the owner's words first-hand: the owner issued a GO for the merge of PR #19 at `969b1b66`, with a snapshot tag; Q10, the history rewrite is dropped; Q7, the owner accepted the leftover `refs/pull/*` exposure until the source repositories go private. Owner statement, 18 Nov 2026 09:50 SAST, given in the PublicFunds chat: all the source repositories, including this data repository, go private when the merged site that holds all 4 public datasets goes live. Nothing was rewritten or force-pushed, and nobody contacted GitHub Support. |
| Type | **Normal-high** (`itil/change-enablement.md`: distribution, POPIA, published history). Two independent reviewer PASSes on the exact RFC head, then the owner's GO naming that head. The force-push needs a second, separate owner GO at execution time (section 12). The nightly data-refresh exemption does not cover this change. |
| Environment | DEV: a fresh mirror clone, held privately on the author's computer (all rewrite work and all checks). PROD: the GitHub repo GrokForum/publicfunds-sa and its GitHub Pages site (https://publicfunds.grokforum.site/). There is no TEST host for a history rewrite; the full check of the rewritten mirror (section 7) is the test. |
| Depends on | PR #18 (CHG-2026-067 code) merged, and the first nightly publish after that merge masked the live data (pre-check P1). |
| CIs affected | The GitHub repo (all branches, tags and commit SHAs); `public-data/v1/awards-2021.json`, `awards-2023.json`, `awards-2024.json`, `awards-2025.json` in every historic commit; GitHub Pages (rebuild); GitHub Actions `github-pages` artifacts; the production checkout of the nightly and every local clone and worktree; this record; `itil/registers/change-log.md`; `STATUS.md`. |
| Linked records | CHG-2026-067 (title masks, Q4 and Q6); CHG-2026-069 (separate public site repository, RFC head `3756dcd3`, section 16); CHG-2026-050 and CHG-2026-051 (fresh repo, first public commit `b063190`); CHG-2026-066 (nightly duties, account and origin guard, `incidents/local`); CHG-2026-044 (state backup); CHG-2026-061 (live check); CHG-2026-063 (robots); RSK-021, RSK-023 |
| Rollback | Force-push the private mirror backup (the S1 copy taken just before S2) back to GitHub, while that backup is kept (Q4). A `--mirror` push from that backup also deletes any branches created after S1. After the backup is deleted, there is no rollback. A restore after the nightly routine resumes also overwrites later commits. See section 10. |

## 1. What and why

The published award files hold 5 supplier values that start with a personal title (the 5 titled supplier values; the list is held privately off git). CHG-2026-067 masks them in the export from the first nightly after PR #18 merges. At Q4 of CHG-2026-067 the owner first decided not to rewrite the history (masking from the next nightly, history kept, no rewrite). Owner decision, 18 Nov 2026 07:37 SAST: rewrite the history after PR #18 merges, and draft the plan first. That later decision supersedes the CHG-2026-067 Q4 answer. The 07:37 decision was given in the PublicFunds chat and was relayed to reviewers; the reviewers did not hear it first-hand.

The masks alone do not remove the values from the public repo. Every commit holds a full tree, so all old commits keep the values. This change replaces the values in every commit on a branch or tag that a push can update with the same masks that the export writes, and replaces the `doc` link of those 5 rows with `null` (CHG-2026-067 Q6). After the rewrite, the values are in no branch or tag. They remain in the old commits that `refs/pull/*` still name. Those refs are advertised by `git ls-remote` (22 at the 18 Nov 2026 07:58 SAST count). Any `git clone --mirror`, or any fetch of `refs/pull/*`, downloads those commits and the values, without a SHA. Cached views of old SHAs also remain. There is no GitHub Support purge request (owner decision relayed 18 Nov 2026 07:51 SAST). Confirmation that the owner accepts this leftover exposure is open (Q7). The 07:51 decisions were also given in the PublicFunds chat and were relayed to reviewers; the reviewers did not hear them first-hand. The earlier private repository is addressed as a separate step (section 6.1, Q5).

The values come from eTenders, an official public source that still publishes them. The masks are POPIA caution on our side. This change is not a finding about any person.

Precedent: on 17 Nov 2026 the histories of two sister public-data repos of the same owner were rewritten and force-pushed under an owner GO, as reported to the author by the orchestrator.

## 2. Evidence (measured by the author)

All checks ran read-only on a temporary mirror clone of the repo (deleted after the checks) and with read-only `gh api` calls. The values were matched with `grep -F -f` and `git grep -F -f` on the private list. No command printed a value. The counts below are dated findings. At execution, later steps compare against the S1 `git ls-remote` list, not against these numbers.

### 2.1 Repo history (18 Nov 2026 07:37 to 07:45 SAST)

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
| The earlier private repository (before CHG-2026-050) | Not reachable with the GrokForum token (HTTP 404). Whether it is private or deleted is **[unverified]**. Its local clone holds the values in 245 of 283 commits. See section 6.1. |

### 2.2 Later dated findings (18 Nov 2026 07:57 to 07:58 SAST)

Origin was first confirmed as `https://github.com/GrokForum/publicfunds-sa.git`. Then read-only `gh api` and `git ls-remote` ran with the GrokForum token.

| Item | Result |
|---|---|
| Open PRs | #19 (this RFC, branch `chg-2026-068-history-rewrite-rfc`, draft), #18 and #11. |
| Remote refs (`git ls-remote`) | 20 branches (`main` and 19 others, including `chg-2026-068-history-rewrite-rfc`), 18 tags, 22 `refs/pull/*` refs (the 07:45 set plus `refs/pull/19/head` and `refs/pull/19/merge`). These counts already differ from section 2.1. That is why S1 records a fresh list. |
| GitHub Actions artifacts | 7 unexpired artifacts, all named `github-pages`. Sizes 2,298,690 to 2,373,269 bytes (about 2.3 MB each). Each expires about 24 hours after it was created. None was expired at the check. Heads: `76688eca` (created 18 Nov 2026 07:04 SAST, expires 19 Nov 2026 07:04 SAST), `d688b031` (18 Nov 03:23 SAST, expires 19 Nov 03:23 SAST), `c00fa2fe` (17 Nov 19:52 SAST, expires 18 Nov 19:52 SAST), `8733c608` (17 Nov 18:26 SAST, expires 18 Nov 18:26 SAST), `ad850d92` (17 Nov 18:02 SAST, expires 18 Nov 18:02 SAST), `e5fbfa58` (17 Nov 15:46 SAST, expires 18 Nov 15:46 SAST), `de37f666` (17 Nov 11:29 SAST, expires 18 Nov 11:29 SAST). Each head is a commit that section 2.1 found holds the values. A `github-pages` artifact is the built site, so it holds the award files. The artifacts were not downloaded. |
| Push from a `--mirror` clone | Reproduced in a scratch directory: `git clone --mirror` sets `remote.origin.mirror=true`. `git push --force-with-lease=main:<SHA> origin refs/heads/main:refs/heads/main` exits 128 with `fatal: --mirror can't be combined with refspecs`. The same command succeeds with `git -c remote.origin.mirror=false` and after `git config --unset remote.origin.mirror`. |

GitHub's guide "Removing sensitive data from a repository" (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository, read 18 Nov 2026) says:

- After a rewrite and force-push, old commits can still be reached in clones and forks, by SHA in cached views on GitHub, and through pull requests that reference them.
- `refs/pull/*` are read-only, so a push cannot change them.
- `git filter-repo` drops commit and tag signatures.

The guide also describes a request to GitHub Support to purge cached views and `refs/pull/*`. This plan does not include that request (owner decision relayed 18 Nov 2026 07:51 SAST). `refs/pull/*` stay advertised, so any `git clone --mirror` or any fetch of those refs downloads the old commits with the values, without a SHA. Cached views of old SHAs, and pull-request diffs that cite them, can also still show the values. Confirmation that the owner accepts this leftover exposure is open (Q7; risk R8).

Installed `git-filter-repo` 2.47.0 (help and source, read 18 Nov 2026): `--sensitive-data-removal` fetches all refs from origin in a non-mirror clone, and it keeps the `origin` remote. The fetch runs only when `remote.origin.mirror` is not `true`. In a `--mirror` clone that fetch is skipped. A fresh `git clone --mirror` of GitHub already has all advertised refs, including `refs/pull/*`, so the skip is harmless, and `origin` is kept.

## 3. Scope

### 3.1 In scope

1. In every blob of every commit on every branch and tag that is pushed: replace each of the 5 quoted `supplier` values with its quoted mask, exactly as the first nightly after PR #18 wrote it (first letter or digit in upper case, `*****`, last letter or digit in lower case; 7 characters; CHG-2026-067 `mask_value`).
2. In the same 5 rows: replace the quoted `doc` string with `null`. The `doc` strings hold no name words (section 2). But each link opens the tender document that names the supplier, and CHG-2026-067 Q6 dropped `doc` on masked rows. So the old commits must match the masked live rows. `ocid`, `award_id`, `reference` and `src` stay, as in Q6.
3. Paths: only the 4 award files hold the values. The replacement still runs on all blobs, so a copy in an unexpected path is also replaced.
4. GitHub: `main`, the tags, the open branches, and deletion of the merged branches, as listed at S1. No Support request (owner decision relayed 18 Nov 2026 07:51 SAST). After the push, the values are in no branch or tag. `refs/pull/*` stay advertised and still name the old commits with the values. Confirmation of that leftover exposure is open (Q7).
5. GitHub Actions `github-pages` artifacts that still hold the unmasked values (P9, Q8).
6. Local: the production checkout of the nightly and every worktree of it (re-cloned), and `incidents/local` if it exists then.
7. The earlier private repository (section 6.1): the owner or the orchestrator acts on it with the account that owns it, by the owner's choice at Q5.

### 3.2 Out of scope (noted, not touched)

- About 2,000 short supplier strings that may be private persons. They get a separate review later. The 2 sets of name words in section 2 belong to that review.
- Local clones of the earlier private repository on the author's computer, other than the production checkout of this repo. The owner decides about them (Q6).
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

- `--sensitive-data-removal` marks the rewrite as a sensitive-data removal. It rewrites every ref in the mirror. In a non-mirror clone it also fetches all refs from origin (`+refs/*:refs/*`), including `refs/pull/*`. In a mirror clone (`remote.origin.mirror=true`) that fetch is skipped. The skip is harmless for a fresh `--mirror` clone of GitHub, which already has all advertised refs. The option also keeps the `origin` remote (it returns before the default `git remote rm origin`). See section 2.2. The tool may still print a "First Changed Commit(s)" line and write `filter-repo/changed-refs`. That is its normal output. This plan does not keep those items for a Support request.
- `--replace-text` changes blob content only. Messages hold no values, so `--replace-message` is not used.
- `--prune-empty never` and `--prune-degenerate never` keep one new commit for each old commit. Without them, a nightly commit whose only change was the masks would become empty and be dropped, and the commit map would not be 1 to 1.
- `filter-repo/commit-map` and `filter-repo/ref-map` are copied to the private store (section 8).
- After PR #18's first nightly, `main` already holds the masks, so the tree of the new `main` is the same as the tree of the old `main`. Only the commit SHAs change.

A `--mirror` clone has `remote.origin.mirror=true`. A push that names a refspec then fails (`fatal: --mirror can't be combined with refspecs`; section 2.2). After the rewrite and the section 7 checks, either run `git config --unset remote.origin.mirror`, or use `git -c remote.origin.mirror=false` on each push in S5 to S7. Do not unset the flag before S2: the skip of the extra fetch depends on `remote.origin.mirror=true`.

## 5. Pre-checks (all must pass; stop on any failure)

| # | Check | How |
|---|---|---|
| P1 | PR #18 is merged and the first nightly after it masked the live data. | `main` has the PR #18 merge. The award files on `main` and on the live site have 0 hits for the private list (`grep -c -F -f`) and exactly 5 masked rows with `doc` `null`. The nightly report passed (data gate, POPIA check, `check_live` OK). |
| P2 | No nightly runs, and the routine is paused for the window. | The orchestrator pauses the nightly refresh routine and confirms it. `pgrep -f '[t]husa run'` prints nothing. The window ends at least 2 hours before 03:00 SAST. |
| P3 | A full mirror backup exists in two places, and a restore check passed. | `git clone --mirror` of GitHub into the private store on the author's computer; `git fsck --full` clean; a clone of the backup has the same refs and SHAs as `git ls-remote` at that time. A second copy (a git bundle of all refs) goes to the owner's backups (Q3). The backup holds the values, so it stays private and is deleted at the end of the retention period (Q4). At S1 this backup is replaced by, or checked against, the S1 mirror taken just before S2. The rollback copy is the S1 pre-S2 mirror (section 10). |
| P4 | Every open branch and PR is listed. | `gh pr list --state open` and `git ls-remote --heads`, each marked merged or open. The list is taken at execution time, not from the dated counts in section 2. On 18 Nov 2026 07:57 SAST the open PRs were #19 (this RFC), #18 (merged at P1) and #11. The owner decides for #11 (Q2) and for #19 (Q9). |
| P5 | Every local copy is listed. | The production checkout and its worktrees; `incidents/local` if it exists (list its commits); every other local clone of this repo. Uncommitted work in a worktree is committed or saved as a patch first. |
| P6 | GitHub settings allow the push. | Branch protection and rulesets on `main` read-only with `gh api`. If any blocks a force-push, the owner allows it for the window and restores it after (section 9, R6). The Pages `cname` is recorded. |
| P7 | The account and origin are correct. | The CHG-2026-066 guard: `GH_TOKEN` from `gh auth token --user GrokForum`, `gh auth setup-git`, and `git remote get-url origin` must match `github.com/GrokForum/publicfunds-sa`. |
| P8 | The replacements file is correct. | Exactly 10 lines (5 values, 5 `doc` lines); every left side occurs exactly once in the pre-PR #18 tree; every right side is a 7-character mask or `null`. |
| P9 | No unexpired `github-pages` artifact has a `workflow_run.head_sha` that still holds the unmasked values, unless the owner has given a GO to delete those artifacts and they have been deleted (Q8). | Confirm the origin URL. Then `GH_TOKEN=$(gh auth token --user GrokForum) gh api --paginate repos/GrokForum/publicfunds-sa/actions/artifacts`. For each artifact with `expired` false and name `github-pages`, compare `workflow_run.head_sha` with the first masked commit (P1), not only `created_at`. Before the rewrite, the SHA must be the first masked commit or a descendant of it (on the then-current `main` history). After S9, accept the SHA if any one of these is true: (1) it is the rewritten first masked commit (the commit-map SHA) or a descendant of that new commit; (2) the S1 pre-rewrite backup shows that the SHA is the first masked commit or a descendant of it; (3) the filter-repo commit-map maps the SHA to the rewritten first masked commit or to a descendant of that new commit. A clean artifact built from a masked commit before the rewrite keeps its old `head_sha`, so (2) and (3) are required: the window may start inside the 24-hour artifact life, and that old SHA would otherwise fail the check just after the force-push. Do not accept an old SHA that the S1 backup shows is not the first masked commit and is not a descendant of it, and do not accept a mapped SHA that is not the rewritten first masked commit and is not a descendant of it. Those are unmasked artifacts. `created_at` may be recorded as supporting evidence; it does not decide the check. If the SHA fails that test, the artifact must already have been deleted under the Q8 GO. Repeat this check immediately before S9 and immediately after S9. |

## 6. Steps (window)

| # | Step | Stop if |
|---|---|---|
| S0 | The owner gives the execution GO for the force-push. The author records the time. | No GO. |
| S1 | Take a fresh mirror (`git clone --mirror`) of GitHub. Record `git ls-remote` (all refs) and `git show-ref` on the mirror (SHA of `main` and of each branch, tag and `refs/pull/*`). This list is the baseline for later steps. Copy or bundle that mirror as the rollback backup, held privately, before S2. If a P3 backup already exists, replace it with this S1 copy, or check that its SHAs match S1 and keep the matching copy. | `main` differs from P1, or the rollback backup SHAs differ from S1. |
| S2 | Run the filter-repo command of section 4 in the working mirror (not in the rollback copy). | Any error. |
| S3 | Verify (section 7), including check 8: a copy of the working mirror whose `origin` points at a bare copy of the S1 pre-rewrite backup. | Any check fails. Then discard the working mirror; nothing on GitHub changed. The rollback backup is unused and stays private. |
| S4 | Tags: `git filter-repo` moved the lightweight tags and wrote new annotated tag objects for the annotated tags (same names, tagger and message). Check that each tag from the S1 list points to the commit that `commit-map` gives for its old commit. | Any tag is missing or wrong. |
| S5 | Unset `remote.origin.mirror` (`git config --unset remote.origin.mirror`), or use `git -c remote.origin.mirror=false` on this push and on S6 and S7. Run the P7 guard. Force-push `main` with a lease: `git push --force-with-lease=main:<old main SHA from S1> origin refs/heads/main:refs/heads/main`. | The lease fails (`main` moved). Then stop and find out why. |
| S6 | Force-push the tags, with the same mirror workaround as S5: `git push --force origin 'refs/tags/*:refs/tags/*'`. | Any tag push fails. |
| S7 | Open branches: force-push each rewritten open branch from the S1 and P4 lists with a lease (and the same mirror workaround). Merged branches from those lists: delete them on GitHub (`git push origin --delete <branch>`). For PR #11 follow Q2. For PR #19 follow Q9. | Any push fails. |
| S8 | Check GitHub: `git ls-remote` shows only the expected refs and the new SHAs, compared with the S1 list through `commit-map` and `ref-map` (open branches kept or deleted as in S7; merged branches deleted; tags remapped; `refs/pull/*` still present at their old SHAs and still advertised). A new `git clone --mirror`, or any fetch of `refs/pull/*`, still downloads the old commits with the values, without a SHA. Hits in those refs are expected under this plan; confirmation that the owner accepts that leftover exposure is open (Q7). Branches and tags must have 0 hits. | Any hit in a branch or tag, or a branch or tag from S1 is missing or has the wrong SHA. |
| S9 | Repeat the P9 artifact check (`gh api --paginate`, and `workflow_run.head_sha` against the first masked commit, not only `created_at`). Pages: wait for the Pages build of the new `main` (`gh api repos/GrokForum/publicfunds-sa/pages/builds/latest` status `built`). Run `scripts/check_live.py`. Check that `/CNAME` and `/robots.txt` on the live site are the same bytes as before and that the Pages `cname` setting is unchanged. Repeat the P9 artifact check after the build, using the after-S9 rule in P9 (old masked `head_sha` values that the S1 backup or the commit-map shows are the first masked commit or a descendant of it also pass; unmasked artifacts do not). | Build fails, `check_live` is not OK, or an unexpired `github-pages` artifact fails the after-S9 P9 rule. Then decide between rollback (section 10) and a fix. |
| S10 | If `incidents/local` exists on the current production checkout, export its commits with `git format-patch main..incidents/local` and check the patches with `grep -c -F -f` (0 hits expected) before the checkout is moved aside. Then re-clone the production checkout: move it aside, clone the new repo to the same place, move the git-ignored `data/` and other git-ignored state across, and check the CHG-2026-066 guard and `git status`. Re-create the worktrees that are still needed from the new clone. Start the review app again and check its health. If patches were exported, apply them in the new clone on a new `incidents/local` from the new `main`, in its own worktree. If `incidents/local` did not exist, the nightly creates it when it needs it. | The guard fails, `data/` is not complete, or the patches do not apply or hold a value. |
| S11 | (Removed as a separate export step; the `incidents/local` export and apply are in S10.) | — |
| S12 | The orchestrator resumes the nightly routine. The next nightly must pass step 0 (fast-forward from the new `origin/main`). | The routine stays paused until S10 passes. |
| S13 | The author commits one records change (section 8): Result of this record, change-log row, STATUS line and the SHA mapping note. It goes through the normal PR process. | — |
| S14 | The owner or the orchestrator acts on the earlier private repository, with the account that owns it, by the owner's choice at Q5 (section 6.1). The GrokForum token cannot see that repository (HTTP 404, section 2). | No owner choice at Q5. |

The window from S1 to S12 is short: the repo is about 3.3 MB, so the rewrite itself takes seconds. Plan 2 hours, in daytime, not within 2 hours of 03:00 SAST, and not before the Q8 artifact condition is met (section 5, P9). S14 is a separate step. It is not part of the short public window.

## 6.1 The earlier private repository

This repository is the private repo from before CHG-2026-050. It is not GrokForum/publicfunds-sa.

Facts measured by the author on 18 Nov 2026 (section 2.1):

- A local clone holds the values in 245 of 283 commits.
- The GrokForum token gets HTTP 404 for that repository. Whether it is still on GitHub (private) or already deleted is **[unverified]**.

### Options (Q5; the owner chooses)

| Option | Action | Effect |
|---|---|---|
| a | Delete the repository on GitHub, after a verified backup if the owner wants one. | The content is then gone from GitHub's normal access. |
| b | Run the same `git filter-repo` rewrite and force-push, with the account that owns the repository. | The values are removed from branches and tags that a push can change. If that repository has `refs/pull/*`, those refs stay advertised and still name the old commits with the values, as in R8. Cached views may also remain. |
| c | Archive the repository as it is, and keep it private. | The values stay in its history. Access stays limited to those who can see a private repository. |

### Step (S14)

Steps on this repository need the account that owns it. The owner or the orchestrator must run them. The GrokForum token cannot see the repository (HTTP 404).

1. The owner answers Q5 (option a, b or c).
2. The owner or the orchestrator runs the chosen option with the owning account.
3. If the owner wants a backup first (option a, and also wise for b), take a verified mirror or bundle and store it privately, as in P3 and Q3, with retention as in Q4.

S14 can run after the public window, once Q5 is answered.

This change does not act on local clones of the earlier private repository on the author's computer. Those stay under Q6.

## 7. Verification of the rewritten mirror (S3)

All checks run on the working mirror before any push to GitHub.

1. `git grep -c -F -f <private list> $(git rev-list --branches --tags)`: 0 hits. Also with `-i`: 0 hits.
2. The tree of the new `main` is byte-identical to the tree of the old `main`: `git rev-parse <new main>^{tree}` equals `git rev-parse <old main>^{tree}`. The live data is already masked, so nothing at the tip changes.
3. For each pair in `commit-map`, `git diff --name-only <old> <new>` lists only the 4 award files (or nothing). A JSON check of those files shows that only the `supplier` and `doc` cells of the 5 rows differ, and that they equal the values of the masked tip.
4. The number of commits on `main` and on each branch matches the S1 list. Author, committer, dates and messages are the same.
5. `git fsck --full` is clean.
6. The full test suite on a checkout of the new `main` gives the same counts as on the old `main`.
7. `CNAME`, `robots.txt` and `public-data/v1/manifest.json` are the same bytes as on the old `main` (follows from check 2).
8. Test the exact S5–S7 push commands, not against GitHub. Take a copy of the working (rewritten) mirror and point its `origin` at a bare copy of the S1 pre-rewrite backup, so the `remote.origin.mirror` flag still applies to that `origin`. A bare copy of the rewritten mirror, added as a temporary remote, is not a valid test: it reports `Everything up-to-date`, and the mirror flag applies only to `origin`. That failure was reproduced in a scratch directory on 18 Nov 2026. Then all of these must hold, and the test stops if any one does not:

   - The plain S5 lease and refspec push must fail with `fatal: --mirror can't be combined with refspecs`.
   - The same S5 command with `git -c remote.origin.mirror=false` (or after `git config --unset remote.origin.mirror`) must show `forced update`.
   - The S6 tag push (`git push --force origin 'refs/tags/*:refs/tags/*'`) must fail with the same fatal error, and with `-c remote.origin.mirror=false` must show `forced update`.
   - The S7 deletes (`git push origin --delete <branch>`) must fail with the same fatal error, and with `-c remote.origin.mirror=false` must show the delete.

   Discard the copies after the test.

## 8. Commit map and old SHAs in records

- `filter-repo/commit-map` (old SHA to new SHA) and `filter-repo/ref-map` are copied to the private store, held privately on the author's computer, with the S1 rollback backup. They do not go into git, because the old SHAs point to commits that `refs/pull/*` still name. Those refs stay advertised, so a mirror clone or a fetch of them still downloads the values.
- Records that cite old SHAs (change records, the change-log, STATUS, PR texts, the private approval record) stay as they are. They are history.
- S13 adds one mapping note to this record and to STATUS: SHAs cited in records before the rewrite date refer to the history before CHG-2026-068; the private commit map gives the new SHA of each one. The snapshot tags keep their names, so a record that cites a tag still works.
- The live manifest's `build.code_commit` cites an old SHA until the next nightly writes a new one. This is expected; `check_live` does not check it.

## 9. Risks

| # | Risk | Likelihood × impact | Mitigation |
|---|---|---|---|
| R1 | Links to old commits break (records, PR pages, chats, the old `code_commit`). | 5 × 2 = 10 | Accepted. Tags keep their names; the private commit map and the S13 note map old to new. Pull-request diffs that cite old SHAs can still show the values (R8). |
| R2 | The nightly runs in the window and pushes a commit that the force-push then removes, or it starts from the old history. | 2 × 4 = 8 | P2 pauses the routine. S5 uses `--force-with-lease`. A nightly that starts on the old checkout stops at step 0 with `ACTION: checkout update failed`, because `--ff-only` fails on the rewritten `origin/main`, so it cannot publish or push. |
| R3 | A clone made before the rewrite pushes the old history back (recontamination). | 2 × 5 = 10 | The repo has 1 collaborator and 0 forks. All local copies are listed (P5) and re-cloned or retired (Q6). No push from an old clone. S8 and the next week's checks look for hits again. |
| R4 | The live site is down or stale during the Pages rebuild. | 2 × 2 = 4 | The tree is unchanged, so the build has the same files. The rebuild takes minutes. S9 runs `check_live`. Rollback if the site does not come back. |
| R5 | The custom domain is lost. | 1 × 4 = 4 | `CNAME` is in the tree and does not change (section 7, check 7). S9 checks the Pages `cname` setting and `/CNAME` on the live site. |
| R6 | Branch protection or a ruleset blocks the force-push. | 1 × 2 = 2 | Today there is none (section 2). If one exists at P6, the owner allows force-pushes on `main` for the window (Settings, Branches or Rules) and restores the setting after S9. |
| R7 | A replacement hits text that is not one of the 5 cells. | 1 × 3 = 3 | Quoted whole-string matches; each left side occurs once (P8); section 7 check 3 limits the diff to the 5 rows. |
| R8 | After the rewrite, `refs/pull/*` stay advertised (22 at the 18 Nov 2026 07:58 SAST count). Any `git clone --mirror`, or any fetch of those refs, downloads the old commits with the values, without a SHA. Cached views of old SHAs also remain. | 5 × 3 = 15 | The values are still removed from all branches and tags that a push can change. Owner decision relayed 18 Nov 2026 07:51 SAST: no GitHub Support purge request. Confirmation that the owner accepts this leftover exposure is open (Q7). |
| R9 | GitHub's signatures on 18 web-merge commits are lost. | 5 × 1 = 5 | Accepted (GitHub's guide). The "18" figure is the dated finding in section 2.1; S1 records the number at execution. |
| R10 | Open PR #11 loses review comments on the old diff. | 3 × 1 = 3 | The owner decides at Q2: keep it open on the rewritten branch, or close it and open a new PR. |
| R11 | The private backup keeps the values longer than needed. | 2 × 3 = 6 | Mode 0600, off git, deleted at the end of the retention period (Q4). The rollback backup is the S1 pre-S2 copy. |
| R12 | Unexpired `github-pages` Actions artifacts hold the unmasked award files outside git. | 5 × 3 = 15 | P9 and the S9 checks fail if any unexpired artifact fails the P9 rule. After S9, a clean artifact whose old `head_sha` is the first masked commit or a descendant of it (on the S1 backup, or mapped by the commit-map to the rewritten first masked commit or a descendant of it) passes; an unmasked artifact does not. Q8: wait at least 24 hours after the last unmasked Pages build, or delete the unmasked artifacts through the API under an owner GO. |
| R13 | A force-push from the mirror clone fails because `remote.origin.mirror` is true. | 5 × 2 = 10 | Reproduced (section 2.2). S5 unsets the flag or uses `git -c remote.origin.mirror=false`. Section 7 check 8 points a copy of the working mirror's `origin` at a bare copy of the S1 pre-rewrite backup and requires a fatal error, then `forced update` (and the same for S6 and S7). A temporary remote that is a bare copy of the rewritten mirror is not used; that method reports `Everything up-to-date`. |

## 10. How to revert

- **While the S1 private mirror backup is kept (Q4):** from that backup (the copy taken just before S2, with SHAs that match S1), run the P7 guard and `git push --force --mirror origin`. GitHub refuses the `refs/pull/*` updates (read-only); that is expected and harmless. A `--mirror` push from the backup also deletes any branches created after S1. Then check `git ls-remote` against the S1 ref list, wait for the Pages build and run `check_live`. Re-clone the production checkout from GitHub again. A nightly commit made after the force-push would be lost, so a clean restore (no later work lost) is only for the paused window, before S12. After S12, a restore is still possible until the backup is deleted, but it overwrites any commits made after the rewrite.
- **After the backup is deleted, there is no rollback.** A push of the old history would publish the values again and undo this change.
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
| `incidents/local` (never pushed) | Exported and re-applied in S10 if it exists. |
| Masks and the export-blocking scan (CHG-2026-067) | Unchanged; they keep the values out of every new publish. |

## 12. Approval

1. Two independent reviewer PASSes on the exact head of this RFC.
2. The owner's GO naming that head. This approves the plan only.
3. At execution time, a separate explicit owner GO for the force-push (S0), because it overwrites published history. The author never force-pushes without it.
4. If Q8 is "delete the artifacts", a separate owner GO is required for the artifact deletions, before P9 can pass by that route.

## 13. Questions for the owner

Owner decision relayed 18 Nov 2026 07:51 SAST: the remaining questions will be answered as the work proceeds.

### Open

| # | Question | Author's recommendation |
|---|---|---|
| Q1 | When is the window? | The first daytime period after the first masked nightly that is also at least 24 hours after the last unmasked Pages build (unless the owner chooses deletion at Q8). |
| Q2 | PR #11 (open draft): keep it open on the rewritten branch, or close it and open a new PR after the rewrite? | Close and reopen, so no review comment hangs on an old diff. |
| Q3 | Where do the owner's backups of the mirror go? | A git bundle in the owner's private backup store, not in any repo. |
| Q4 | How long are the mirror backup and the commit map kept? | 7 days after the force-push. Then delete the backup; keep only the commit map (SHAs only). The push-back rollback is available only while the backup is kept. |
| Q5 | The earlier private repository (before CHG-2026-050) also holds the values. Delete it on GitHub after a verified backup if wanted (option a), rewrite and force-push it with the owning account (option b), or archive it as it is, private (option c)? | See section 6.1 for the effects. The author cannot act with the GrokForum token (HTTP 404). The owner or the orchestrator must run the chosen option. |
| Q6 | Retire the other local repos and worktrees of this repo and of the earlier repo on the author's computer? | Yes, after S10, as a separate step with its own GO, because it deletes local data. |
| Q7 | After the rewrite, `refs/pull/*` stay advertised (22 at the 18 Nov 2026 07:58 SAST count). Any `git clone --mirror`, or any fetch of those refs, downloads the old commits with the values, without a SHA. Cached views of old SHAs also remain. Does the owner accept this leftover exposure? | The 07:51 SAST decision remains: no GitHub Support purge request. The earlier wording that the leftover was SHA-only, and that the owner had accepted that wording, was inaccurate. Owner answer, 18 Nov 2026 09:48 SAST, given in the orchestrator's chat and relayed to the author; the author did not see the owner's words first-hand: the owner accepted this leftover exposure until the source repositories go private. Owner statement, 18 Nov 2026 09:50 SAST, given in the PublicFunds chat: all the source repositories, including this data repository, go private when the merged site that holds all 4 public datasets goes live. |
| Q8 | Unexpired `github-pages` artifacts hold the values outside git. Wait at least 24 hours after the last unmasked Pages build so they expire, or delete the unexpired artifacts that fail the P9 rule (unmasked `head_sha` values), through the API, under an owner GO? | Wait 24 hours if the window can be that late. If the window must start earlier, delete the unmasked artifacts under a separate owner GO, then re-run P9. After S9, do not delete a clean artifact that only still has the old masked `head_sha`. |
| Q9 | How is PR #19 (this RFC, branch `chg-2026-068-history-rewrite-rfc`) handled: merged or closed before the window, or rewritten like #11? | Merge it before the window, so the approved plan is on `main` before the SHAs change. If it is still open at P4, close it after the records are on `main`, or rewrite it like #11 (Q2). |
| Q10 | CHG-2026-069 (branch `chg-2026-069-public-site-repo`, RFC head `3756dcd31dd53fe64772492be66be678a2f5bffd`) proposes a separate public site repository and, later, making the data repository private. In what order do those changes and this rewrite run? Does this rewrite still run? | See section 16. Owner answer, 18 Nov 2026 09:48 SAST, given in the orchestrator's chat and relayed to the author; the author did not see the owner's words first-hand: the history rewrite is dropped; making the data repository private is enough. Owner statement, 18 Nov 2026 09:50 SAST, given in the PublicFunds chat: all the source repositories, including this data repository, go private when the merged site that holds all 4 public datasets goes live. This record is withdrawn and was not executed. |

## 14. Seen, not touched

- The name words of 2 of the 5 values also occur in other untitled supplier cells. They belong to the later review of short supplier strings.
- One tag (`snapshot-2026-11-01-1944`) exists in a local clone and is not on GitHub. It goes away with the re-clone.

## 15. Testing of this record

- Docs only. The full test suite ran on the branch (counts in the Revisions section).
- The added lines were checked for the 5 values (`grep -c -F -f` on the private list: 0 hits), for names, ids, e-mail addresses, private paths and stale words.

## 16. Effect of CHG-2026-069

CHG-2026-069 (draft RFC, branch `chg-2026-069-public-site-repo`, head `3756dcd31dd53fe64772492be66be678a2f5bffd`) plans a separate public GrokForum repository that holds only the built site files, with fresh history and no data-repository `refs/pull` residue, and a later change that makes GrokForum/publicfunds-sa private. That later visibility change is not part of CHG-2026-069.

This rewrite is not automatically cancelled. The values stay in the data repository until a rewrite runs, or until that repository is no longer public. A private repository still keeps the values in its history and in its `refs/pull/*` for anyone with access.

Options (Q10; the owner chooses; this record does not decide). They match the options in CHG-2026-069 section 9:

| Option | Order | Effect on the public | Effect on this rewrite and Q7 |
|---|---|---|---|
| a | Do the CHG-2026-069 site-repository change first, move the hostname, then make the data repository private as a later change. Defer or drop this history rewrite. | Once the data repository is private, the advertised website has fresh history and no `refs/pull` residue, and the public cannot clone the data repository or fetch its `refs/pull/*`. | The public leftover in Q7 becomes moot. Q7 would be reframed as: does the owner accept that residual for anyone with access, or still want a rewrite? |
| b | Do the site-repository change first (and later make the data repository private), and still run this rewrite, before or after the repository is private. | The public site is as in (a). Branches and tags of the data repository no longer hold the values, for anyone with access. `refs/pull/*` may still hold them for anyone with access (no GitHub Support purge). | This rewrite still runs. Q7 is about the residual for anyone with access, not about a public `ls-remote`. |
| c | Run this rewrite first, as this RFC now plans, then the site-repository change, then the later private change. | Until the data repository is private, the public data repository has rewritten branches and tags, and the advertised `refs/pull/*` residual stays public until visibility changes. | Q7 stays as it is until the data repository is private. |

Author's recommendation, not a decision: option a for the order (site repository first, hostname cutover, data repository private later), because that ends the public `refs/pull` exposure without a force-push of the data repository. Whether this rewrite still runs (a versus b) is left to the owner. Option c remains available if the owner wants the rewrite while the data repository is still public. Q7 stays open until the owner answers.

## Revisions

- Draft (18 Nov 2026): first version. Full test suite on the branch: 961 passed, 61 skipped. Added lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.
- Rev 2 (18 Nov 2026): Owner decision relayed 18 Nov 2026 07:51 SAST: no GitHub Support purge request; cached views and `refs/pull/*` stay reachable by direct SHA, and the owner accepted this. Removed the Support step (old S14) and Appendix A. Restated the rollback window and Q4 so they are not bounded by a purge. Closed Q7. Added section 6.1 and step S14 for the earlier private repository (Q5 stays open: delete, rewrite, or archive). Reviewer B (records): this record now states that the 07:37 SAST decision supersedes the CHG-2026-067 Q4 answer, and that the 07:37 and 07:51 decisions were given in the PublicFunds chat and relayed to reviewers, who did not hear them first-hand. Reviewer A (on `4871d87d`, PASS_WITH_CONCERNS): (1) S5–S7 now unset `remote.origin.mirror` or use `git -c remote.origin.mirror=false`; section 7 check 8 tests the exact push commands against a local bare copy (failure and both workarounds were reproduced). (2) P9 and S9 check unexpired `github-pages` artifacts; Q8 asks whether to wait 24 hours or delete them under an owner GO (7 unexpired artifacts, about 2.3 MB each, 1-day expiry, measured 18 Nov 2026 07:57 SAST). (3) Execution steps compare against the S1 `ls-remote` list; the 19-branch, 20-`refs/pull` and 109-commit figures stay only as dated findings (a 07:58 SAST recount already differed). (4) Q9 states how PR #19's branch is handled. (5) The rollback backup is the S1 mirror taken just before S2, or a P3 copy checked against those SHAs. (6) The `incidents/local` patch export is in S10, before the checkout is moved aside. (7) Section 4 states that in a mirror clone `--sensitive-data-removal` skips its own fetch, that the skip is harmless, and that `origin` is kept (installed git-filter-repo 2.47.0). Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 07:56 SAST). Added and changed lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.
- Rev 3 (18 Nov 2026): Reviewer A (on `08db5abd`, PASS_WITH_CONCERNS). (1) Section 7 check 8 now takes a copy of the working mirror and points its `origin` at a bare copy of the S1 pre-rewrite backup. The plain push must fail with the fatal mirror/refspec error, and `git -c remote.origin.mirror=false` must show `forced update`. S6 tag pushes and S7 deletes are covered the same way. A bare copy of the rewritten mirror added as a temporary remote is not used: it reports `Everything up-to-date`, and the mirror flag applies only to `origin` (reproduced in a scratch directory). (2) Leftover exposure stated accurately in section 1, the GitHub-guide note, section 3.1, S8, R8, Q7, STATUS and the change-log: `refs/pull/*` stay advertised (22 at last count), so any `git clone --mirror` or fetch of those refs downloads the old commits with the values, without a SHA. Goal wording is "in no branch or tag", not "in no commit". The 07:51 decision remains: no Support purge request. Q7 is open: record the owner's acceptance only when the owner confirms this accurate residual. (3) P9 uses `gh api --paginate` and compares each artifact's `workflow_run.head_sha` with the first masked commit, not only `created_at`. (4) Section 10 and the rollback field note that a `--mirror` push from the backup also deletes any branches created after S1. (5) S2 no longer saves the "First Changed Commit(s)" line or the `refs/pull` count for a Support request; Q7 wording was tidied and moved back to the open list. Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 08:09 SAST). Added and changed lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.
- Rev 4 (18 Nov 2026): Reviewer A (on `ace55d61`, records concern). After S9, P9, S9, R12 and Q8 also accept an old `head_sha` that the S1 backup shows is the first masked commit or a descendant of it, or that the filter-repo commit-map maps to the rewritten first masked commit or to a descendant of it. A clean artifact built from a masked commit before the rewrite therefore still passes if the window starts inside the 24-hour artifact life. An unmasked artifact still fails. Added section 16 and Q10 on CHG-2026-069 (RFC head `3756dcd3`): order, whether this rewrite still runs, and how Q7 would be reframed; the owner's choice stays open. Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 08:20 SAST). Added and changed lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.
- Rev 5 (18 Nov 2026): records only, after `main` `70da3065` (PR #18) was merged into the branch. Owner answers of 18 Nov 2026 09:48 SAST, given in the orchestrator's chat and relayed to the author; the author did not see the owner's words first-hand: the owner issued a GO for the merge of PR #19 at `969b1b66`, with a snapshot tag; Q10, the history rewrite is dropped; Q7, the owner accepted the leftover `refs/pull/*` exposure until the source repositories go private. Owner statement, 18 Nov 2026 09:50 SAST, given in the PublicFunds chat: all the source repositories, including this data repository, go private when the merged site that holds all 4 public datasets goes live. The Status field is **Withdrawn (not executed)**. Full test suite on the branch: 1060 passed, 61 skipped (18 Nov 2026 10:00 SAST). Added and changed lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.

## Post-implementation review

- Outcome: not started (draft).
