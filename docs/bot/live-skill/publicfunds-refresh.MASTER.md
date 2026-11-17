---
name: publicfunds-refresh
description: >-
  Use for the daily PublicFunds data refresh (from a scheduled routine or on
  request): ingest all sources, rebuild the warehouse, run the data-quality gate
  and report what changed.
---
# PublicFunds refresh

Two kinds of run: the nightly routine does steps 0 to 6, and step 4 is its only publish. A run on request does steps 0 to 3 and then 5 and 6, and reports; it does not publish unless the owner asks for a publish (see step 4). On the nightly run, the routine prompt decides whether the report is sent (it sends nothing when all is well).

0. Before any git pull or push (CHG-2026-066), in this order:
   - **Wait for any other pipeline run.** Run `pgrep -f '[t]husa run' > /dev/null && echo running || echo none`. If it prints `running`, another `thusa run` is in progress on this computer: wait for it to end (check again every 60 s) and do not start a second run.
   - **Account and origin guard.** Run exactly: `cd /workspace/publicfunds && export GH_TOKEN="$(gh auth token --user GrokForum)" && [ -n "$GH_TOKEN" ] && gh auth setup-git && git remote get-url origin | grep -Eq 'github\.com[:/]GrokForum/publicfunds-sa(\.git)?$'; echo $?`
     Every git pull and push in this run goes out as the GrokForum GitHub account, never as any other GitHub account (the computer's active `gh` account can change). Keep `GH_TOKEN` exported for the whole run. If a later command runs in a new shell, run this guard again before any git pull or push. A non-zero exit means **stop and report**: begin the report with `ACTION: account or origin check failed`, skip steps 1 to 6, and do not pull, publish or push.
   Then update the checkout (CHG-2026-025). Run exactly: `cd /workspace/publicfunds && [ "$(git branch --show-current)" = main ] && [ -z "$(git status --porcelain --untracked-files=no)" ] && git fetch -q origin && git merge --ff-only origin/main`
   - Any non-zero exit (not on `main`, tracked file modified, offline fetch, diverged, index.lock) means **stop and report**: skip steps 1 to 6 (including the healthz check and any publish), run nothing else, and do not push, reset or clean. In the routine's final SendToUser message give the error text, `git status --short`, and the local HEAD and `origin/main` SHAs (`git rev-parse --short HEAD origin/main`).
   - "Already up to date" is a pass (also when local `main` is ahead of origin with an unpushed data commit). Never `reset --hard`.
1. `cd /workspace/publicfunds && uv run thusa run > data/refresh-$(date +%F).log 2>&1; echo $?`
   - **0** means the build is releasable.
   - **2** means a data-quality check failed. Don't publish anything; summarise the failed checks and follow runbook RB-01. Record an incident with **publicfunds-itil** and commit it locally (no push).
2. Read the latest entries in `data/raw/runs.jsonl` and report each source's status. For any source that is not `ok`:
   - if a known error already matches it (`itil/knowledge/known-errors.md`), name it;
   - otherwise (a source fails in a new way) record an incident with **publicfunds-itil** and commit it locally (no push).
   Never bypass a block (403, login, WAF).
3. Report briefly: the coverage headline, flag counts by detector, and new flags or flags with "evidence changed" (`uv run pf review list --status stale`).
4. **Nightly run only.** Only if step 1 returned **0**: publish, then check the live site (CHG-2026-061, CHG-2026-065). If step 1 returned anything else, do not publish.
   On a run on request, skip this step: do not publish unless the owner asks for a publish. If the owner asks, run this step with the same condition: only if step 1 returned **0**.
   If step 4 was skipped, add no publish ACTION line; report the step 1 result.
   This is the only publish of the night. The nightly routine prompt runs this skill and does not publish by itself.
   The push of `public-data/` to `main` of GrokForum/publicfunds-sa by this step is the standing pre-approved change (owner approval of 23 Oct 2026, recorded in `changes/CAB-DECISION.md`; the repo moved to GrokForum on 1 Nov 2026). It covers this data refresh only and updates the live dashboard. Never push anything else and never merge PRs.
   Before the publish command, in this order (CHG-2026-066):
   - **Account and origin guard again.** Run the step 0 guard command. A non-zero exit: do not publish; begin the report with `ACTION: account or origin check failed`; skip the rest of this step.
   - **POPIA release check.** Make the candidate public data without touching `public-data/`: `cd /workspace/publicfunds && rm -rf data/popia-candidate && mkdir -p data/popia-candidate && cp -a public-data/v1 data/popia-candidate/v1 && uv run pf publish-data --out data/popia-candidate/v1 > data/popia-candidate.json 2> data/popia-candidate.log; echo $?`
     If that exits 0, run `git diff --no-index --stat public-data/v1 data/popia-candidate/v1` and read every changed line. Use the **popia-review** skill's release check (copy at `/home/box/shared-laws/popia-review-SKILL.md` if the skill cannot be loaded): no ID, phone or account numbers, no emails, no addresses and no names of private persons.
     - PASS: go on to the publish command.
     - BLOCK: do not publish. Begin the report with `ACTION: publish blocked (POPIA)`. Say what kind of item was found and in which file, never the personal data itself. Skip the rest of this step.
     - The candidate export exits 3 (export refused, nothing written): skip the release check and go on to the publish command. It refuses in the same way, and the publish rules below report it.
     - The candidate export exits with any other non-zero code: the check cannot run, so treat it as BLOCK (`ACTION: publish blocked (POPIA)`, reason: release check could not run; quote the last 5 lines of `data/popia-candidate.log`).
     For a blocked publish, `ACTION: account or origin check failed` or `ACTION: publish blocked (POPIA)` is the only publish ACTION line; the publish exit code rules below do not apply, because the publish did not run.
   `cd /workspace/publicfunds && scripts/publish-public-data.sh --push > data/publish-run.log 2>&1; echo $?`
   Always use `--push`. Do not push by hand. Read data/publish-run.log for the evidence_guard line and the publish result.
   Then, whatever the publish exit code, run the live check wrapper. It only reads; it never publishes or pushes:
   `python3 scripts/nightly_check_live.py --publish-exit <that exit code> --publish-log data/publish-run.log; echo $?`
   - **Publish guard line (CHG-2026-041, applied 26 Oct 2026 with the owner's approval).** The publish script prints one line starting `evidence_guard:`. Add a line "Evidence guard:" to the report with that line and up to three note lines under it. Only a bare `evidence_guard: pass` is quiet: it adds no ACTION line of its own. If the line is anything else (`pass (N notes)`, `warn (N notes)`, `BLOCKED`, `not an evidence-guard refusal`, `UNKNOWN`) or is **missing**, treat it as not passed (a missing line is UNKNOWN) and quote the line. The first ACTION line of the report depends on the publish exit code. If the publish was refused (exit 3, see the next bullet), the report always begins with `ACTION: publish refused`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. If the publish failed (exit 4 or any other non-zero exit, see the bullets below), the report always begins with `ACTION: publish failed`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. If the publish exited 0 and the guard line is not a bare pass, the report begins with `ACTION: publish needs attention`. A bare pass with publish exit 0 adds no ACTION line. Never describe an `UNKNOWN` or missing guard line as a pass.
   - If the publish script exits **3**, the export was refused: nothing was published, the files in `public-data/` are left as they are, nothing was committed or pushed. Do not retry and do not edit data. The wrapper prints `check_live: SKIPPED` and exits 3. Begin the report with `ACTION: publish refused`. If the guard line is not a bare pass (for example `BLOCKED`), put `ACTION: publish needs attention` on the next line (refused first, then needs attention). Then give first: the exit code, the `evidence_guard:` line (`BLOCKED` means the evidence guard refused; `not an evidence-guard refusal` means the cause may be the quality gate, the safety scan, another refusal or a crash, so read `data/publish-data.log` and quote its last lines with `data/publish-data.json`). `scripts/check_live.py` warns at 30 h of data age and breaches at 48 h, so the owner must hear before then.
   - If it exits **4** (other changes, wrong branch, main moved), nothing was pushed. The wrapper prints `check_live: SKIPPED` and exits 3. Begin the report with `ACTION: publish failed`. If the guard line is not a bare pass, put `ACTION: publish needs attention` on the next line (failed first, then needs attention). Record an incident with **publicfunds-itil** and commit it locally (no push). Stop after the wrapper and report. Do not retry.
   - Any other non-zero publish exit: the wrapper cannot tell if the publish pushed. It prints `check_live: FAILED CHECK` and exits 2. Begin the report with `ACTION: publish failed`. If the guard line is not a bare pass, put `ACTION: publish needs attention` on the next line (failed first, then needs attention). Record an incident with **publicfunds-itil** and commit it locally (no push). Stop and report, and check by hand if new data went live. Do not retry.
   The wrapper's exit code:
   - Put its RESULT: line, any [BREACH] / [WARN] lines, and its check_live:, healthz: and NEXT: lines in the nightly report.
   - 0: OK, or WARN only. The live manifest shows the new build (the check_live `local.build` line). Report any [WARN] lines. The rest of the routine may finish.
   - 1: at least one BREACH. A BREACH is reported as a breach, never as success. The wrapper has already run
     the health check (curl -s http://127.0.0.1:8765/healthz); report its healthz: line. Then stop.
     Do not re-run the publish to fix it. Follow RB-12.
   - 2: a failed check (bad command line, crash, time limit, or it cannot tell if the publish pushed; nothing
     was checked). Report it as a failed check and stop. Do not treat it as OK.
   - 3: skipped, because it is clear that the publish did not push (publish exit 3 or 4, or nothing new to push).
     check_live was not run. Report the check_live: SKIPPED line. The publish rules above still apply.
   **Back up state** (CHG-2026-044 appendix A, CHG-2026-066). Do this only if step 1 returned 0 and the publish exited 0. Do it after the live check, also when the wrapper said stop (the backup does not publish).
   `cd /workspace/publicfunds && scripts/backup-state.sh > data/backup-run.log 2>&1; echo $?`
   - 0: put the `backup: ok` line in the report. It adds no ACTION line.
   - Any other exit code: add `ACTION: backup failed` to the report, after any publish ACTION line, and quote the `backup: FAILED` line. Do not retry. Do not delete any backup. The routine prompt also tells the orchestrator agent (the failed line only, no data).
   - Backups stay on this computer only. Never commit, push or publish them.
5. Check `curl -s http://127.0.0.1:8765/healthz`. If it is not ok, run `scripts/review-app.sh restart`. A broken audit chain is a security incident: stop and tell the user.
6. Never confirm or reject flags here. Reviews happen only in **publicfunds-review**, on the user's instruction. Never push anything except the step 4 publish of `public-data/`, and never merge PRs.
