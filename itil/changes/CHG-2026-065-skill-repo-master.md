# CHG-2026-065: Repo master copy of the live refresh skill; nightly publish with `--push` in skill step 4

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decisions, 17 Nov 2026, as reported to the author (PublicFunds) by the orchestrator: (a) the nightly run publishes automatically with `--push`, as CHG-2026-061 step 4, and step 4 runs only if step 1 returned 0; (b) the repo copy in `docs/bot/live-skill/` is the master, and the live skill is deployed from it. A further owner decision, 17 Nov 2026, as reported to the author (PublicFunds): (c) step 4 publishes on the nightly run only; a refresh run on request reports and publishes only if the owner asks for a publish. Exact words are in the private approval record. This record is not a merge GO and not a deploy GO. |
| Status | Built in DEV on branch `chg-2026-065-skill-repo-master` from `main` `e5fbfa58` (17 Nov 2026; the merge of PR #13, CHG-2026-061, exact head `7a7cd868`, 15:46 SAST; rollback tag `snapshot-2026-11-17-pre-pf-pr13` on `de37f666`; post-merge tag `snapshot-2026-11-17-1546` on `e5fbfa58`, pushed by the author on 17 Nov 2026; `check_live` OK at 15:55 SAST). First commit `6183fe19`; a follow-up commit `acc67faa` adds decision (c), the exit 3 and exit 4 wording of step 4, and the PR #13 merge records. Draft PR #15 was opened at head `acc67faa`. A review follow-up commit on `acc67faa` adds the step-1 condition for a publish on request, puts a publish refusal first in the report, adds the merge order with PR #14, and makes the CHG-2026-061 change-log description factual. A second review follow-up commit on `e9778987` gives the merge with PR #14 row by row and the order of the two ACTION lines on a refused publish. A third review follow-up commit on `f3d6909b` makes the publish guard bullet agree with the exit 3 bullet (on a refusal the report always begins with `ACTION: publish refused`). A fourth review follow-up commit on `0e075302` states that a bare pass with no refusal adds no ACTION line, that a refusal means publish exit 3 only, and adds the ACTION case matrix. A follow-up commit on `75b59dab` (draft PR #15) gives publish exit 4 and any other non-zero exit the first ACTION line `ACTION: publish failed`. A follow-up commit on `a4350327` states that a skipped step 4 adds no publish ACTION line and completes the case matrix. Merged as PR #15: merge `ad850d92dd3ea85bf75486f859219bed3419cbaa`, 17 Nov 2026 18:02 SAST, exact head `dd52775a`, tag `snapshot-2026-11-17-1802`. The deploy was held on 17 Nov 2026; see CHG-2026-066. Recorded by CHG-2026-066. |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline). After the deploy, the nightly routine publishes from skill step 4. A merge needs two reviewer PASSes on the exact head and the owner's GO naming that head. The deploy follows the merge (see "Deploy"). |
| Environment | DEV (local worktree). Pre-change `main` is `e5fbfa58644f48f1ba01b718d3b9ced0d270dda2`. The merge changes only repo files; GitHub Pages serves them as plain files. The live skill and the routine prompt are outside git and change only at the deploy. |
| CIs affected | New CI-118 (master copy of the live refresh skill and the nightly routine prompt text, `docs/bot/live-skill/`); `tests/test_live_skill_snapshot.py`; this record; the CHG-2026-061 record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md`. At the deploy: the live refresh skill and the nightly routine prompt (CI-004). |
| Linked records | CHG-2026-061 (PR #13, merge `e5fbfa58`: `scripts/nightly_check_live.py` (CI-116), the live-skill snapshot and the draft step), CHG-2026-041 (publish guard line), CHG-2026-025 (step 0), CSI-036, RB-12, CI-070 (template skills) |
| Rollback | See "How to revert". Git is the rollback for the repo; no `.bkp` files. |

## What and why

CHG-2026-061 added the after-publish live check as a draft skill step and left three owner decisions open. The owner decided two of them on 17 Nov 2026 (as reported to the author (PublicFunds)): the nightly run publishes automatically with `--push`, from step 4, only if step 1 returned 0; and the repo copy is the master of the live skill. This change makes the master file, the routine prompt that goes with it, the deploy and drift-check steps, and tests. It also records the merge of PR #13 (CHG-2026-061) in the CHG-2026-061 record, its change-log row and `STATUS.md`.

## Changes

| File | Change |
|---|---|
| `docs/bot/live-skill/publicfunds-refresh.MASTER.md` | New. The master text of the live skill. Name: the skill name plus `MASTER`. It is not called `SKILL.md`, so that `tests/test_bot_skills.py` does not treat it as a template skill and the bot does not load it from the repo. |
| `docs/bot/live-skill/routine-nightly.PROPOSED.md` | New. The routine prompt that goes with the master, between two marker lines. |
| `docs/bot/live-skill/README.md` | Rewritten: master = repo copy; deploy by the orchestrator; drift check; rollback; the template skill. |
| `tests/test_live_skill_snapshot.py` | Tests added for the master, the routine prompt, the snapshot sha256 and the drift check. The CHG-2026-061 tests are unchanged. |
| `itil/registers/ci-register.md` | New row CI-118. |
| `itil/registers/change-log.md`, `STATUS.md` | One new row and one new line. |
| `itil/changes/CHG-2026-061-check-live-nightly.md`, its change-log row, its `STATUS.md` line | The PR #13 merge: merge `e5fbfa58644f48f1ba01b718d3b9ced0d270dda2`, 17 Nov 2026 15:46 SAST, exact head `7a7cd868`, owner GO as reported to the author (PublicFunds); rollback tag `snapshot-2026-11-17-pre-pf-pr13` on `de37f666`; post-merge tag `snapshot-2026-11-17-1546` on `e5fbfa58`, pushed by the author on 17 Nov 2026; `check_live` OK at 15:55 SAST (the author ran it again at 15:56 SAST: RESULT OK, build B20261117T012014Z). The reviewer PASSes on `7a7cd868` are not in the author's records **[unverified]**. |

`publicfunds-refresh.LIVE-2026-11-17.md` (the live skill before this change, sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`) and `publicfunds-refresh.PROPOSED-CHG-2026-061.md` stay as history. The snapshot is the rollback text. On 17 Nov 2026 the live skill on the bot computer had that sha256 (checked with `sha256sum` and `cmp`).

### Master text compared with the live skill of 17 Nov 2026

The master is the CHG-2026-061 draft with these 9 edits and no others (`tests/test_live_skill_snapshot.py`, `MASTER_EDITS`; the first commit `6183fe19` had 5 edits):

1. The DRAFT comment after the frontmatter is removed.
2. The first two lines of step 4 are replaced by four lines. Step 4 now starts: "**Nightly run only.** Only if step 1 returned **0**: publish, then check the live site (CHG-2026-061, CHG-2026-065). If step 1 returned anything else, do not publish." Then: "On a run on request, skip this step: do not publish unless the owner asks for a publish. If the owner asks, run this step with the same condition: only if step 1 returned **0**." Then: "If step 4 was skipped, add no publish ACTION line; report the step 1 result." Then: "This is the only publish of the night. The nightly routine prompt runs this skill and does not publish by itself."
3. After the publish command: "Always use `--push`. Do not push by hand." comes first, then the line about `data/publish-run.log`, then "Then, whatever the publish exit code, run the live check wrapper. It only reads; it never publishes or pushes:" and the wrapper command.
4. Publish guard bullet: "When the routine publishes with `scripts/publish-public-data.sh --push`, the script prints ..." becomes "The publish script prints ...". "Only a bare `evidence_guard: pass` is quiet." becomes "Only a bare `evidence_guard: pass` is quiet: it adds no ACTION line of its own." "..., and begin the report with `ACTION: publish needs attention` and quote the line." becomes "... and quote the line. The first ACTION line of the report depends on the publish exit code. If the publish was refused (exit 3, see the next bullet), the report always begins with `ACTION: publish refused`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. If the publish failed (exit 4 or any other non-zero exit, see the bullets below), the report always begins with `ACTION: publish failed`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. If the publish exited 0 and the guard line is not a bare pass, the report begins with `ACTION: publish needs attention`. A bare pass with publish exit 0 adds no ACTION line." The guard bullet and the exit 3, exit 4 and other-exit bullets now agree (see "ACTION lines: case matrix").
5. A new line after the title: the nightly routine does steps 0 to 6 and step 4 is its only publish; a run on request does steps 0 to 3, then 5 and 6, and reports, and does not publish unless the owner asks for a publish.
6. Publish exit 3 bullet: adds "The wrapper prints `check_live: SKIPPED` and exits 3.", and "Report to the owner at once:" becomes "Begin the report with `ACTION: publish refused`. If the guard line is not a bare pass (for example `BLOCKED`), put `ACTION: publish needs attention` on the next line (refused first, then needs attention). Then give first:". The routine reports only through its own final report, so the refusal goes first in that report. When the guard line is not a bare pass, both ACTION lines apply: `ACTION: publish refused` comes first, then `ACTION: publish needs attention`.
7. The exit 4 line becomes two bullets. Exit 4: nothing was pushed; the wrapper prints `check_live: SKIPPED` and exits 3; "Begin the report with `ACTION: publish failed`. If the guard line is not a bare pass, put `ACTION: publish needs attention` on the next line (failed first, then needs attention)."; stop after the wrapper and report; do not retry. Any other non-zero publish exit: the wrapper cannot tell if the publish pushed; it prints `check_live: FAILED CHECK` and exits 2; the same two ACTION sentences; stop and report, and check by hand if new data went live; do not retry.
8. "Then run: <wrapper command>" becomes "The wrapper's exit code:" (the command moved up, see edit 3).
9. Wrapper exit 3: "skipped, because it is clear that the publish did not push (publish exit 3 or 4, or nothing new to push). check_live was not run. Report the check_live: SKIPPED line. The publish rules above still apply."

Compared with the live skill, the master therefore: adds the line about the two kinds of run; says "skip steps 1 to 6" in step 0; keeps only the first line of step 3; adds step 4 (nightly run only: the publish command with `--push`, the wrapper command, the publish guard bullet, the exit 3 and exit 4 bullets moved from step 3 with the wrapper results added, a bullet for any other non-zero exit, then the wrapper exit codes 0 to 3); renumbers the health check to step 5 and "Never confirm or reject" to step 6.

### Why the wrapper runs after every publish exit code

`scripts/nightly_check_live.py` (`publish_pushed`) treats publish exit 3 and 4 as a refusal: it prints `check_live: SKIPPED`, does not run `check_live` and exits 3. It reads nothing from the network in that case. For any other non-zero publish exit it cannot tell if the publish pushed: it prints `check_live: FAILED CHECK` and exits 2, and tells the operator to check by hand if new data went live. Running the wrapper every time is therefore safe (it only reads; it never publishes or pushes) and safer than skipping it: an unexpected exit code after a partial push gets a FAILED CHECK line instead of no line, and the nightly report always has a `check_live:` line. The CHG-2026-061 draft said "stop and report" for exit 4 before the wrapper line, which could be read either way; the master now says it clearly.

### ACTION lines: case matrix

What the master text gives for each case. The guard lines the publish script can print come from `scripts/publish-public-data.sh` (`guard_report`): on exit 3 it prints `BLOCKED`, `not an evidence-guard refusal` or `UNKNOWN` (or no line after a crash); it prints `pass`, `pass (N notes)`, `warn (N notes)` or `UNKNOWN` only after a successful export, so also before exit 0 and exit 4. Rows marked "not printed today" are combinations the script cannot produce now; the master still decides them, so a later change to the script cannot leave a case open.

| Publish exit | Guard line | Report begins with |
|---|---|---|
| 0 | bare `pass` | no ACTION line |
| 0 | `pass (N notes)`, `warn (N notes)`, `UNKNOWN` | `ACTION: publish needs attention` only |
| 0 | missing | `ACTION: publish needs attention` only (a missing line is UNKNOWN) |
| 0 | `BLOCKED`, `not an evidence-guard refusal` (not printed today) | `ACTION: publish needs attention` only |
| 3 (refusal) | `BLOCKED`, `not an evidence-guard refusal`, `UNKNOWN`, missing | `ACTION: publish refused`, then `ACTION: publish needs attention` |
| 3 (refusal) | `pass (N notes)`, `warn (N notes)` (not printed today) | `ACTION: publish refused`, then `ACTION: publish needs attention` |
| 3 (refusal) | bare `pass` (not printed today) | `ACTION: publish refused` only |
| 4 | bare `pass` | `ACTION: publish failed` only; then stop after the wrapper and report |
| 4 | any other line, or missing | `ACTION: publish failed`, then `ACTION: publish needs attention`; then stop after the wrapper and report |
| other non-zero | bare `pass` | `ACTION: publish failed` only; wrapper FAILED CHECK; stop and report, check by hand |
| other non-zero | any other line, or missing | `ACTION: publish failed`, then `ACTION: publish needs attention`; wrapper FAILED CHECK; stop and report, check by hand |
| step 4 skipped (step 1 did not return 0, or a run on request with no publish ask) | none (no publish ran) | no publish ACTION line; report the step 1 result |

Each case has exactly one outcome. Every non-zero publish exit gives a first ACTION line (refused for exit 3, failed for exit 4 and any other non-zero exit); `ACTION: publish needs attention` alone begins the report only on publish exit 0; a skipped step 4 adds no publish ACTION line.

### Run on request (decision (c))

The skill is used by the nightly routine and on request. Before decision (c), the draft wording meant that a run on request would publish in step 4 when step 1 returned 0. The master now says that step 4 is for the nightly run only. A run on request does steps 0 to 3, reports, and does steps 5 and 6. It publishes only if the owner asks for a publish, and then only with the same condition as the nightly run: step 4 runs only if step 1 returned 0. Steps 5 (review-app health check) and 6 (never confirm or reject flags) still apply to a run on request, because they do not publish.

### Routine prompt

The author cannot read the routine prompt, and the repo has no copy of the current prompt (CHG-2026-061 marks it **[unverified]**). `routine-nightly.PROPOSED.md` is therefore written in full from the master skill. It is not an edit of the current prompt. The prompt says that this is the nightly run, runs the skill steps 0 to 6 on the nightly-run path, says that step 4 is the only publish (the wrapper runs whatever the publish exit code), gives no publish command line of its own, and lists the items of the final report. The routine prompt and the live skill change in the same step: with the new skill and the old prompt, the night could publish twice; with the new prompt and the old skill, the night does not publish.

## Deploy (after the merge)

Done by the orchestrator, only after two reviewer PASSes on the exact head, the owner's GO naming that head, and the merge to `main`:

1. From a clean checkout of `main`: `cp docs/bot/live-skill/publicfunds-refresh.MASTER.md /home/box/agent-data/workflows/publicfunds-refresh/SKILL.md`.
2. `sha256sum` of both files gives the same value; `cmp` gives no output.
3. In the same step: read the current routine prompt, keep it outside git as its rollback text, and replace it with the text between the marker lines in `routine-nightly.PROPOSED.md`.
4. The next nightly report shows the step 4 lines (publish exit code, `Evidence guard:` line, RESULT: and check_live: lines). Record the deploy and that first night in the next change record.

## Testing

- `tests/test_live_skill_snapshot.py`:
  - the snapshot is byte-exact to its sha256;
  - the master is exactly the draft with the 9 edits (`len(MASTER_EDITS) == 9`);
  - structure of the master: step 4 starts "**Nightly run only.** Only if step 1 returned **0**: publish"; the publish command (with `--push`) is the only mention of `publish-public-data.sh` and is in step 4; no publish, `evidence_guard`, `--push` or `nightly_check_live` wording before step 4, and no guard or check wording in step 4 before the publish command; no DRAFT marker. A negative test changes the text in 5 ways and checks that each fails;
  - decision (c): step 4 starts "**Nightly run only.**", its next line is the run-on-request rule, and the line after the title says a run on request does not publish unless the owner asks. A negative test drops each of these in turn and checks that each fails;
  - the wrapper: its command is in step 4 once, after the publish command and before the exit bullets; the exit 3 and exit 4 bullets say SKIPPED / exit 3 and the other-exit bullet says FAILED CHECK / exit 2; and `publish_pushed` in `scripts/nightly_check_live.py` gives NOT_PUSHED for publish exit 3 and 4 and UNKNOWN for exit 5;
  - the routine prompt: says that this is the nightly run, runs the skill steps 0 to 6 on the nightly-run path, says that step 4 is the only publish, always `--push`, no push by hand, and has no publish command line of its own; the file names `publish-public-data.sh` exactly once (a negative test with a second publish line fails);
  - the ACTION order on a refused publish: in the exit 3 bullet, `ACTION: publish refused` comes before `ACTION: publish needs attention`; the guard bullet says that on a refusal the report always begins with `ACTION: publish refused` and that needs-attention alone begins the report only on publish exit 0; the routine prompt says the same. A negative test (3 cases: the draft guard wording, the refusal sentence dropped, the exit 3 order swapped) checks that each fails; a bare pass with publish exit 0 adds no ACTION line (positive test in the master and the routine prompt, and a negative test with 3 cases that give a bare pass an ACTION line); `ACTION: publish failed` comes first on exit 4 and any other non-zero exit, and needs attention next (positive test in the master and the routine prompt, and a negative test with 5 cases: the old exit 4 wording, the old other-exit wording, the order swapped on exit 4, the failed sentence dropped from the guard bullet, and the "no refusal" wording that would cover exit 4); a skipped step 4 adds no publish ACTION line (positive test: the sentence is in step 4 of the master before the publish command and in the routine prompt; negative test: the sentence removed from either file fails);
  - drift check: when `/home/box/agent-data/workflows/publicfunds-refresh/SKILL.md` exists, it must be equal to the master or to the 17 Nov 2026 snapshot. When the path does not exist (CI, other computers), the test is skipped.
- `uv run pytest -q` on this branch, 17 Nov 2026 (no warehouse in the worktree): first commit `6183fe19`: 923 passed, 61 skipped (`main` `e5fbfa58`: 917 passed, 61 skipped; 6 new tests). Follow-up commit `acc67faa`: 926 passed, 61 skipped (3 more tests). Review follow-up commit on `acc67faa` (draft PR #15): 927 passed, 61 skipped (1 more test). Second review follow-up commit on `e9778987`: 928 passed, 61 skipped (1 more test). Third review follow-up commit on `f3d6909b`: 929 passed, 61 skipped (1 more test). Fourth review follow-up commit on `0e075302`: 931 passed, 61 skipped (2 more tests). Follow-up commit on `75b59dab`: 933 passed, 61 skipped (2 more tests). Follow-up commit on `a4350327`: 935 passed, 61 skipped (2 more tests). The drift check ran on the bot computer and passed (the live skill is equal to the 17 Nov 2026 snapshot).

## Risk assessment

- A double publish if only the skill or only the prompt changes. Control: the deploy changes both in one step; the master and the prompt both say step 4 is the only publish.
- No publish on a night when step 1 returns 2 (data-quality fail). This is the intended rule (RB-01). The live check then warns at 30 h and breaches at 48 h (SLO-PD-1).
- The live skill is edited outside the repo. Control: the drift check in the tests and the `cmp` command in the README.
- Flags shown in public: no change. POPIA: the new text holds only the repo path, the local review-app address and role words. POPIA scan: PASS.

## How to revert

- Before the merge: delete the branch.
- After the merge, before the deploy: `git revert -m 1 <merge commit>`.
- After the deploy: copy `docs/bot/live-skill/publicfunds-refresh.LIVE-2026-11-17.md` byte for byte to `/home/box/agent-data/workflows/publicfunds-refresh/SKILL.md` (check sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`), and write back the old routine prompt text, in the same step. Then revert the repo merge if needed.

## Merge order with PR #14 (CHG-2026-064)

A test merge (17 Nov 2026, a throwaway worktree, `git merge a60e3493` into this branch at `e9778987`) gave one conflict block, in `itil/registers/change-log.md`, with three rows on each side. `STATUS.md` and all other files merged without a conflict.

- This branch side: the CHG-2026-061 row (changed by this change), the CHG-2026-063 row (as on `main` `e5fbfa58`), the CHG-2026-065 row (new).
- PR #14 side: the CHG-2026-061 row (as on `main` `e5fbfa58`), the CHG-2026-063 row (changed by CHG-2026-064), the CHG-2026-064 row (new).

Merge order planned: PR #15 (this change) first. Then the PR #14 branch merges `main` again (`git merge origin/main`, no rebase) and resolves the block row by row, in this order:

1. the CHG-2026-061 row from PR #15;
2. the CHG-2026-063 row from PR #14;
3. the CHG-2026-064 row (from PR #14);
4. the CHG-2026-065 row (from PR #15).

Each new head needs new reviews and the owner GO naming it.

## Seen, not touched

- CI-116 status says "not in the nightly routine". That stays true until the deploy; the deploy record can update it.
- The template skill `docs/bot/skills/publicfunds-refresh/SKILL.md` (CI-070) differs from the master. Whether it follows the master is a later decision.
- The CHG-2026-061 record still has older history lines that name draft PR #13 (for example "Result" and "Review of head `72d84812`"). They are past-tense facts and stay as they are.

## Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Change authority | owner | decisions (a), (b) and (c), as reported to the author (PublicFunds); not a merge GO | 17 Nov 2026 |
| Reviewer 1 | reviewer | | |
| Reviewer 2 | reviewer | | |

## Post-implementation review

- Outcome: merged as `ad850d92` (PR #15, 17 Nov 2026 18:02 SAST). The deploy was held on 17 Nov 2026, because the master skill and the proposed routine prompt did not have all the duties of the routine prompt that was live then. CHG-2026-066 adds them.
