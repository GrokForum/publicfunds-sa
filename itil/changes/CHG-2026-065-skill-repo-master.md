# CHG-2026-065: Repo master copy of the live refresh skill; nightly publish with `--push` in skill step 4

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decisions, 17 Nov 2026, as reported to the author (PublicFunds) by the orchestrator: (a) the nightly routine always publishes by itself with `--push`, as CHG-2026-061 step 4, and step 4 runs only if step 1 returned 0; (b) the repo copy in `docs/bot/live-skill/` is the master, and the live skill is deployed from it. Exact words are in the private approval record. This record is not a merge GO and not a deploy GO. |
| Status | Built in DEV on branch `chg-2026-065-skill-repo-master` from `main` `e5fbfa58` (17 Nov 2026; the merge of PR #13, CHG-2026-061, exact head `7a7cd868`, 15:46 SAST; rollback tag `snapshot-2026-11-17-pre-pf-pr13` on `de37f666`). |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline). After the deploy, the nightly routine publishes from skill step 4. A merge needs two reviewer PASSes on the exact head and the owner's GO naming that head. The deploy follows the merge (see "Deploy"). |
| Environment | DEV (local worktree). Pre-change `main` is `e5fbfa58644f48f1ba01b718d3b9ced0d270dda2`. The merge changes only repo files; GitHub Pages serves them as plain files. The live skill and the routine prompt are outside git and change only at the deploy. |
| CIs affected | New CI-118 (master copy of the live refresh skill and the nightly routine prompt text, `docs/bot/live-skill/`); `tests/test_live_skill_snapshot.py`; this record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md`. At the deploy: the live refresh skill and the nightly routine prompt (CI-004). |
| Linked records | CHG-2026-061 (PR #13, merge `e5fbfa58`: `scripts/nightly_check_live.py` (CI-116), the live-skill snapshot and the draft step), CHG-2026-041 (publish guard line), CHG-2026-025 (step 0), CSI-036, RB-12, CI-070 (template skills) |
| Rollback | See "How to revert". Git is the rollback for the repo; no `.bkp` files. |

## What and why

CHG-2026-061 added the after-publish live check as a draft skill step and left three owner decisions open. The owner decided two of them on 17 Nov 2026 (as reported to the author (PublicFunds)): the routine always publishes with `--push`, from step 4, only if step 1 returned 0; and the repo copy is the master of the live skill. This change makes the master file, the routine prompt that goes with it, the deploy and drift-check steps, and tests.

## Changes

| File | Change |
|---|---|
| `docs/bot/live-skill/publicfunds-refresh.MASTER.md` | New. The master text of the live skill. Name: the skill name plus `MASTER`. It is not called `SKILL.md`, so that `tests/test_bot_skills.py` does not treat it as a template skill and the bot does not load it from the repo. |
| `docs/bot/live-skill/routine-nightly.PROPOSED.md` | New. The routine prompt that goes with the master, between two marker lines. |
| `docs/bot/live-skill/README.md` | Rewritten: master = repo copy; deploy by the orchestrator; drift check; rollback; the template skill. |
| `tests/test_live_skill_snapshot.py` | Tests added for the master, the routine prompt, the snapshot sha256 and the drift check. The CHG-2026-061 tests are unchanged. |
| `itil/registers/ci-register.md` | New row CI-118. |
| `itil/registers/change-log.md`, `STATUS.md` | One new row and one new line. |

`publicfunds-refresh.LIVE-2026-11-17.md` (the live skill before this change, sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`) and `publicfunds-refresh.PROPOSED-CHG-2026-061.md` stay as history. The snapshot is the rollback text. On 17 Nov 2026 the live skill on the bot computer had that sha256 (checked with `sha256sum` and `cmp`).

### Master text compared with the live skill of 17 Nov 2026

The master is the CHG-2026-061 draft with these 5 edits and no others (`tests/test_live_skill_snapshot.py`, `MASTER_EDITS`):

1. The DRAFT comment after the frontmatter is removed.
2. Step 4, first line: the `[DRAFT ...]` marker is removed. It now says "Only if step 1 returned **0**: publish, then check the live site (CHG-2026-061, CHG-2026-065). If step 1 returned anything else, do not publish."
3. Step 4, second line: "This is the only publish of the night. The nightly routine prompt runs this skill and does not publish by itself."
4. Step 4, fourth line: "Always use `--push`. Do not push by hand." comes first, then the line about `data/publish-run.log`.
5. Publish guard bullet: "When the routine publishes with `scripts/publish-public-data.sh --push`, the script prints ..." becomes "The publish script prints ...". The bullet is in step 4, after the publish command.

Compared with the live skill, the master therefore: says "skip steps 1 to 6" in step 0; keeps only the first line of step 3; adds step 4 (the publish command with `--push`, the publish guard bullet and the exit 3 and exit 4 bullets moved from step 3 without change, then `scripts/nightly_check_live.py` and its exit codes 0 to 3); renumbers the health check to step 5 and "Never confirm or reject" to step 6.

### Routine prompt

The author cannot read the routine prompt, and the repo has no copy of the current prompt (CHG-2026-061 marks it **[unverified]**). `routine-nightly.PROPOSED.md` is therefore written in full from the master skill. It is not an edit of the current prompt. The prompt runs the skill steps 0 to 6, says that step 4 is the only publish, gives no publish command line of its own, and lists the items of the final report. The routine prompt and the live skill change in the same step: with the new skill and the old prompt, the night could publish twice; with the new prompt and the old skill, the night does not publish.

## Deploy (after the merge)

Done by the orchestrator, only after two reviewer PASSes on the exact head, the owner's GO naming that head, and the merge to `main`:

1. From a clean checkout of `main`: `cp docs/bot/live-skill/publicfunds-refresh.MASTER.md /home/box/agent-data/workflows/publicfunds-refresh/SKILL.md`.
2. `sha256sum` of both files gives the same value; `cmp` gives no output.
3. In the same step: read the current routine prompt, keep it outside git as its rollback text, and replace it with the text between the marker lines in `routine-nightly.PROPOSED.md`.
4. The next nightly report shows the step 4 lines (publish exit code, `Evidence guard:` line, RESULT: and check_live: lines). Record the deploy and that first night in the next change record.

## Testing

- `tests/test_live_skill_snapshot.py`:
  - the snapshot is byte-exact to its sha256;
  - the master is exactly the draft with the 5 edits;
  - structure of the master: step 4 starts "Only if step 1 returned **0**: publish"; the publish command (with `--push`) is the only mention of `publish-public-data.sh` and is in step 4; no publish, `evidence_guard`, `--push` or `nightly_check_live` wording before step 4, and no guard or check wording in step 4 before the publish command; no DRAFT marker. A negative test changes the text in 5 ways and checks that each fails;
  - the routine prompt: runs the skill steps 0 to 6, says that step 4 is the only publish, always `--push`, no push by hand, and has no publish command line of its own;
  - drift check: when `/home/box/agent-data/workflows/publicfunds-refresh/SKILL.md` exists, it must be equal to the master or to the 17 Nov 2026 snapshot. When the path does not exist (CI, other computers), the test is skipped.
- `uv run pytest -q` on this branch, 17 Nov 2026 (no warehouse in the worktree): 923 passed, 61 skipped (`main` `e5fbfa58`: 917 passed, 61 skipped; 6 new tests). The drift check ran on the bot computer and passed (the live skill is equal to the 17 Nov 2026 snapshot).

## Risk assessment

- A double publish if only the skill or only the prompt changes. Control: the deploy changes both in one step; the master and the prompt both say step 4 is the only publish.
- No publish on a night when step 1 returns 2 (data-quality fail). This is the intended rule (RB-01). The live check then warns at 30 h and breaches at 48 h (SLO-PD-1).
- The live skill is edited outside the repo. Control: the drift check in the tests and the `cmp` command in the README.
- Flags shown in public: no change. POPIA: the new text holds only the repo path, the local review-app address and role words. POPIA scan: PASS.

## How to revert

- Before the merge: delete the branch.
- After the merge, before the deploy: `git revert -m 1 <merge commit>`.
- After the deploy: copy `docs/bot/live-skill/publicfunds-refresh.LIVE-2026-11-17.md` byte for byte to `/home/box/agent-data/workflows/publicfunds-refresh/SKILL.md` (check sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`), and write back the old routine prompt text, in the same step. Then revert the repo merge if needed.

## Seen, not touched

- The CHG-2026-061 record, its change-log row and the `STATUS.md` line for PR #13 still describe PR #13 as a draft. A records change can state its merge (`e5fbfa58`).
- CI-116 status says "not in the nightly routine". That stays true until the deploy; the deploy record can update it.
- The template skill `docs/bot/skills/publicfunds-refresh/SKILL.md` (CI-070) differs from the master. Whether it follows the master is a later decision.
- The skill is also used "on request". With the master, a run on request publishes in step 4 when step 1 returns 0, as the nightly does. This is the CHG-2026-061 draft wording, not a new rule.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | decisions (a) and (b), as reported to the author (PublicFunds); not a merge GO | 17 Nov 2026 |
| Reviewer 1 | reviewer | | |
| Reviewer 2 | reviewer | | |

## Post-implementation review

- Outcome: see the merge and deploy records.
