# CHG-2026-061: Add check_live to the nightly refresh after a successful publish

| Field | Value |
|---|---|
| Requested by / date (SAST) | Follow-on to CSI-036, CHG-2026-032 and the CHG-2026-053 RFC (PR #2, merged 15 Nov 2026). RFC drafted 15 Nov 2026. Repo part built 17 Nov 2026 on branch `chg-2026-061-nightly-check-live` (owner GO for the CHG-061 build and the PR #11 fold, 17 Nov 2026, as reported to the author (PublicFunds)). This record is not a merge GO. |
| Status | RFC merged as PR #10 (merge `ceabf99`, 15 Nov 2026 21:26 SAST, exact head `84590a20`). **Implementation, repo part only: built on branch `chg-2026-061-nightly-check-live` from `main` `eebb4c44` (17 Nov 2026); draft PR #13, opened 17 Nov 2026 11:43 SAST by the orchestrator at head `72d84812`.** This change does **not** change the live skill, the template skill copy or the nightly routine prompt. It adds a snapshot of the live skill and the proposed step as a marked draft (`docs/bot/live-skill/`). See "Implementation (repo part)" and "Follow-up (owner decisions)". |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline / distribution). The repo part (wrapper script, tests, records, live-skill snapshot and draft) is on branch `chg-2026-061-nightly-check-live`. A merge needs two reviewer PASSes and the owner's GO naming the exact head. Changing the nightly routine and the live skill is a later step with its own owner GO. |
| Environment | DEV: branch `chg-2026-061-nightly-check-live` (draft PR #13, opened 17 Nov 2026 11:43 SAST by the orchestrator at head `72d84812`), pre-change `main` `eebb4c44c82e47da2d8879e2af6b61287ed6cd68` (the RFC was written on `8b4f72b8`, tag `snapshot-2026-11-15-1817`); `main` `de37f666` merged in on 17 Nov 2026. This change publishes nothing. The routine prompt and the live skill on the bot computer are outside git and are not changed by this change. |
| CIs affected (this RFC) | `itil/changes/CHG-2026-061-check-live-nightly.md`, `itil/registers/change-log.md` |
| CIs affected (repo part, this branch) | New `scripts/nightly_check_live.py` and `tests/test_nightly_check_live.py` (CI-116); new `docs/bot/live-skill/` (live skill snapshot of 17 Nov 2026, the proposed step as a marked draft, README) and `tests/test_live_skill_snapshot.py`; this record; `itil/registers/change-log.md`; `itil/registers/ci-register.md`; `STATUS.md` |
| CIs affected (later step, after the owner GO) | Live refresh skill; repo copy `docs/bot/skills/publicfunds-refresh/SKILL.md`; the nightly routine prompt; `itil/registers/csi-register.md` (CSI-036 status) |
| Linked records | CHG-2026-032 (script and RB-12), CHG-2026-053 (RFC draft, open PR #2), CSI-036, SLO-PD-1, RB-12, D-08 (still open; out of scope) |
| Rollback | For this docs change: close it unmerged, or `git revert -m 1 <merge commit>` if it is later merged. Git is the rollback; no `.bkp` files. The later implementation rollback and the BREACH kill switch are quoted below, reused from CHG-2026-032, CHG-2026-053, RB-12 and CSI-036. |

## Problem

`scripts/check_live.py` and RB-12 already exist (CHG-2026-032). CSI-036 still says the "nightly routine step needs a separate owner GO" (`itil/registers/csi-register.md:42`). The refresh skill publishes public data after a successful build, but it does not then run the live check. It only names the script as context when a publish is refused. A broken site, a failed Pages deploy, or a stale manifest can sit until someone runs the check by hand, or until the 30 h WARN / 48 h BREACH windows on SLO-PD-1.

CHG-2026-053 is an RFC only. Merging that RFC does not authorise editing the live skill or the nightly routine.

## Change (proposed; not applied in this RFC)

After a successful `scripts/publish-public-data.sh --push`, run the existing after-publish live check, report its result, and follow the RB-12 kill switch on a BREACH. Do not change the script. Do not re-publish to "fix" a BREACH.

### Exact command the nightly would run

The command is the after-publish line already written in RB-12 (`itil/knowledge/runbooks.md:132`) and in CHG-2026-053 (open PR #2, commit `9ff492e`, lines 21–24):

```
python3 scripts/check_live.py \
  --expect-local public-data/v1/manifest.json \
  --raw-url https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json \
  --wait 600
```

CHG-2026-032 (`itil/changes/CHG-2026-032-live-site-check.md:53`) gave the same command with a placeholder for the raw URL ("`<raw manifest URL from RB-11>`"). This RFC uses the concrete URL from RB-12:132.

Flags checked on `main` at `8b4f72b8`, in `scripts/check_live.py`:

- `--raw-url` is defined at line 380.
- `--expect-local` is defined at line 381.
- `--wait` is defined at line 382; the allowed range is 0 to `MAX_WAIT` (3600.0) at line 39. A value of 600 is inside that range.
- A probe `python3 scripts/check_live.py --wait 3601` printed `argument --wait: must be at least 0 and at most 3600` and exited 2, and the usage line listed `--expect-local`, `--raw-url` and `--wait`. No production URL was fetched.

If the publish step did not run, or did not push (quality-gate failure, evidence-guard block, exit 4, or no `--push`), do not run this after-publish command. A read-only default run (`python3 scripts/check_live.py`, RB-12:131) may still be used when investigating; it is not part of this change.

### Exit codes (from the script, not from older RFC wording)

Use the codes in `scripts/check_live.py:10` and RB-12 (`itil/knowledge/runbooks.md:133`):

- **0** = OK or WARN only.
- **1** = at least one BREACH.
- **2** = bad command line; nothing was checked.

The early CHG-2026-053 draft named BREACH as exit 3 and WARN as exit 1. That does not match the script. The current PR #2 head (`9ff492e`, lines 27–28) already corrects this. This RFC follows the script and RB-12.

How to act on each code (same rule as CHG-2026-053 at `9ff492e`, lines 27–28, aligned with RB-12):

- **Exit 0:** OK, or WARN only. If there are `[WARN]` lines, put them in the report. The rest of the routine may finish.
- **Exit 1:** at least one `[BREACH]` line. Report and stop. Do not re-publish to "fix" it. Follow RB-12.
- **Exit 2:** bad command line; nothing was checked. Report it as a failed check and stop. Do not treat this as OK.

### What the nightly report adds

Put the script's `RESULT:` line, and any `[BREACH]` or `[WARN]` lines, in the nightly report (CHG-2026-032:53; CHG-2026-053 at `9ff492e`, line 26; the proposed skill text below). A BREACH is reported as a breach, never as success.

### Exact text to add after the owner GO

This RFC does not add the text. After two independent reviewer PASSes on the exact head, and the owner's own GO naming that head, the author adds the following block in three places: the repo skill copy `docs/bot/skills/publicfunds-refresh/SKILL.md`, the live skill on the bot computer, and the nightly routine prompt. Insert it after a successful `scripts/publish-public-data.sh --push` (current skill step 4) and before the review-app health check (current skill step 5). Then renumber the later steps.

The block reuses the CHG-2026-032:53 wording, with the concrete `--raw-url` from RB-12:132, and the script's exit codes:

```
5. After a successful `scripts/publish-public-data.sh --push`, check the live site:
   `python3 scripts/check_live.py --expect-local public-data/v1/manifest.json --raw-url https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json --wait 600`
   - Put its `RESULT:` line and any `[BREACH]` / `[WARN]` lines in the nightly report.
   - Exit 0 means OK, or WARN only. If there are `[WARN]` lines, report them; the rest of the routine may finish.
   - Exit 1 means at least one `[BREACH]` line. A BREACH is reported as a breach, never as success. Do not re-run the publish to "fix" it; report it, still run the health check (`curl -s http://127.0.0.1:8765/healthz`), then stop. Follow RB-12.
   - Exit 2 means a bad command line and nothing was checked. Report it as a failed check and stop. Do not treat this as OK.
   - If the publish step did not run, or did not push, do not run this after-publish command.
```

If the live check exits 1, still run the current skill's health check (`curl -s http://127.0.0.1:8765/healthz`) because a broken audit chain is a security incident, then stop. Do not re-publish.

The repo copy and the live skill must be updated together, or the implementation note must state which one is the source of truth and how the other will be brought in line. Once that is done, update CSI-036 from "nightly routine step needs a separate owner GO" to delivered for the nightly step. Leave D-08 (external uptime check) open.

## Implementation (repo part)

Date: 17 Nov 2026 SAST. Branch `chg-2026-061-nightly-check-live`, from `main` `eebb4c44c82e47da2d8879e2af6b61287ed6cd68` (the 16 Nov 2026 nightly data commit). Approval to build: owner GO for the CHG-061 build and the PR #11 fold, 17 Nov 2026, as reported to the author (PublicFunds). That GO is for a local branch only. It is not a GO to push, to merge, or to change the routine.

### What the branch adds

- `scripts/nightly_check_live.py` (new, CI-116). A small wrapper around the RFC command. Standard library only. Read-only. It never runs the publish script and never pushes.
  - Input: the exit code of `scripts/publish-public-data.sh --push` and a file with that run's saved output.
  - It decides if the publish pushed (see "Push detection"). If it is clear that the publish did not push, it prints `check_live: SKIPPED (<reason>)` and exits 3. If it cannot tell, it prints `check_live: FAILED CHECK (<reason>)` and exits 2. In both cases it does not run `check_live`.
  - If the publish pushed, it runs the RFC command without change: `python3 scripts/check_live.py --expect-local public-data/v1/manifest.json --raw-url https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json --wait 600` (with the Python that runs the wrapper). It uses an overall time limit of 1,200 s, because RB-12 says to call the script under an overall timeout.
  - It prints the `RESULT:` line and every `[BREACH]` and `[WARN]` line, then one `check_live:` line and one `NEXT:` line.
  - The health check runs only on a BREACH (the RFC asks for it only on check_live exit 1).

Exit-code table (wrapper):

| Wrapper exit | When | Routine does |
|---|---|---|
| 0 | check_live exit 0 (OK, or WARN only) | Report any `[WARN]` lines and carry on |
| 1 | check_live exit 1 (at least one `[BREACH]`) | The wrapper runs `curl -s http://127.0.0.1:8765/healthz` (30 s limit) and prints a `healthz:` line. Report it as a breach, never as success. Stop. Do not re-publish. Follow RB-12 |
| 2 | Failed check: check_live exit 2 (bad command line, nothing checked); any other check_live exit code; a crash; the 1,200 s overall limit; **cannot tell if the publish pushed** (no known log line, unreadable log, a publish exit code other than 0, 3 or 4, a git or `ls-remote` error, `origin/main` moved past the data commit or not comparable with it); a bad wrapper command line; `--help` | Report it as a failed check, never as OK. Stop |
| 3 | Skipped, only when it is clear that the publish did not push: the publish refused (exit 3 or 4); the log says nothing to commit; the log says only timestamps changed; or the log says committed with no push line and `origin/main` is still behind that data commit (run without `--push`) | check_live not run. Follow the refresh skill for the publish result |

- `tests/test_nightly_check_live.py` (new, 42 tests). A fake runner stands in for `subprocess.run`, so no test uses the network, git push or the publish script. Two tests run the real `scripts/check_live.py` with no outside network: `--wait 3601` gives exit 2, and a closed local port gives a BREACH (exit 1) and the health-check line (a stub in place of curl).

### Push detection (the publish script's push behaviour)

`scripts/publish-public-data.sh` exits **0** in four cases. Only one of them is a push by the script:

1. `--push`, committed and pushed: it prints `[publish-data HH:MM:SS SAST] pushed to origin/main`.
2. No `--push`: it commits, prints `committed <sha>`, and exits 0 **without a push**.
3. No change in `public-data/`: `nothing to commit`, exit 0.
4. Only timestamps changed: `not committed`, exit 0.

A failed push under `--push` is a non-zero exit (`set -e`), and a refused push is exit 4. So **exit 0 alone does not prove a push**. The wrapper uses the script's own log lines:

- The `pushed to origin/main` line (at the start of a line, in the script's own `[publish-data ... SAST]` form) means pushed.
- `nothing to commit` or `not committed` means not pushed: skip (exit 3).
- Publish exit 3 or 4 (a refusal; the script pushes nothing): skip (exit 3).
- `committed <sha>` with no push line: the wrapper reads `origin/main` with `git ls-remote` and compares it with the data commit (`git rev-parse`, `git merge-base --is-ancestor`; all read-only).
  - Equal (a push outside the script): the check runs, and the `check_live:` line says so.
  - `origin/main` is behind the data commit (the script ran without `--push`): skip (exit 3).
  - `origin/main` moved past the data commit, is not known locally, or does not contain it and is not behind it; or git or `ls-remote` fails: failed check (exit 2).
- Any other publish exit code, a missing or unreadable log, or no known log line: failed check (exit 2).

Only positive evidence gives exit 3. If the publish log format changes, the wrapper gives exit 2 and the routine reports a failed check. It cannot turn the check off without a report.

Finding for the reviewers and the owner. The nightly report of 17 Nov 2026 said that the publish script committed but did not push, and that a manual push was needed (as reported to the author; the author did not see that run). The local git reflog shows the 17 Nov data commit `7cb9faf` at 03:20:45 SAST and the `origin/main` tracking ref updated by a push at 03:21:05 SAST. The reflog cannot show if the script or a manual `git push` made that push. If the routine runs the script without `--push` and then pushes by hand, a check on the push line only would skip the live check on a night when new data did go live. The `git ls-remote` fallback covers that case. A better fix is that the routine always uses `--push` and never pushes by hand. That is a routine decision for the owner, not part of this branch.

### Proposed routine and skill text (draft only; not applied)

This replaces the block in "Exact text to add after the owner GO" for the later step. It needs two reviewer PASSes and the owner's own GO naming the exact head. Put it in the routine prompt, the live skill and the repo skill copy (`docs/bot/skills/publicfunds-refresh/SKILL.md`), after the publish step and before the review-app health check:

```
N. Publish, then check the live site:
   `cd /workspace/publicfunds && scripts/publish-public-data.sh --push > data/publish-run.log 2>&1; echo $?`
   Read data/publish-run.log for the evidence_guard line and the publish result, as before.
   Do not push by hand.
   Then run: `python3 scripts/nightly_check_live.py --publish-exit <that exit code> --publish-log data/publish-run.log; echo $?`
   - Put its RESULT: line, any [BREACH] / [WARN] lines, and its check_live:, healthz: and NEXT: lines in the nightly report.
   - 0: OK, or WARN only. Report any [WARN] lines. The rest of the routine may finish.
   - 1: at least one BREACH. A BREACH is reported as a breach, never as success. The wrapper has already run
     the health check (curl -s http://127.0.0.1:8765/healthz); report its healthz: line. Then stop.
     Do not re-run the publish to fix it. Follow RB-12.
   - 2: a failed check (bad command line, crash, time limit, or it cannot tell if the publish pushed; nothing
     was checked). Report it as a failed check and stop. Do not treat it as OK.
   - 3: skipped, because it is clear that the publish did not push. Report the check_live: SKIPPED line.
     The publish rules (exit 3, exit 4, evidence guard) still apply.
```

Two points need a decision before that step:

- The live skill and the repo skill copy differ. The repo copy has the publish as step 4 and the health check as step 5. The live skill has no numbered publish step: its step 3 only says "when the routine publishes", and its step 4 is the health check. So the publish command is probably in the routine prompt **[unverified: the author did not read the routine prompt]**. The later step must say where the text goes and which copy is the source of truth (as the RFC already asks).
- With `> data/publish-run.log`, the routine reads the `evidence_guard:` line from that file, not from the screen. The CHG-2026-041 rule (a missing line is UNKNOWN) stays the same.

### Differences from the RFC

1. The RFC said the later step changes only the skill and the routine text, and that tests do not change. This branch adds a wrapper script and its tests, as the owner GO of 17 Nov 2026 asked (as reported to the author (PublicFunds)). `scripts/check_live.py` and `tests/test_check_live.py` are not changed.
2. Push detection: the RFC says to skip if the publish did not push. Because exit 0 does not prove a push, the wrapper reads the script's log lines and, for a commit without a push line, compares `origin/main` with `git ls-remote`. It skips (exit 3) only on positive evidence of no push; when it cannot tell, it gives a failed check (exit 2).
3. The wrapper adds an overall time limit of 1,200 s (RB-12 asks for one). A time-out is a failed check (exit 2), not a BREACH.
4. Any check_live exit code other than 0, 1 or 2 is a failed check (exit 2). The RFC names only 0, 1 and 2.
5. The routine text in "Proposed routine and skill text" calls the wrapper, not `check_live.py` direct. The command that the wrapper runs is the RFC command, unchanged.

### Rollback

- Before a merge: close draft PR #13 unmerged and delete the branch.
- After a merge: `git revert -m 1 <merge commit>`. Nothing else in the repo calls the wrapper. `scripts/check_live.py` stays. Git is the rollback; no `.bkp` files.
- Kill switch (CHG-2026-032 and RB-12): to turn the nightly step off, remove the added routine and skill text (write back the previous text). On a BREACH: report it as a breach, do not re-publish, follow RB-12.

### Testing (repo part)

See "Result". Live behaviour is not tested here: the RFC's scratch dry run after a real or rehearsed publish is for the later step.

### Docs follow-ups in this branch (small, docs only)

- KE-001 (`itil/knowledge/known-errors.md`): the "page 3" update was out of date. It now says that every eTenders OCDS run from 19 Oct to 17 Nov 2026 (39 runs in `data/raw/runs.jsonl`) was `partial`, each with HTTP 500 after 5 attempts on one delta page, and that the page changes (page 1 to page 7; page 5 on 12, 14, 15 and 16 Nov; page 4 on 17 Nov). The follow-up note said page 5; the run log shows that the page changes, so the text gives the range. KE-001 is in the published manifest, so the new text goes live with the first nightly after a merge.
- CSI-009 (`itil/registers/csi-register.md`) and the CHG-2026-044 row in `itil/registers/change-log.md` and its Result line: they said "PR open, not merged". CHG-2026-044 was merged in the old private repository on 31 Oct 2026 19:39 SAST and is in the public tree since CHG-2026-051. The restore-check log on the box shows PASS on 1 Nov (two runs), 8 Nov and 15 Nov 2026. CSI-009 now says this. Closing CSI-009 is left to the owner.
- CHG-2026-060 Rollback (`itil/changes/CHG-2026-060-close-059.md`, two places): "Close the PR unmerged" changed to the revert of the real merge `8b4f72b8`.
- `STATUS.md` Current: brought up to 17 Nov 2026 (merges of PR #1 to #4 and #10, draft PR #11, this branch, current live data build).
- The change-log rows for CHG-2026-052 to CHG-2026-055 and CHG-2026-061 said "Open PR, not merged". They now give the merges. This also records those merges (no separate records PR).

## Not changed

- `scripts/check_live.py` behaviour, flags, or exit codes.
- Existing tests, including `tests/test_check_live.py`. (The repo part adds a new test file only.)
- The standing nightly publish GO (data refresh only). Adding the check is a new ops step and needs its own implementation GO naming the exact head.
- Detector logic, review decisions, `public-data/` contents, the dashboard, and RB-12 text.
- D-08, offsite backup, and leftovers from CHG-2026-059.
- No re-publish on BREACH. No auto-fix of the site, of Pages, or of the data.

## Testing (evidence, not claims)

This RFC (docs only):

- [x] `git diff --stat origin/main` shows only `itil/changes/CHG-2026-061-check-live-nightly.md` and `itil/registers/change-log.md`.
- [x] `uv run pytest -q` on this worktree (no warehouse), including `tests/test_no_owner_quotes.py` and `tests/test_popia_names.py`: **865 passed, 61 skipped** in 86.36 s.
- [x] Flag check (done on `8b4f72b8`, quoted above): `--expect-local`, `--raw-url` and `--wait` exist; `--wait 600` is inside 0–3600; `--wait 3601` exited 2 and fetched nothing.

Later implementation (after the owner GO; not in this change):

- A scratch dry run after a real or rehearsed publish prints `RESULT: OK` (or `WARN` / `BREACH` with exit 0 or 1 as above).
- A forced BREACH (for example an unreachable `--site` in a scratch run, not a change to production files) exits 1 and is reported as a breach.
- A bad flag (already probed: `--wait 3601`) exits 2.
- `uv run pytest -q tests/test_check_live.py` still passes (no script change expected).
- Confirm the live skill text matches the repo copy, or record the gap.

## Risk

- False BREACH if GitHub Pages is still deploying after `--wait 600`. Mitigate: keep the wait (RB-12:132 and :134). A checksum mismatch right after a publish can be Pages lag; a persistent mismatch is real. Do not re-push.
- Editing the live skill or the routine prompt outside git can drift from the repo copy. Update both in the same implementation step, or state the source of truth.
- A BREACH stops the publish-related flow. The review-app health check must still run, as stated above.
- Normal-high: two independent reviewer PASSes and the owner's own GO that names the exact head are required. An agent's say-so is not approval.

## How to revert, and the kill switch (reused)

These are the existing commands and steps. This RFC does not invent new ones.

**Rollback of this docs change** (same form as CHG-2026-032:10 and CHG-2026-053 at `9ff492e`, line 11):

> Close the PR unmerged. If merged: `git revert -m 1 <merge commit>`; nothing else depends on the script (git is the rollback; no .bkp files)

(CHG-2026-032 shortens "Close the PR" and adds "nothing else depends on the script". CHG-2026-053 line 11 is the shorter docs form: "Close the PR. If merged: `git revert -m 1 <merge commit>`.")

**Rollback of the later implementation** (CHG-2026-053 at `9ff492e`, line 50):

> Revert the skill/routine edit; the script itself stays. For this docs PR: `git revert -m 1 <merge commit>`.

That is also the way to turn the new nightly step off: remove the added skill and routine-prompt text. The script stays. No `.bkp` files. Git is the rollback for anything committed; for the live skill and the routine prompt, write back the previous text.

**Kill switch on a BREACH (no re-publish, no auto-fix)** — quote from CHG-2026-032:53:

> N. Check the live site: `python3 scripts/check_live.py --expect-local public-data/v1/manifest.json --raw-url <raw manifest URL from RB-11> --wait 600`. Put its `RESULT:` line and any `[BREACH]`/`[WARN]` lines in the report. A BREACH is reported as a breach, never as success. Do not re-run the publish to "fix" it; report and stop.

And from RB-12 (`itil/knowledge/runbooks.md:135`):

> **On a BREACH**: report it as a breach with the output, never as success. Do not re-run the publish blindly. Stale data: check the last refresh report, RB-11 and the data-quality gate (RSK-024). Site down or files mismatched: check GitHub Pages status and the last Pages build; takedown steps are in RB-11. Open a P2 incident if the site shows wrong data.

CHG-2026-053 at `9ff492e`, line 27, says the same in the corrected exit-code form: "On BREACH (exit 1, at least one `[BREACH]` line): report and stop. Do not re-publish to "fix" it. Follow RB-12."

CSI-036 (`itil/registers/csi-register.md:42`) does not add a separate command. It records that the script and RB-12 are already delivered, and that the nightly routine step still "needs a separate owner GO". This RFC is that GO request, not the implementation.

## Approval

This change is Normal-high because it changes the nightly routine once the owner GO is given. Before the author adds the text above, all of the following are required:

1. Two independent reviewer PASSes on the exact head of this RFC (a new head needs new reviews).
2. The owner's own GO naming that exact head. A reviewer PASS is not an owner GO. An agent's say-so is not approval. Silence is not a GO. A GO about another head or another change is not a GO for this head.

The routine prompt change itself is done by the author after that GO. The exact text to add is the block in "Exact text to add after the owner GO". This RFC does not apply that text.

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Independent reviewer 1 | | | |
| Independent reviewer 2 | | | |
| Change authority (owner GO naming the exact head) | | | |

## popia-review verdict: PASS

Repo part (17 Nov 2026): new script, tests and docs text checked. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key. No person, supplier, account or agent is named. Role words only. No owner chat quotes. The only URLs are the public site, the public raw manifest and the local review-app health URL, which were already in the repo. Nothing was removed.

RFC (15 Nov 2026):

Docs-only RFC wording. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key. No person or supplier is named. Role words only; no owner or agent names; no owner chat quotes. Nothing was removed from the text.

## Seen, not touched

- The early CHG-2026-053 exit-code slip (BREACH as exit 3, WARN as exit 1). The current PR #2 head already corrects it. This RFC follows the script.
- CSI-009 / CHG-2026-044 still say "PR open, not merged" even though the backup code is on `main`. Out of scope.
- KE-001 text is behind the current page-5 symptom. Out of scope.
- D-08 (external uptime check) stays open.

## Result

RFC: merged as PR #10 (merge `ceabf99`, 15 Nov 2026 21:26 SAST). The approval for that merge is not in the author's records **[unverified]**.

Repo part (17 Nov 2026, branch `chg-2026-061-nightly-check-live`; draft PR #13, opened 17 Nov 2026 11:43 SAST by the orchestrator at head `72d84812`):

- `uv run pytest -q tests/test_nightly_check_live.py`: **42 passed** (fix commit after review; first commit: 27).
- `uv run pytest -q` (worktree, no warehouse), fix commit: **907 passed, 61 skipped, 0 failed** (first commit `e92d149d`: 892 passed, 61 skipped; baseline on `eebb4c44`: 865 passed, 61 skipped). This includes `tests/test_no_owner_quotes.py` and `tests/test_popia_names.py`, run again after the commit so that the new files are tracked.
- No real publish, push or live check was run. `scripts/publish-public-data.sh` was not run.
- Merge rule: two independent reviewer PASSes on the exact head and the owner's own GO naming that head. The routine and live skill change is a later step with its own owner GO (see "Follow-up (owner decisions)").

## Records carried in this branch

- 17 Nov 2026: `origin/main` `de37f666` merged into this branch (merge only, no rebase). It brings in CHG-2026-063 (PR #12) and the 17 Nov 2026 nightly data commit `7cb9faf`. Conflicts in `itil/registers/change-log.md` and `itil/registers/ci-register.md` were resolved by keeping both sides (CHG-2026-061 row from this branch, CHG-2026-063 row from `main`; CI-116 and CI-117).
- This branch records the CHG-2026-063 merge: PR #12, merge `de37f666`, 17 Nov 2026 11:29 SAST, exact head `3c93c88d`, tag `snapshot-2026-11-17-1129`. Merged by the orchestrator on an owner instruction as reported to the author (PublicFunds), 17 Nov 2026. The PR shows no reviews. Updated: the CHG-2026-063 record (status, environment, approval, outcome), its change-log row, CI-117 and `STATUS.md`.

## Review of head `72d84812` and this commit

A reviewer gave PASS_WITH_CONCERNS on `72d84812` (outside GitHub, as reported to the author (PublicFunds)), with two findings. This commit answers both:

1. **The record, `STATUS.md` and the change-log described the branch as not pushed and with no PR.** They now state that draft PR #13 was opened on 17 Nov 2026 11:43 SAST by the orchestrator at head `72d84812`. Things still to do are in "Follow-up (owner decisions)" below.
2. **The live skill was not in the head.** `docs/bot/live-skill/publicfunds-refresh.LIVE-2026-11-17.md` is a byte-for-byte copy of the live `publicfunds-refresh` skill of 17 Nov 2026 (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`). `docs/bot/live-skill/publicfunds-refresh.PROPOSED-CHG-2026-061.md` is the same text with the proposed step added as a marked draft (step 4; later steps renumbered). `tests/test_live_skill_snapshot.py` checks that the draft differs from the snapshot only by that step. The live skill, the template skill copy (`docs/bot/skills/publicfunds-refresh/SKILL.md`) and the nightly routine prompt are not changed. POPIA scan of the copied text: PASS (no names, accounts, contact details or personal paths; only the repo path, the local review-app address and role words).

## Follow-up (owner decisions)

These items are outside this change. Each one needs the owner's own decision or GO:

1. Apply the draft step (`docs/bot/live-skill/publicfunds-refresh.PROPOSED-CHG-2026-061.md`, step 4) to the live skill and the nightly routine prompt.
2. Choose the source of truth for the refresh skill (the live skill or the template copy) and bring the other copy in line.
3. Decide if the routine always uses `--push` and never pushes by hand ("Push detection").
4. After item 1: update CSI-036 for the nightly step and refresh the live-skill snapshot in the repo. D-08 stays open.
