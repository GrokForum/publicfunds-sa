# CHG-2026-053: Draft — add check_live to the nightly refresh (RFC only)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner GO for outstanding backlog items, 6 Nov 2026 SAST (message t247u), as reported to the author (PublicFunds) |
| Status | **RFC draft.** Open PR for review. Do **not** implement the skill or routine change in this PR |
| Type | Standard while this PR is docs only. The later implementation that edits the live refresh skill or the nightly routine is Normal-high (publishing pipeline / distribution) and needs its own CHG, two PASSes and an owner GO naming that head |
| Environment | Records only in this PR. No code, skill, routine or data change yet |
| CIs affected (this PR) | `itil/changes/CHG-2026-053-check-live-nightly.md`, `itil/registers/change-log.md`, `itil/registers/csi-register.md` (CSI-036 status note) |
| Linked records | CHG-2026-032 (script and RB-12), CSI-036, SLO-PD-1, RB-12 |
| Rollback | Close the PR. If merged: `git revert -m 1 <merge commit>` |

## Goal

After each successful nightly publish, run the existing read-only live check so a broken site or stale data is reported before the 30 h WARN / 48 h BREACH windows on SLO-PD-1.

## Proposed later change (not in this PR)

1. In the refresh skill (repo copy `docs/bot/skills/publicfunds-refresh/SKILL.md` and the live skill on the bot computer), add a step **after** a successful `scripts/publish-public-data.sh --push`:
   ```
   python3 scripts/check_live.py \
     --expect-local public-data/v1/manifest.json \
     --raw-url https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json \
     --wait 600
   ```
2. Put the script's `RESULT:` line and any `[BREACH]` / `[WARN]` lines in the nightly report.
3. On BREACH (exit 3): report and stop. Do not re-publish to "fix" it. Follow RB-12.
4. On WARN (exit 1): report; the rest of the routine may finish.
5. Update CSI-036 from "nightly routine step needs a separate owner GO" to delivered once the implementation CHG merges.

## What stays

- `scripts/check_live.py` behaviour (CHG-2026-032). This RFC does not change the script.
- The standing nightly publish GO (data refresh only). Adding the check is a new product/ops step and needs its own implementation GO.
- No public-data or dashboard change.

## Success (for the later implementation)

- A scratch dry run after a publish prints `RESULT: OK` (or WARN/BREACH with the right exit code).
- A BREACH reaches the owner in the nightly report before 30 h of data age.
- pytest for `tests/test_check_live.py` still passes (no script change expected).

## Risk

- False BREACH if Pages is slow beyond `--wait 600`. Mitigate: keep the wait; report timeout as BREACH per RB-12; do not re-push.
- Editing the live skill outside git can drift from the repo copy. The implementation CHG must update both, or state which one is source of truth.

## How to revert (later implementation)

Revert the skill/routine edit; the script itself stays. For this docs PR: `git revert -m 1 <merge commit>`.

## Result

RFC opened for review. Implementation not started.
