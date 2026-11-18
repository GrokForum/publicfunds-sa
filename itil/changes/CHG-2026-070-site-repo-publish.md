# CHG-2026-070: Nightly publish to the site repository (CHG-2026-069 step S11)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 18 Nov 2026 13:04 SAST, in the orchestrator's chat: option b (S11 as its own change before the switch window; option a as the fallback). |
| Status | Built in DEV on branch `chg-2026-070-site-repo-publish` from `main` `432a455e` (18 Nov 2026). This record is not a merge GO and not a deploy GO. |
| Type | **Normal-high** (`itil/change-enablement.md`: the publishing pipeline, distribution, the refresh skill and the routine). Reviewers: the orchestrator and a critic (owner update, 18 Nov 2026). A merge needs their review of the exact head and the owner's GO naming that head. The owner GO for this change also grants the standing approval for nightly site pushes to `main` of GrokForum/publicfunds-site (CHG-2026-069 Q2). The deploy follows the merge, in the CHG-2026-069 window, after S9 and before the 20 Nov 2026 03:00 SAST nightly. |
| Environment | DEV: local worktree and temporary local git repositories for the tests. PROD at the deploy: the nightly routine pushes to `main` of GrokForum/publicfunds-site. Pre-change `main` is `432a455ed76c181c02dd81bce5f8c530d238d5ab`. |
| CIs affected | New CI-121 (`thusa/site_repo.py`, `scripts/publish_site_repo.py`); `scripts/nightly_check_live.py` (`RAW_URL`, site push input); CI-118 (`docs/bot/live-skill/publicfunds-refresh.MASTER.md`, `routine-nightly.PROPOSED.md`, `README.md`, new `publicfunds-refresh.PREVIOUS-CHG-2026-066.md`); `tests/test_site_repo_publish.py` (new), `tests/test_nightly_check_live.py`, `tests/test_live_skill_snapshot.py`, `tests/test_robots_noindex.py`, `tests/test_site_draft_privacy.py`; this record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md`. At the deploy: the live refresh skill and the nightly routine prompt (CI-004), and one private config file off git. |
| Linked records | CHG-2026-069 (step S11, sections 3, 4.1, 4.2, 4.4, 4.5, R11, Q2); CHG-2026-065 and CHG-2026-066 (skill master and routine prompt pattern); CHG-2026-061 (`nightly_check_live.py`); CHG-2026-067 (titled-supplier masks, `doc` null); CHG-2026-063 (robots). |
| Rollback | See "How to revert". Git is the rollback for the repo; no `.bkp` files. The site repository keeps serving the last published tree. |

## 1. What and why

CHG-2026-069 moves the public site to GrokForum/publicfunds-site. After the custom domain moves (S5 to S9), the nightly must publish to that repository, or the live site keeps the data of the last site publish. Step S11 of CHG-2026-069 is that change. The owner chose to prepare S11 as its own change, so that it can go live in the same window as the domain move (option b). If the review and the owner GO are not done by 19 Nov 2026 15:00 SAST, the window runs under option a: one expected failed live check and stale data until S11 is deployed.

This change does exactly the S11 scope: a site publish helper, the live check wrapper with the site push result as an input and `RAW_URL` on the site repository, the tests, and the proposed skill and routine text. It does not run the helper, does not push to either repository, and does not change GitHub settings.

## 2. Changes

| File | Change |
|---|---|
| `thusa/site_repo.py` (new) | The site publish helper. Guards: the data checkout is on `main`, its origin is GrokForum/publicfunds-sa, and remote `main` of the data repository is the local HEAD (the data push has finished, gate 2). The site-remote guard accepts only `https://github.com/GrokForum/publicfunds-site(.git)` (gate 6). It builds the staging tree from the section 3 allowlist, read from the data commit at HEAD (site pages and every file under `public-data/v1/`), and writes the expected `CNAME` (`publicfunds.grokforum.site` plus LF) before the gates. Gate 3: 0 hits for the private list (exact and case-insensitive) in every file, the titled-person rule and `doc` null on masked rows in every award file. Gate 4: the export's public-safety check on every JSON file, no SA ID numbers, no e-mail address other than a role mailbox at the site domain or its parent, no phone number on the site pages. Gate 5: the allowlist test. Gate 8: it fetches the remote tip and accepts only the recorded last tip, or that tip plus exactly one commit with a single parent that only adds `CNAME` (mode 100644) with the bytes `publicfunds.grokforum.site`, with or without one trailing LF. Option a: `git write-tree` of the scanned staging tree, `git commit-tree <tree> -p <accepted tip>`, the tree-hash check, a push without force, then the new tip is recorded privately (mode 0600), with an optional private bundle. |
| `scripts/publish_site_repo.py` (new) | Command-line entry for the helper. It takes no arguments. Exit 0: `site_publish: pushed <commit>` or `site_publish: no change; nothing pushed`. Exit 3: `ACTION: site publish blocked (...)`, nothing pushed. Exit 4: `ACTION: site publish failed (...)`. |
| `scripts/nightly_check_live.py` | `RAW_URL` moves to `https://raw.githubusercontent.com/GrokForum/publicfunds-site/main/public-data/v1/manifest.json`. New required inputs `--site-exit <code, or not-run>` and `--site-log`. It runs the live check when the site pushed, when the data pushed, and also when the site push was blocked, failed, gave no known line or did not run after a data exit 0, so a stale live tree is visible. It skips only when neither push pushed. A site push after a failed data publish is a failed check (exit 2). The other exit codes are unchanged. |
| `docs/bot/live-skill/publicfunds-refresh.MASTER.md` | 7 edits (L to R) on the CHG-2026-066 text: step 4 is data push, then site push, then the live check; the site push scope under the owner's standing approval for the site repository; the site push block (only after a data publish exit 0, exit codes 0, 3 and 4, the ACTION lines, never forced or by hand); the new wrapper command; the `site_publish:` line in the report; the exit 3 wording; a failed or blocked site push does not skip the backup; step 6 names the site push. |
| `docs/bot/live-skill/routine-nightly.PROPOSED.md` | The proposed routine prompt: step 4 order, the site push scope, the site ACTION lines in the quiet rule and in the report order, the site push exit code in the report. |
| `docs/bot/live-skill/publicfunds-refresh.PREVIOUS-CHG-2026-066.md` (new) | Byte copy of the CHG-2026-066 master that is live (sha256 `c80a5133…`), as the rollback text. |
| `docs/bot/live-skill/README.md` | The new file, the step 4 order, the private config deploy step, the drift check and the rollback. |
| `tests/test_site_repo_publish.py` (new) | 65 tests with temporary local bare repositories and no network. |
| `tests/test_nightly_check_live.py` | The site push input and its matrix; `RAW_URL` on the site repository. |
| `tests/test_live_skill_snapshot.py` | The 7 edits as `CHG070_EDITS`; the order check includes the site push; the drift check also accepts the previous master; checks for the site push rules and their must-fail cases. |
| `tests/test_robots_noindex.py`, `tests/test_site_draft_privacy.py` | The expected `CNAME` and the site domain come from `thusa/site_repo.py`. The data-repository `CNAME` file is checked only while it exists, so the tests pass before and after that file is removed. |

The private list, its path, the tip file and the private config are not in git. The helper reads them from `PF_TITLED_VALUES_FILE`, `PF_SITE_TIP_FILE` and `PF_SITE_BUNDLE_DIR`, or else from `~/.config/thusa/site-publish.json`. If it cannot read the list or the tip, the run is blocked.

## 3. ACTION lines and the live check

| Data publish | Site push | Site ACTION line | Live check (wrapper) |
|---|---|---|---|
| exit 0, pushed | pushed or no change | none | runs |
| exit 0, nothing to commit or timestamps only | pushed (for example a new `CNAME` tree) | none | runs |
| exit 0, nothing to commit or timestamps only | no change | none | skipped (exit 3) |
| exit 0 | blocked (exit 3) | `ACTION: site publish blocked (...)` | runs (stale tree visible) |
| exit 0 | failed (exit 4 or other) | `ACTION: site publish failed` | runs (stale tree visible) |
| exit 3 or 4 | did not run (`not-run`) | none | skipped (exit 3), as before |
| other non-zero | did not run (`not-run`) | none | failed check (exit 2), as before |

The site ACTION line comes after the data-publish ACTION lines and before the live-check lines (CHG-2026-069 section 4.5). The backup still follows the live check; a failed or blocked site push does not skip it.

## 4. Deploy (in the CHG-2026-069 window, after S9, before 20 Nov 2026 03:00 SAST)

1. Merge at the exact head after the review and the owner's GO naming that head. Tag the snapshot and run `check_live`.
2. In `/workspace/publicfunds`, the nightly checkout updates by its own step 0 fast-forward. The deploy does not edit that checkout.
3. Write the private config file `~/.config/thusa/site-publish.json` (mode 0600, never in git) with these fields: `titled_values_file` (the private list of titled values, one per line); `tip_file` (a private file that holds one 40-hex commit id plus LF, written by the S3 run with the first published tip, and rewritten by the helper after each site push); and, if wanted, `bundle_dir` (a private folder for a bundle of each published tip).
4. Save the live routine prompt word for word in the private deploy notes. Copy the master to the live skill path byte for byte, check `sha256sum` and `cmp`, and set the routine prompt from `routine-nightly.PROPOSED.md` with the agent id filled, in the same step (as in CHG-2026-065 and CHG-2026-066).
5. Record in `changes/CAB-DECISION.md` the standing approval for nightly site pushes to GrokForum/publicfunds-site that the owner GO for this change grants (CHG-2026-069 Q2). Record the deploy time, the sha256 and who deployed in the next change record.

The first site push after the deploy is the 20 Nov 2026 03:00 SAST nightly. It accepts the S3 tip plus the GitHub `CNAME` commit of S6.

## 5. Testing

- Full test suite on the branch: 1170 passed, 61 skipped (18 Nov 2026 13:17 SAST).
- `tests/test_site_repo_publish.py`: gate 8 (the recorded tip; the tip plus a `CNAME`-only commit with and without LF; CRLF, CR, two LFs, another domain, an extra line, a leading space, an extra file, executable mode, a modified `CNAME`, two commits and an unknown tip are rejected; a remote with no `main`; a failed fetch), the tree-hash check, staging with `CNAME` with and without a data-repository `CNAME` file, the allowlist, the mask scan and POPIA failures that block the push, a refused push, a tip that was not recorded, the private bundle, the guards.
- `tests/test_nightly_check_live.py`: 83 passed, including the site push matrix in section 3.
- A dry run on 18 Nov 2026, in temporary copies only (no push to GitHub): the export of this branch, from a copy of the warehouse, into a scratch clone; the helper with the real private list against a local bare repository that held a root commit and a GitHub-style `CNAME` commit without LF. Result: the gates passed, 27 files, `site_publish: pushed`, then `site_publish: no change; nothing pushed` on the second run. The same helper on today's `main` data (before the first masked nightly) was blocked by the mask scan in 4 award files. The scratch copies were deleted.

## 6. Risk

| Risk | Score | Control |
|---|---|---|
| The helper pushes a tree with an unmasked value or a file that is not on the allowlist. | 2 × 5 = 10 | Gates 3 to 5 on the exact tree that is pushed; the tree-hash check; the tests. |
| GitHub's S6 commit, or any other remote commit, is parented or rides along (CHG-2026-069 R11). | 2 × 4 = 8 | Gate 8 accepts only the recorded tip or that tip plus one `CNAME`-only add with the expected bytes; the tree is built from the staging files only. |
| The nightly site push is blocked or fails after the domain move. | 3 × 3 = 9 | The ACTION line leads the report; the live check still runs, so a stale tree shows as WARN or BREACH; the site keeps serving the last published tree. |
| The tip is pushed but not recorded. | 1 × 3 = 3 | `ACTION: site publish failed (pushed <commit>, but the tip was not recorded)`; the next run is blocked by gate 8 until the tip is recorded by hand. |
| The new wrapper runs with the old skill, or the old wrapper with the new skill. | 2 × 3 = 6 | `--site-exit` and `--site-log` are required, so the new wrapper with the old command line is a failed check (exit 2). The skill, the routine and the code change in one deploy. |

## 7. How to revert

- Repo: `git revert` of the merge commit of this change. `RAW_URL` and the wrapper go back to the data repository.
- Skill and routine: copy `docs/bot/live-skill/publicfunds-refresh.PREVIOUS-CHG-2026-066.md` byte for byte to the live skill path, and write back the routine prompt saved in the private deploy notes at this deploy, in the same step.
- The site repository keeps serving the last published tree. Nothing is deleted. The private config file can stay; nothing reads it after the revert.

## 8. Open items

- Q2 of CHG-2026-069: the owner GO for this change also grants the standing approval for nightly site pushes to GrokForum/publicfunds-site; the deploy records it in `changes/CAB-DECISION.md`. The token scope stays open. The helper uses the GrokForum account through `GH_TOKEN` from the step 0 guard. A token that can write only to the site repository is **[unverified]** as set up.
- The S3 run writes the first published tip to the file that the `tip_file` field names: one 40-hex commit id plus LF. Gate 8 blocks every site push if that file holds anything else.

## 9. Seen, not touched

- `scripts/check_live.py` keeps its default site URL. No change is needed.
- The data-repository `CNAME` file stays until a later change removes it.

## Approval

Reviewers: orchestrator and critic. Owner GO in the orchestrator's chat, naming the merged head (recorded in the deploy record).

## Post-implementation review

- Outcome: not started.
