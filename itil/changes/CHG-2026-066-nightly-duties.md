# CHG-2026-066: Nightly duties of the routine prompt of 17 Nov 2026 in the master skill and the proposed routine prompt

| Field | Value |
|---|---|
| Requested by / date (SAST) | The orchestrator held the CHG-2026-065 deploy on 17 Nov 2026 (as reported to the author (PublicFunds)): the proposed pair (master skill and routine prompt) did not have all the duties of the routine prompt that was live then. This record is not a merge GO and not a deploy GO. |
| Status | Built in DEV on branch `chg-2026-066-nightly-duties` from `main` `ad850d92` (17 Nov 2026; the merge of PR #15, CHG-2026-065, exact head `dd52775a`, 18:02 SAST, tag `snapshot-2026-11-17-1802`). |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline). After the deploy, the nightly routine runs these steps. A merge needs two reviewer PASSes on the exact head and the owner's GO naming that head. The deploy follows the merge. |
| Environment | DEV (local worktree). Pre-change `main` is `ad850d92dd3ea85bf75486f859219bed3419cbaa`. The merge changes only repo files. The live skill and the routine prompt are outside git and change only at the deploy. |
| CIs affected | CI-118 (`docs/bot/live-skill/publicfunds-refresh.MASTER.md`, `docs/bot/live-skill/routine-nightly.PROPOSED.md`, `docs/bot/live-skill/README.md`); `tests/test_live_skill_snapshot.py`; `tests/test_popia_candidate_export.py`; this record; the CHG-2026-065 record (merge facts); `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md`. At the deploy: the live refresh skill and the nightly routine prompt (CI-004). |
| Linked records | CHG-2026-065 (PR #15, merge `ad850d92`), CHG-2026-061, CHG-2026-044 (state backup, appendix A), CHG-2026-041 (publish guard line), CHG-2026-025 (step 0), CI-110, CI-114, CI-116 |
| Rollback | See "How to revert". Git is the rollback for the repo; no `.bkp` files. |

## What and why

Before the CHG-2026-065 deploy, the orchestrator read the routine prompt that was live on 17 Nov 2026 and kept it, word for word, in the private deploy notes (mode 0600, outside git). The CHG-2026-065 master skill and proposed routine prompt left out some of its duties, so the deploy was held. This change compares the two, duty by duty, and puts every duty into the master skill or the proposed routine prompt. The saved prompt is not copied or quoted in git; the tests hold duty names and short marker strings only.

## Duties and where each one is

| Duty | Where |
|---|---|
| wait for any other pipeline run | master, step 0 |
| wait cap of 2 hours, then `ACTION: nightly skipped (another run still in progress after 2h)` (decision 2) | master, step 0; routine prompt |
| pull the latest main | master, step 0 |
| run the pipeline | master, step 1 |
| publish only if the data-quality gate passed | master, step 4 |
| POPIA release check before the publish | master, step 4 |
| POPIA skill fallback copy | master, step 4 |
| POPIA BLOCK: no publish, no personal data in the report | master, step 4 |
| publish with `--push` | master, step 4 |
| GrokForum token for every pull and push | master, step 0 |
| `gh auth setup-git` | master, step 0 |
| never another GitHub account | master, step 0; routine prompt |
| origin check before the push | master, step 0 and step 4 |
| standing pre-approved change, `public-data/` only | master, step 4; routine prompt |
| never push anything else, never merge PRs | master, step 4 and step 6; routine prompt |
| never confirm or reject flags | master, step 6; routine prompt |
| incident on a failed gate, on the local incidents branch | master, step 1 |
| incidents only on `incidents/local`, never on `main`, never pushed (decision 1) | master, intro ("Incidents"); routine prompt |
| main checkout stays on `main`; main check before the publish (decision 1) | master, intro and step 4 |
| incident on a new source failure | master, step 2 |
| incident on a failed push | master, step 4 |
| review-app health check and restart | master, step 5 |
| live manifest shows the new build | master, step 4 (live check) |
| evidence guard line | master, step 4 |
| refused export: no retry, no data edit | master, step 4 |
| missing or UNKNOWN guard line is never a pass | master, step 4 |
| backup only if the build and the publish returned 0 | master, step 4 |
| `backup: ok` line | master, step 4 |
| `ACTION: backup failed` | master, step 4 |
| backup: no retry, no delete | master, step 4 |
| backups never committed, pushed or published | master, step 4 |
| tell the orchestrator agent on a backup failure (failed line only) | routine prompt |
| quiet rule: send nothing when all is well | routine prompt |
| new high-severity flags in the report | routine prompt |
| HTTPS or manifest failure in the report | routine prompt |

## Changes

| File | Change |
|---|---|
| `docs/bot/live-skill/publicfunds-refresh.MASTER.md` | 10 edits (A to J) on the CHG-2026-065 text: A intro line on the quiet rule, and the "Incidents" block (the exact commands for the local branch `incidents/local` in its own worktree); B step 0 starts with the wait for any other pipeline run (capped at 2 hours) and the account and origin guard, before the pull; C and D incidents on a failed gate and on a new source failure; E in step 4, the standing pre-approval scope, then the main check, the account and origin guard again and the POPIA release check, before the publish command; F and G incidents on a failed push (publish exit 4 and other non-zero exits); H the live check confirms the live manifest shows the new build; I the backup step after the live check; J step 6 scope (never push anything else, never merge PRs). `publish-public-data.sh` is still named once, as the publish command. |
| `docs/bot/live-skill/routine-nightly.PROPOSED.md` | Rewritten: runs the skill's nightly-run path (steps 0 to 6); the account, scope and stop rules; the orchestrator agent message on a backup failure, with a placeholder for the agent id; the incidents branch rule; the quiet rule (with the nightly skipped after 2 hours); the report items with the ACTION lines first (the step 0 ACTION line alone when step 0 stops the run; `ACTION: publish blocked (not on main)` as a blocked publish). `publish-public-data.sh` is named once. The sentence "At the end, send one report" is gone (it contradicted the quiet rule). |
| `docs/bot/live-skill/README.md` | Deploy steps: save the live prompt privately first, put the agent id into the placeholder, deploy both together; rollback. |
| `tests/test_live_skill_snapshot.py` | The master is now the CHG-2026-061 draft with the 9 CHG-2026-065 edits and then the 10 CHG-2026-066 edits (`MASTER_EDITS`, `CHG066_EDITS`); a test checks both counts. New tests: duty coverage (`DUTIES`: duty names, the file and a marker string); order (account guard before the first pull; guard again and POPIA check before the publish command; backup after the live check; one publish command); quiet rule; no agent id in the committed files; incidents only on `incidents/local` (text); the 2-hour wait cap and its ACTION line; the main check before the publish; the publish script commits before its branch check and refuses a push off `main` (exit 4); a real git test in a temporary repo with a bare remote that runs the master's own incident commands; each with must-fail cases. |
| `tests/test_popia_candidate_export.py` (new) | The POPIA candidate export (`pf publish-data --out`, on a copy of `public-data/v1`) is byte-identical to the real export (`pf publish-data`), on the synthetic fixture warehouse; must-fail cases. See "Decisions". |
| CHG-2026-065 record | Status and post-implementation review: the PR #15 merge and the held deploy. |
| `itil/registers/change-log.md`, `itil/registers/ci-register.md`, `STATUS.md` | One new row, CI-118 updated, one new line. |

`publicfunds-refresh.LIVE-2026-11-17.md` is not changed. It is still byte-identical to the live skill (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`; `cmp` on 17 Nov 2026).

### Why two edit lists

The test compares the master with the CHG-2026-061 draft plus exact edits. The CHG-2026-065 edits (9) are kept as they were merged. The CHG-2026-066 edits (10) are applied after them. A reviewer can see each step separately, and any other change to the master fails the test.

### Choices

- **The orchestrator agent id.** The master and the routine prompt are both in git, so neither holds the id. The master says that the routine prompt tells the orchestrator agent. The routine prompt has the placeholder `<orchestrator agent id from the private deploy notes>`. At the deploy, the orchestrator puts in the id from the saved prompt in the private deploy notes. The deployed routine prompt is therefore the committed text with that one placeholder filled; this is the only expected difference.
- **The POPIA release check.** The publish script exports and pushes in one run, so there is no diff to read before it runs. The check makes a candidate export (`pf publish-data --out data/popia-candidate/v1`, from a copy of `public-data/v1`, so the evidence guard and the changelog compare with the same files) and reads `git diff --no-index` against `public-data/v1`. `data/` is not in git. A candidate exit 3 (export refused) goes on to the publish command, which refuses the same way, so the CHG-2026-041 report lines stay as they are. Any other candidate failure is treated as BLOCK (fail closed).
- **Account and origin guard.** It runs before the step 0 pull and again right before the publish, because the publish script does the push. `GH_TOKEN` stays exported for the run.
- **Incidents in their own worktree.** The requested design was `git switch` to `incidents/local` and back to `main`. A worktree (`/workspace/publicfunds-incidents`) does the same with less risk: the main checkout never switches branches, so a stale `incidents/local` never puts old code under a running pipeline (for example in the 2-hour wait case, when another run uses the checkout), and a modified file in the main checkout cannot block the switch back. `incidents/local` is made from `main` on first use and so shares its history; that is acceptable because it is never pushed. It is not kept up to date with `main`; the author moves its records to `main` with a normal change.
- **Backup after a BREACH.** The backup runs after the live check when step 1 and the publish returned 0, also when the wrapper said stop, because the backup does not publish.

## ACTION lines: case matrix

The CHG-2026-065 matrix still applies for a publish that ran. The new cases:

| Case | Report begins with |
|---|---|
| another run still in progress after 120 minutes (step 0) | `ACTION: nightly skipped (another run still in progress after 2h)` only (incident on `incidents/local`; no pull, no publish, no push; the run stops) |
| step 0 account or origin guard fails | `ACTION: account or origin check failed` only (the run stops) |
| step 4: the checkout is not on `main` | `ACTION: publish blocked (not on main)` only (no publish, no branch switch) |
| step 4 account or origin guard fails | `ACTION: account or origin check failed` only (no publish) |
| POPIA release check BLOCK | `ACTION: publish blocked (POPIA)` only (no publish) |
| candidate export exits non-zero, not 3 | `ACTION: publish blocked (POPIA)` only (no publish; reason: release check could not run) |
| candidate export exits 3 | the publish runs and refuses: the CHG-2026-065 rows for publish exit 3 |
| publish exit 0, guard bare `pass`, backup ok | no ACTION line |
| publish exit 0, guard bare `pass`, backup fails | `ACTION: backup failed` only |
| publish exit 0, guard not a bare pass, backup ok | `ACTION: publish needs attention` only |
| publish exit 0, guard not a bare pass, backup fails | `ACTION: publish needs attention`, then `ACTION: backup failed` |
| publish exit not 0 | the CHG-2026-065 rows; no backup, so no backup line |
| step 4 skipped | no publish ACTION line; no backup |

Each case has exactly one outcome. The backup runs only after publish exit 0, so `ACTION: backup failed` can follow only `ACTION: publish needs attention` or stand alone.

## Decisions (follow-up at head `03c325d1`)

Decided 17 Nov 2026 by the orchestrator under authority delegated by the owner (as reported to the author); the owner's deploy GO names the head that carries them.

1. **Incidents.** An incident is committed only on the local branch `incidents/local`, never on `main`, and that branch is never pushed. The master's "Incidents" block gives the exact commands (worktree `/workspace/publicfunds-incidents`; see "Choices"). Step 4 first checks `git -C /workspace/publicfunds rev-parse --abbrev-ref HEAD` is `main`; if not, `ACTION: publish blocked (not on main)` and no publish. The reason: `scripts/publish-public-data.sh` commits `public-data/` on the current branch (line 84) before it checks the branch (lines 87 to 88: exit 4, "refusing to push from branch ... (main only)"), and pushes `HEAD:main` (line 91). So the script would not push from `incidents/local`, but it would leave a data commit there; the main check stops that before the script runs. The git test shows that a push of `HEAD:main` from `main` does not carry the incident commit, and that the same push from `incidents/local` would.
2. **Wait cap.** Step 0 checks for another `thusa run` every 60 s, for up to 120 minutes. If one is still running, the report begins with exactly `ACTION: nightly skipped (another run still in progress after 2h)`, an incident is recorded on `incidents/local`, and nothing else is done: no pull, no publish, no push.

### Byte test of the POPIA candidate

`pf publish-data` (the publish script, line 68, default output `public-data/v1`) and `pf publish-data --out data/popia-candidate/v1` (the POPIA check) both call `thusa.publish_data.export`; only the output directory differs. The output directory is read for the evidence guard (`coverage.json`) and the changelog (`changes.json`, `manifest.json`), which is why the skill copies `public-data/v1` first. The test runs the real `pf` entry point three times on the synthetic fixture warehouse (`tests/conftest.py`), with the repo root moved to a temporary directory so that the default output is a temporary `public-data/v1`: a first export (the files that are live), then the candidate on a copy, then the real export. All files are compared byte for byte; nothing is excluded. The one clock field (`manifest.json` `generated_at_sast`, also used in `changes.json` and `feed.json`) is fixed to one value for both runs. Must-fail cases: without the copy, `changes.json` differs; with a different clock, only `manifest.json`, `changes.json` and `feed.json` differ. Limits: in a real night the two exports run some seconds apart, so those three files differ by that time only; the test uses the fixture warehouse, not the real one; it does not run `scripts/publish-public-data.sh` (never run by the author).

## Deploy (after the merge)

Done by the orchestrator, only after two reviewer PASSes on the exact head, the owner's GO naming that head, and the merge to `main`:

1. Save the routine prompt that is live at that time, word for word, in the private deploy notes (mode 0600, never in git), as its rollback text. The prompt of 17 Nov 2026 is already saved there.
2. From a clean checkout of `main`: `cp docs/bot/live-skill/publicfunds-refresh.MASTER.md /home/box/agent-data/workflows/publicfunds-refresh/SKILL.md`; `sha256sum` of both files gives the same value and `cmp` gives no output.
3. In the same step: take the text between the marker lines of `routine-nightly.PROPOSED.md`, replace the placeholder with the orchestrator agent id from the private deploy notes, and make that the routine prompt.
4. The next nightly report (or its silence when all is well) and the next backup are checked; record the deploy in the next change record.

## Testing

- `tests/test_live_skill_snapshot.py`: see "Changes". The drift check still accepts the master or the 17 Nov 2026 snapshot.
- `uv run pytest -q` on this branch, 17 Nov 2026 (no warehouse in the worktree): 955 passed, 61 skipped (`main` `ad850d92`: 935 passed, 61 skipped; 20 new tests: 7 at `8744e39b`, 13 in the follow-up).

## Risk assessment

- An incident commit pushed with the data. Control: incidents only on `incidents/local` in its own worktree, the main check before the publish, the git test.
- A night lost to a hung run. Control: the 2-hour cap reports `ACTION: nightly skipped (another run still in progress after 2h)`.
- A duty lost again. Control: the duty coverage test with must-fail cases.
- A push as another GitHub account or to another remote. Control: the guard before the pull and again before the publish.
- Personal information in the public data. Control: the POPIA release check before the publish, fail closed.
- A silent failure under the quiet rule. Control: every failure in the list sends a report, and every ACTION line sends a report.
- POPIA: the committed text holds role words, the public account name GrokForum and repo paths only; no agent id and no other account name. POPIA scan: PASS.

## How to revert

- Before the merge: delete the branch.
- After the merge, before the deploy: `git revert -m 1 <merge commit>`.
- After the deploy: copy `docs/bot/live-skill/publicfunds-refresh.LIVE-2026-11-17.md` byte for byte to the live skill path (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`) and write back the saved routine prompt from the private deploy notes, together, in the same step.

## Merge with PR #14 (CHG-2026-064)

A test merge with `git merge-tree` (17 Nov 2026) of this branch at `8744e39b` and the PR #14 branch at `47c007fb` (PR #14 with `main` `ad850d92` merged in) gave no conflict. The two changes can merge in either order.

## Seen, not touched

- The saved prompt committed incidents on `main` and had no time limit on the wait. Both are changed by decisions 1 and 2.
- The nightly never merges `incidents/local` into `main`. Its records reach `main` only with a normal change by the author.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | | |
| Reviewer 1 | reviewer | | |
| Reviewer 2 | reviewer | | |

## Post-implementation review

- Outcome: see the merge and deploy records.
