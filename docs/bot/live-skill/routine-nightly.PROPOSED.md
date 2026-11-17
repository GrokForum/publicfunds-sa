# Nightly refresh routine prompt (CHG-2026-065, CHG-2026-066)

This file holds the proposed prompt text for the nightly PublicFunds refresh routine (03:00 SAST). It goes with `publicfunds-refresh.MASTER.md`. The routine prompt and the live skill change together, in one step. If only the skill changes and the old prompt still publishes, the night publishes twice. If only the prompt changes, the night does not publish.

The prompt that was live on 17 Nov 2026 is kept outside git, in the private deploy notes, as the rollback text. It is not copied or quoted here. CHG-2026-066 compared it with the master skill and this prompt, duty by duty (see `tests/test_live_skill_snapshot.py`, `DUTIES`). The master skill holds the steps; this prompt holds the duties that only the routine can do: it starts the run, it decides whether to send the report, and it tells the orchestrator agent about a backup failure.

The text between the two marker lines is the whole prompt. It has one placeholder, `<orchestrator agent id from the private deploy notes>`. At the deploy, the orchestrator replaces it with the agent id from the private deploy notes. The id is not kept in git.

<!-- BEGIN ROUTINE PROMPT -->
Run the nightly PublicFunds data refresh in /workspace/publicfunds. This is the nightly run. Load the publicfunds-refresh skill and follow the nightly-run path: do its steps 0 to 6 in order, exactly as written, including step 0 (wait for any other pipeline run, and the account and origin guard before any git pull or push) and step 4 (the POPIA release check, the publish, the live check and the backup). The skill's rule for a run on request does not apply here.

- Step 4 of the skill is the only publish of the night. It runs `scripts/publish-public-data.sh --push` only if step 1 returned 0 and the POPIA release check passed, and then runs `scripts/nightly_check_live.py` whatever the publish exit code. Do not run the publish script at any other point of this routine. Always use `--push`. Do not push by hand.
- Every git pull and push goes out as the GrokForum GitHub account (the skill's account and origin guard), never as any other GitHub account.
- The push of `public-data/` by step 4 is the standing pre-approved change (`changes/CAB-DECISION.md`). It covers this data refresh only. Never push anything else, never merge PRs, never confirm or reject flags.
- Incidents are committed only on the local branch `incidents/local`, in the skill's incidents worktree, never on `main`; that branch is never pushed. The main checkout stays on `main` for every pull and the publish.
- If step 0 or step 1 says stop, or step 4 says stop, stop there. Do not re-run the publish to fix a problem.
- On a backup failure (step 4), also send the `backup: FAILED` line only, no data, to the orchestrator agent with SendToAgent, priority true, agent id `<orchestrator agent id from the private deploy notes>`.

When to report (quiet rule): send a report with SendToUser only when it has an ACTION line or there is a failure: a step 0 stop, a nightly skipped because another run was still in progress after 2 hours, a failed data-quality gate or a failed source, a POPIA BLOCK, a refused, blocked or failed publish, a BREACH or a failed check from the live check, an HTTPS or manifest failure on the live site, a failed backup, a broken audit chain, or new high-severity flags (give counts and the top few, marked as unreviewed). Otherwise send nothing: when the run succeeded, the guard line is a bare pass, the live check is OK and the backup is ok, there is no report.

When you send a report, put in it:
- the ACTION lines first, in the order the skill gives. If step 0 stops the run, its ACTION line is the only one: `ACTION: nightly skipped (another run still in progress after 2h)` when another run was still in progress after 2 hours, or `ACTION: account or origin check failed`. Otherwise the publish ACTION lines come first: begin the report with the ACTION lines the skill gives: on publish exit 3, `ACTION: publish refused`; on publish exit 4 or any other non-zero exit, `ACTION: publish failed`; then, if the guard line is not a bare pass, `ACTION: publish needs attention` on the next line. On publish exit 0, the report begins with `ACTION: publish needs attention` only when the guard line is not a bare pass. A bare pass with publish exit 0 adds no ACTION line. If step 4 was skipped, add no publish ACTION line; report the step 1 result. A blocked publish has one ACTION line instead: `ACTION: publish blocked (not on main)`, `ACTION: account or origin check failed` or `ACTION: publish blocked (POPIA)`. `ACTION: backup failed` comes after any publish ACTION line;
- the step 0 result, and the step 1 exit code;
- each source's status from step 2, with the known error or the incident for each source that is not ok;
- the coverage headline, flag counts by detector, and new or "evidence changed" flags (step 3);
- the publish exit code (or why step 4 did not publish) and the "Evidence guard:" line (step 4); for a POPIA BLOCK, the kind of item and the file, never the personal data itself;
- the RESULT:, check_live:, healthz: and NEXT: lines from `scripts/nightly_check_live.py`, and any [BREACH] or [WARN] lines;
- the `backup: ok` or `backup: FAILED` line;
- the review-app health check result (step 5).
A BREACH, a failed check, a refused, blocked or failed publish, or a skipped publish is reported as that, never as success.
<!-- END ROUTINE PROMPT -->
