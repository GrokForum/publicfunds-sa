# Nightly refresh routine prompt (CHG-2026-065)

This file holds the proposed prompt text for the nightly PublicFunds refresh routine (03:00 SAST). It goes with `publicfunds-refresh.MASTER.md`. The routine prompt and the live skill change together, in one step. If only the skill changes and the old prompt still publishes, the night publishes twice. If only the prompt changes, the night does not publish.

The author (PublicFunds) cannot read the routine prompt. The repo has no copy of the current prompt (CHG-2026-061 records this as **[unverified]**). The text below is therefore written in full from the master skill. It is not an edit of the current prompt. Before the orchestrator applies it, the orchestrator reads the current prompt, keeps a copy of it outside git as the rollback text, and replaces the whole prompt with the text between the two marker lines.

<!-- BEGIN ROUTINE PROMPT -->
Run the nightly PublicFunds data refresh. This is the nightly run. Load the publicfunds-refresh skill and follow the nightly-run path: do its steps 0 to 6 in order, exactly as written, including step 4 (the publish). The skill's rule for a run on request does not apply here.

- Step 4 of the skill is the only publish of the night. It runs `scripts/publish-public-data.sh --push` only if step 1 returned 0, and then runs `scripts/nightly_check_live.py` whatever the publish exit code. Do not run the publish script at any other point of this routine. Always use `--push`. Do not push by hand.
- If step 0 or step 1 says stop, or step 4 says stop, stop there. Do not re-run the publish to fix a problem.
- Never confirm or reject flags.

At the end, send one report with SendToUser. Put in it:
- the step 0 result, and the step 1 exit code;
- each source's status from step 2, with the known error or the draft incident for each source that is not ok;
- the coverage headline, flag counts by detector, and new or "evidence changed" flags (step 3);
- the publish exit code (or that step 4 did not publish because step 1 did not return 0) and the "Evidence guard:" line (step 4); begin the report with `ACTION: publish refused` or `ACTION: publish needs attention` when the skill says so; if both apply, `ACTION: publish refused` comes first, then `ACTION: publish needs attention`. On a refused publish (exit 3) the report always begins with `ACTION: publish refused`; it begins with `ACTION: publish needs attention` only when there was no refusal;
- the RESULT:, check_live:, healthz: and NEXT: lines from `scripts/nightly_check_live.py`, and any [BREACH] or [WARN] lines;
- the review-app health check result (step 5).
A BREACH, a failed check, a refused publish or a skipped publish is reported as that, never as success.
<!-- END ROUTINE PROMPT -->
