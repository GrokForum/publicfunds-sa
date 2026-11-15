# CHG-2026-061: Add check_live to the nightly refresh after a successful publish (RFC only)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Follow-on to CSI-036, CHG-2026-032 and the CHG-2026-053 RFC (open PR #2). Drafted 15 Nov 2026. This record is not a merge GO and does not implement the step. |
| Status | **RFC only.** Branch `feat/chg-2026-061-check-live-nightly`, open as draft PR #10, not merged. Do **not** edit the live skill, the repo skill copy, or the nightly routine prompt in this change. |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline / distribution). The later step, after an owner GO that names the exact head, changes the nightly routine. This RFC commit itself is docs only. |
| Environment | Docs only in this change. Pre-change `main` is `8b4f72b80de0f31831bba689130a251488e791bd` (tag `snapshot-2026-11-15-1817`). The later implementation runs on the bot computer (live refresh skill and the nightly routine prompt) and updates the repo skill copy. Nothing is published by this RFC. |
| CIs affected (this RFC) | `itil/changes/CHG-2026-061-check-live-nightly.md`, `itil/registers/change-log.md` |
| CIs affected (later implementation, after the owner GO) | Live refresh skill; repo copy `docs/bot/skills/publicfunds-refresh/SKILL.md`; the nightly routine prompt; `itil/registers/csi-register.md` (CSI-036 status) |
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

## Not changed

- `scripts/check_live.py` behaviour, flags, or exit codes.
- Tests, including `tests/test_check_live.py`.
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

Docs-only RFC wording. No SA ID, passport, phone, email, address, account number, plate, precise location, credential or key. No person or supplier is named. Role words only; no owner or agent names; no owner chat quotes. Nothing was removed from the text.

## Seen, not touched

- The early CHG-2026-053 exit-code slip (BREACH as exit 3, WARN as exit 1). The current PR #2 head already corrects it. This RFC follows the script.
- CSI-009 / CHG-2026-044 still say "PR open, not merged" even though the backup code is on `main`. Out of scope.
- KE-001 text is behind the current page-5 symptom. Out of scope.
- D-08 (external uptime check) stays open.

## Result

RFC open as draft PR #10, not merged. Not implemented. The nightly routine, the skills, the scripts and the tests are unchanged by this commit.
