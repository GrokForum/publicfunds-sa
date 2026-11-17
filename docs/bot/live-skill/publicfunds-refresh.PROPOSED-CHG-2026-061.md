---
name: publicfunds-refresh
description: >-
  Use for the daily PublicFunds data refresh (from a scheduled routine or on
  request): ingest all sources, rebuild the warehouse, run the data-quality gate
  and report what changed.
---
<!-- DRAFT (CHG-2026-061). NOT APPLIED. This is the live skill text of 17 Nov 2026 with the proposed CHG-2026-061 step added.
     The live skill and the nightly routine prompt change only after the owner's own GO for that step. -->
# PublicFunds refresh

0. Update the checkout first (CHG-2026-025). Run exactly: `cd /workspace/publicfunds && [ "$(git branch --show-current)" = main ] && [ -z "$(git status --porcelain --untracked-files=no)" ] && git fetch -q origin && git merge --ff-only origin/main`
   - Any non-zero exit (not on `main`, tracked file modified, offline fetch, diverged, index.lock) means **stop and report**: skip steps 1 to 6 (including the healthz check and any publish), run nothing else, and do not push, reset or clean. In the routine's final SendToUser message give the error text, `git status --short`, and the local HEAD and `origin/main` SHAs (`git rev-parse --short HEAD origin/main`).
   - "Already up to date" is a pass (also when local `main` is ahead of origin with an unpushed data commit). Never `reset --hard`.
1. `cd /workspace/publicfunds && uv run thusa run > data/refresh-$(date +%F).log 2>&1; echo $?`
   - **0** means the build is releasable.
   - **2** means a data-quality check failed. Don't publish anything; summarise the failed checks and follow runbook RB-01.
2. Read the latest entries in `data/raw/runs.jsonl` and report each source's status. For any source that is not `ok`:
   - if a known error already matches it (`itil/knowledge/known-errors.md`), name it;
   - otherwise draft an incident with **publicfunds-itil**.
   Never bypass a block (403, login, WAF).
3. Report briefly: the coverage headline, flag counts by detector, and new flags or flags with "evidence changed" (`uv run pf review list --status stale`).
   - **Publish guard line (CHG-2026-041, applied 26 Oct 2026 with the owner's approval).** When the routine publishes with `scripts/publish-public-data.sh --push`, the script prints one line starting `evidence_guard:`. Add a line "Evidence guard:" to the report with that line and up to three note lines under it. Only a bare `evidence_guard: pass` is quiet. If the line is anything else (`pass (N notes)`, `warn (N notes)`, `BLOCKED`, `not an evidence-guard refusal`, `UNKNOWN`) or is **missing**, treat it as not passed (a missing line is UNKNOWN), and begin the report with `ACTION: publish needs attention` and quote the line. Never describe an `UNKNOWN` or missing guard line as a pass.
   - If the publish script exits **3**, the export was refused: nothing was published, the files in `public-data/` are left as they are, nothing was committed or pushed. Do not retry and do not edit data. Report to the owner at once: the exit code, the `evidence_guard:` line (`BLOCKED` means the evidence guard refused; `not an evidence-guard refusal` means the cause may be the quality gate, the safety scan, another refusal or a crash, so read `data/publish-data.log` and quote its last lines with `data/publish-data.json`). `scripts/check_live.py` warns at 30 h of data age and breaches at 48 h, so the owner must hear before then.
   - If it exits **4**, stop and report (other changes, wrong branch, main moved). Any other non-zero exit: stop and report too.
4. **[DRAFT, CHG-2026-061: proposed new step; not in the live skill]** Publish, then check the live site:
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
5. Check `curl -s http://127.0.0.1:8765/healthz`. If it is not ok, run `scripts/review-app.sh restart`. A broken audit chain is a security incident: stop and tell the user.
6. Never confirm or reject flags here. Reviews happen only in **publicfunds-review**, on the user's instruction.
