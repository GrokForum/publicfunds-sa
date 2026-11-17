# CHG-2026-066: Nightly duties of the routine prompt of 17 Nov 2026 in the master skill and the proposed routine prompt

| Field | Value |
|---|---|
| Requested by / date (SAST) | The orchestrator held the CHG-2026-065 deploy on 17 Nov 2026 (as reported to the author (PublicFunds)): the proposed pair (master skill and routine prompt) did not have all the duties of the routine prompt that was live then. This record is not a merge GO and not a deploy GO. |
| Status | Built in DEV on branch `chg-2026-066-nightly-duties` from `main` `ad850d92` (17 Nov 2026; the merge of PR #15, CHG-2026-065, exact head `dd52775a`, 18:02 SAST, tag `snapshot-2026-11-17-1802`). |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline). After the deploy, the nightly routine runs these steps. A merge needs two reviewer PASSes on the exact head and the owner's GO naming that head. The deploy follows the merge. |
| Environment | DEV (local worktree). Pre-change `main` is `ad850d92dd3ea85bf75486f859219bed3419cbaa`. The merge changes only repo files. The live skill and the routine prompt are outside git and change only at the deploy. |
| CIs affected | CI-118 (`docs/bot/live-skill/publicfunds-refresh.MASTER.md`, `docs/bot/live-skill/routine-nightly.PROPOSED.md`, `docs/bot/live-skill/README.md`); `tests/test_live_skill_snapshot.py`; this record; the CHG-2026-065 record (merge facts); `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md`. At the deploy: the live refresh skill and the nightly routine prompt (CI-004). |
| Linked records | CHG-2026-065 (PR #15, merge `ad850d92`), CHG-2026-061, CHG-2026-044 (state backup, appendix A), CHG-2026-041 (publish guard line), CHG-2026-025 (step 0), CI-110, CI-114, CI-116 |
| Rollback | See "How to revert". Git is the rollback for the repo; no `.bkp` files. |

## What and why

Before the CHG-2026-065 deploy, the orchestrator read the routine prompt that was live on 17 Nov 2026 and kept it, word for word, in the private deploy notes (mode 0600, outside git). The CHG-2026-065 master skill and proposed routine prompt left out some of its duties, so the deploy was held. This change compares the two, duty by duty, and puts every duty into the master skill or the proposed routine prompt. The saved prompt is not copied or quoted in git; the tests hold duty names and short marker strings only.

## Duties and where each one is

| Duty | Where |
|---|---|
| wait for any other pipeline run | master, step 0 |
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
| incident on a failed gate, committed locally (no push) | master, step 1 |
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
| `docs/bot/live-skill/publicfunds-refresh.MASTER.md` | 10 edits (A to J) on the CHG-2026-065 text: A intro line on the quiet rule; B step 0 starts with the wait for any other pipeline run and the account and origin guard, before the pull; C and D incidents on a failed gate and on a new source failure; E in step 4, the standing pre-approval scope, then the account and origin guard again and the POPIA release check, before the publish command; F and G incidents on a failed push (publish exit 4 and other non-zero exits); H the live check confirms the live manifest shows the new build; I the backup step after the live check; J step 6 scope (never push anything else, never merge PRs). `publish-public-data.sh` is still named once, as the publish command. |
| `docs/bot/live-skill/routine-nightly.PROPOSED.md` | Rewritten: runs the skill's nightly-run path (steps 0 to 6); the account, scope and stop rules; the orchestrator agent message on a backup failure, with a placeholder for the agent id; the quiet rule; the report items with the ACTION lines first. `publish-public-data.sh` is named once. The sentence "At the end, send one report" is gone (it contradicted the quiet rule). |
| `docs/bot/live-skill/README.md` | Deploy steps: save the live prompt privately first, put the agent id into the placeholder, deploy both together; rollback. |
| `tests/test_live_skill_snapshot.py` | The master is now the CHG-2026-061 draft with the 9 CHG-2026-065 edits and then the 10 CHG-2026-066 edits (`MASTER_EDITS`, `CHG066_EDITS`); a test checks both counts. New tests: duty coverage (`DUTIES`: duty names, the file and a marker string); order (account guard before the first pull; guard again and POPIA check before the publish command; backup after the live check; one publish command); quiet rule; no agent id in the committed files; each with must-fail cases. |
| CHG-2026-065 record | Status and post-implementation review: the PR #15 merge and the held deploy. |
| `itil/registers/change-log.md`, `itil/registers/ci-register.md`, `STATUS.md` | One new row, CI-118 updated, one new line. |

`publicfunds-refresh.LIVE-2026-11-17.md` is not changed. It is still byte-identical to the live skill (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`; `cmp` on 17 Nov 2026).

### Why two edit lists

The test compares the master with the CHG-2026-061 draft plus exact edits. The CHG-2026-065 edits (9) are kept as they were merged. The CHG-2026-066 edits (10) are applied after them. A reviewer can see each step separately, and any other change to the master fails the test.

### Choices

- **The orchestrator agent id.** The master and the routine prompt are both in git, so neither holds the id. The master says that the routine prompt tells the orchestrator agent. The routine prompt has the placeholder `<orchestrator agent id from the private deploy notes>`. At the deploy, the orchestrator puts in the id from the saved prompt in the private deploy notes. The deployed routine prompt is therefore the committed text with that one placeholder filled; this is the only expected difference.
- **The POPIA release check.** The publish script exports and pushes in one run, so there is no diff to read before it runs. The check makes a candidate export (`pf publish-data --out data/popia-candidate/v1`, from a copy of `public-data/v1`, so the evidence guard and the changelog compare with the same files) and reads `git diff --no-index` against `public-data/v1`. `data/` is not in git. A candidate exit 3 (export refused) goes on to the publish command, which refuses the same way, so the CHG-2026-041 report lines stay as they are. Any other candidate failure is treated as BLOCK (fail closed).
- **Account and origin guard.** It runs before the step 0 pull and again right before the publish, because the publish script does the push. `GH_TOKEN` stays exported for the run.
- **Backup after a BREACH.** The backup runs after the live check when step 1 and the publish returned 0, also when the wrapper said stop, because the backup does not publish.

## ACTION lines: case matrix

The CHG-2026-065 matrix still applies for a publish that ran. The new cases:

| Case | Report begins with |
|---|---|
| step 0 account or origin guard fails | `ACTION: account or origin check failed` only (the run stops) |
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

## Deploy (after the merge)

Done by the orchestrator, only after two reviewer PASSes on the exact head, the owner's GO naming that head, and the merge to `main`:

1. Save the routine prompt that is live at that time, word for word, in the private deploy notes (mode 0600, never in git), as its rollback text. The prompt of 17 Nov 2026 is already saved there.
2. From a clean checkout of `main`: `cp docs/bot/live-skill/publicfunds-refresh.MASTER.md /home/box/agent-data/workflows/publicfunds-refresh/SKILL.md`; `sha256sum` of both files gives the same value and `cmp` gives no output.
3. In the same step: take the text between the marker lines of `routine-nightly.PROPOSED.md`, replace the placeholder with the orchestrator agent id from the private deploy notes, and make that the routine prompt.
4. The next nightly report (or its silence when all is well) and the next backup are checked; record the deploy in the next change record.

## Testing

- `tests/test_live_skill_snapshot.py`: see "Changes". The drift check still accepts the master or the 17 Nov 2026 snapshot.
- `uv run pytest -q` on this branch, 17 Nov 2026 (no warehouse in the worktree): 942 passed, 61 skipped (`main` `ad850d92`: 935 passed, 61 skipped; 7 new tests).

## Risk assessment

- A duty lost again. Control: the duty coverage test with must-fail cases.
- A push as another GitHub account or to another remote. Control: the guard before the pull and again before the publish.
- Personal information in the public data. Control: the POPIA release check before the publish, fail closed.
- A silent failure under the quiet rule. Control: every failure in the list sends a report, and every ACTION line sends a report.
- POPIA: the committed text holds role words, the public account name GrokForum and repo paths only; no agent id and no other account name. POPIA scan: PASS.

## How to revert

- Before the merge: delete the branch.
- After the merge, before the deploy: `git revert -m 1 <merge commit>`.
- After the deploy: copy `docs/bot/live-skill/publicfunds-refresh.LIVE-2026-11-17.md` byte for byte to the live skill path (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`) and write back the saved routine prompt from the private deploy notes, together, in the same step.

## Seen, not touched

- Incidents committed locally on `main` (a duty of the saved prompt, kept as it was): a later publish pushes `HEAD:main`, so a local incident commit on `main` would go out with the next data push. This is outside "never push anything else". The owner may want incidents committed on a local branch, or left uncommitted. Not changed here.
- The wait for another pipeline run has no time limit (as in the saved prompt).

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | | |
| Reviewer 1 | reviewer | | |
| Reviewer 2 | reviewer | | |

## Post-implementation review

- Outcome: see the merge and deploy records.
