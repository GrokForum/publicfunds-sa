# CHG-2026-069: Serve the PublicFunds public site from a separate GrokForum GitHub repository (DRAFT)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 18 Nov 2026 08:11 SAST, given by the owner in the orchestrator's chat and relayed to the author. The reviewers did not hear it first-hand. This record is the plan. |
| Status | **DRAFT RFC.** Drafted on 18 Nov 2026 on branch `chg-2026-069-public-site-repo` from `main` `76688eca`. Rev 2 records reviewer concerns on `3756dcd3`. Rev 3 records reviewer concerns on `a4e6b336`. This record is not an execution GO. Nothing was published to a new repository, and the custom domain was not moved. |
| Type | **Normal-high** (`itil/change-enablement.md`: distribution, GitHub Pages, the publishing pipeline, secrets and auth). Two independent reviewer PASSes on the exact RFC head, then the owner's GO naming that head. Creating the repository, the first publish and the hostname cutover need a second, separate owner GO at execution time (section 11). |
| Environment | DEV: a local staging tree of the site files, held on the author's computer. TEST: GitHub Pages on the new repository at its `github.io` URL, before the custom domain is moved. PROD: `https://publicfunds.grokforum.site/` served from the new repository. The hostname cutover is PROD. |
| Depends on | PR #18 (CHG-2026-067 code) merged, and the first nightly publish after that merge masked the live data, before the first publish into the new repository. |
| CIs affected | A new public GitHub repository under GrokForum and its Pages settings; DNS and `CNAME` for `publicfunds.grokforum.site`; the nightly refresh skill and routine prompt; `scripts/check_live.py` and `scripts/nightly_check_live.py` (the default hostname stays the same after the cutover; `RAW_URL` moves to the site repository at S11); Pages settings on GrokForum/publicfunds-sa; this record; `itil/registers/change-log.md`; `STATUS.md`. |
| Linked records | CHG-2026-067 (Q7: serve only the site files from Pages, as a separate change; DRAFT label, robots, privacy page, title masks, PR #18); CHG-2026-068 (history rewrite of the data repository, PR #19; Q10 is the same owner question as Q5 of this record); CHG-2026-007 (GitHub Pages); CHG-2026-061 (`check_live`); CHG-2026-063 (robots); CHG-2026-065 and CHG-2026-066 (skill master and nightly publish); CHG-2026-050 (fresh repository, Pages and DNS). |
| Rollback | Move the custom domain back to Pages on GrokForum/publicfunds-sa, wait for a new HTTPS certificate, and run `check_live` against `https://publicfunds.grokforum.site/`. DNS does not need to change (section 5). Because the live site sends HSTS, the wait for the certificate is a hard HTTPS outage (up to 1 hour **[unverified]**, GitHub Pages documentation). Rollback through the data repository's Pages ends once that repository goes private. See section 6. |

## 1. What and why

Owner decision, 18 Nov 2026 08:11 SAST, given by the owner in the orchestrator's chat and relayed to the author (the reviewers did not hear it first-hand): the PublicFunds public webpage is served from a separate public GitHub repository under GrokForum. Only the website gets advertised. The data repository goes private when the merged site goes live with its own public repository. That visibility change is a later change. This RFC does not make GrokForum/publicfunds-sa private.

This record is the separate follow-up named in CHG-2026-067 Q7. The owner's answer to that question (18 Nov 2026 05:40 SAST, as relayed by the orchestrator to the author) was to serve only the site files from GitHub Pages, in a separate change. This RFC replaces that follow-up.

Today, GitHub Pages on GrokForum/publicfunds-sa is a legacy build from `main`, path `/` (measured in CHG-2026-068). It serves the whole repository root, including review-app templates and records (CHG-2026-067, finding N-3). A new repository that holds only the built site files, with fresh history, removes that. It also avoids copying the data repository's history and its `refs/pull/*` residue into the host of the public site.

## 2. Proposed repository (Q1)

The author's recommendation is the name `publicfunds-site`, so the repository is GrokForum/publicfunds-site. The owner chooses the name (Q1).

Checked by the author on 18 Nov 2026 08:15 SAST, after confirming the origin of the data worktree was `https://github.com/GrokForum/publicfunds-sa.git`, with read-only `gh api` and the GrokForum token: among GrokForum repositories whose names contain `publicfunds`, only `publicfunds-sa` was listed. A read of `repos/GrokForum/publicfunds-site` returned HTTP 404. Whether a private repository with that name exists is **[unverified]**.

The new repository is public. It carries only the listed site files in section 3. It has fresh history: no commits are copied from GrokForum/publicfunds-sa, and it has no `refs/pull/*` residue from that repository.

## 3. What is published into it

There is no `dist/public/` output in the tree today. `config/publication.yaml` uses that path as the name of a public snapshot. GitHub Pages today serves the repository root. The published tree is an assembled allowlist. **Only the listed files** are copied. The planned allowlist test fails if the staging tree contains any file that is not on this list.

Checked on `main` `76688eca` and on the CHG-2026-067 code in PR #18 (`chg-2026-067-impl`, head `5f6a319f` at this check). `apps/public-dashboard/` also holds `README.md` and `GROK_BUILD_PROMPT.md`. No site page loads those two files. Copying the whole directory would publish them. The pages that are loaded are:

- `index.html` (the stub). It links to `apps/public-dashboard/` and sets `og:image` and `twitter:image` to `https://publicfunds.grokforum.site/apps/public-dashboard/og-card.png`.
- `apps/public-dashboard/index.html` (the dashboard). It loads `../../public-data/v1/manifest.json` and `../../public-data/v1/feed.json` (and then the files the manifest names, all under `public-data/v1/`). It uses the same `og-card.png` URL. After PR #18 it also links to `/privacy/`.
- `apps/public-dashboard/og-card.png` (the Open Graph image). It is not at the repository root.

`robots.txt` (`Disallow: /`) is needed, so the new host keeps the same robots policy. After PR #18, `privacy/index.html` is needed (every site page links to `/privacy/`) and `404.html` is needed (GitHub Pages serves it for unknown paths). `.nojekyll` is needed so Pages does not run Jekyll on the tree.

Allowlist (only these files):

- `index.html`
- `apps/public-dashboard/index.html`
- `apps/public-dashboard/og-card.png`
- `robots.txt`
- `.nojekyll`
- After PR #18 is on `main`: `privacy/index.html` and `404.html`
- Every file under `public-data/v1/` that the export writes. On `76688eca` those files are: `manifest.json`, `feed.json`, `flags.json`, `changes.json`, `coverage.json`, `departments.json`, `municipalities.json`, `prices.json`, `tenders-summary.json`, and `awards-2017.json` to `awards-2026.json`. A later export may add a file under `public-data/v1/`; that file is then allowed. A file outside `public-data/v1/` is not allowed unless it is named above.

Not on the list, and the allowlist test must fail if they appear: `apps/public-dashboard/README.md`, `apps/public-dashboard/GROK_BUILD_PROMPT.md`, and every other path (scripts, tests, `thusa/`, `itil/`, records, source, lock files, review-app templates).

`CNAME` is not on the first-publish allowlist. S3 publishes without a `CNAME` file. S6 sets the custom domain in the Pages settings. From the next publish after S6, `CNAME` (`publicfunds.grokforum.site`) joins the allowlist.

The exact list is fixed in the later implementation. The allowlist test fails on any file it does not expect. GitHub Pages on the new repository uses the DRAFT label, `robots.txt` with `Disallow: /` plus `noindex`, the privacy page, and the mask scan on the tree that is published into it.

## 4. How the nightly publishes into it

This design is grounded in `scripts/publish-public-data.sh`, `scripts/nightly_check_live.py` and the live `publicfunds-refresh` skill (byte-identical to `docs/bot/live-skill/publicfunds-refresh.MASTER.md` at this draft, 18 Nov 2026), which were read and were not run. The routine duties are those in `docs/bot/live-skill/routine-nightly.PROPOSED.md`, which matches the report rules in that skill.

Today the nightly, at step 4, and only if step 1 returned 0, runs a POPIA candidate check and then `scripts/publish-public-data.sh --push`. That script runs `uv run pf publish-data`, refuses on a data-quality, safety or evidence-guard failure (exit 3), commits only `public-data/`, and pushes only from `main` as a fast-forward to `origin/main` of GrokForum/publicfunds-sa. The standing pre-approval in `changes/CAB-DECISION.md` covers that data push only. The account and origin guard (CHG-2026-066) takes `GH_TOKEN` from `gh auth token --user GrokForum` and requires that origin to match `github.com/GrokForum/publicfunds-sa`. After PR #18, `pf publish-data` also runs the fail-closed titled-supplier scan and writes the masks and `doc` `null`. The live check then runs `scripts/nightly_check_live.py` and `scripts/check_live.py` against `https://publicfunds.grokforum.site`. The wrapper hard-codes `RAW_URL` to `https://raw.githubusercontent.com/GrokForum/publicfunds-sa/main/public-data/v1/manifest.json`.

The implementation of the site-repository publish is a later code change, after this plan is approved. The plan is as follows.

### 4.1 Build output

After a successful export, assemble a staging tree from the allowlist in section 3, using the exported `public-data/v1` and the listed site pages from `main`. That staging tree is the only input to the push to the site repository. There is no separate front-end build step today. The allowlist test runs on that tree and fails if any file is not on the list.

### 4.2 Gates before the site-repository push

All of these must pass. Stop on any failure. Nothing is pushed to the site repository if a gate fails.

1. The existing nightly pre-checks still pass: step 1 returned 0; the checkout is on `main`; the account and origin guard for the data repository passed; the POPIA candidate check passed; `pf publish-data` exited 0, including the evidence guard and, after PR #18, the titled-supplier scan.
2. The data push in step 4 has finished (section 4.5: data push, then site push, then the live check).
3. A second mask scan on every file in the staging tree: 0 hits for the private titled-supplier list (exact and case-insensitive), and the same fail-closed titled-person rule as the export. A masked row in the tree must have `doc` `null`.
4. A POPIA release check on the staging tree (the popia-review release check), not only on `public-data/`.
5. The allowlist test: only the listed files are present.
6. A site-remote guard: the push URL is exactly `github.com/GrokForum/<name chosen at Q1>`. The token used for this push writes to that repository and is not used, in the same command, to push the data repository.
7. The first publish runs only after PR #18 is on `main` and the first masked nightly has passed, so the new repository's history never holds the unmasked values.

### 4.3 Push identity and token scope

Pushes to the site repository go out as the GrokForum account, as with the data-repository publish. The author's recommendation is a token (or a fine-grained permission) that can write contents only on the site repository, stored privately, not in git. The standing approval for `public-data/` on GrokForum/publicfunds-sa does not cover this push. A new standing approval is needed before the nightly may push to the site repository (Q2).

### 4.4 History of the site repository (Q3)

| Option | Action | Effect |
|---|---|---|
| a | One new commit on `main` for each successful publish. | The history is a public record of what went live. Every published tree stays in public git forever. If a later mask (or any other removal) is needed, the site repository has the same history problem as CHG-2026-068. The first commit is the first masked tree, so the site repository never holds the *present* unmasked values, but a future unmasking mistake would remain in old commits. A bad publish can be replaced by publishing the previous tree again, from this history. |
| b | Each publish is a single orphan commit that replaces `main`. | The site repository then holds only the latest tree. Older published trees are not in public git. Rollback of a bad publish needs a private copy or tag of the previous tip, kept off this repository. |

Rollback through Pages on the data repository works only while that repository is public and still has Pages. Once it goes private (section 8), that rollback path ends. After that, rollback is only from the site repository's own history (option a) or from a private copy (option b, and also wise for a).

The author's recommendation: option a, and also keep a private bundle or tag of each published tip. That keeps a public record of what went live, and it still allows a rollback after the data repository is private. If the owner does not want historical trees in public git, choose option b and keep the private rollback copy.

### 4.5 Order of the nightly publish, and duties kept

At S11, step 4 of the nightly becomes: data push, then site push, then the live check. `scripts/nightly_check_live.py` moves its hard-coded `RAW_URL` from the data repository's raw manifest to the site repository's raw manifest (`https://raw.githubusercontent.com/GrokForum/<name>/main/public-data/v1/manifest.json`). The default `check_live` site URL stays `https://publicfunds.grokforum.site`.

Today the wrapper skips the live check when the data-publish log shows `no change in public-data/; nothing to commit` or `only timestamps changed; not committed` (wrapper exit 3; `NOTHING_RE` in `scripts/nightly_check_live.py`). After S11, the site push can still push on such a night (for example, the `CNAME` file added after S6). The wrapper takes the site-push result as an input and runs the live check whenever the site pushed, even if the data publish did not push. If neither the data publish nor the site push pushed, the live check is still skipped, as today.

If the site push fails after a successful data push, the report begins with `ACTION: site publish failed` (or `ACTION: site publish blocked (...)` if a site gate failed). The live check still runs, so a stale live tree is visible. Do not skip the live check only because the site push failed.

Duties from the live `publicfunds-refresh` skill and the nightly routine, and how each is kept:

| Duty | Exit-code and ACTION rules today | After this change |
|---|---|---|
| Two kinds of run | The nightly does steps 0 to 6; step 4 is its only publish. A run on request does steps 0 to 3, then 5 and 6, and does not publish unless the owner asks (same step-1 = 0 rule). | Unchanged. The site push is part of step 4 on a nightly (or on a requested publish). |
| Quiet report | On the nightly, the routine sends nothing when all is well. | Unchanged. A bare evidence-guard pass, data and site pushes exit 0, and a live check exit 0 still add no ACTION line. |
| Incidents | Written only on local branch `incidents/local` in its own worktree, not on `main`, and not sent to GitHub. The main checkout stays on `main`. If the incidents commands fail, the text goes in the report; no force, stash, reset or delete. | Unchanged. A failed site push that needs an incident uses the same branch. |
| Step 0 wait | `pgrep -f '[t]husa run'`. If still running after 120 minutes: `ACTION: nightly skipped (another run still in progress after 2h)`, record an incident, skip steps 1 to 6. | Unchanged. |
| Step 0 account and origin guard | `GH_TOKEN` from `gh auth token --user GrokForum`; origin must match GrokForum/publicfunds-sa. Non-zero: `ACTION: account or origin check failed`, skip steps 1 to 6, no pull, publish or push. The guard is run again before any later pull or push. | Unchanged for the data repository. A second guard (section 4.2) covers the site-repository URL before the site push. |
| Step 0 checkout update | Must be on `main`, clean tracked files, `git fetch` and `git merge --ff-only origin/main`. Non-zero: `ACTION: checkout update failed` (its only ACTION line), skip steps 1 to 6, no push, reset or clean. "Already up to date" is a pass, including when local `main` is ahead with an unpushed data commit. Never `reset --hard`. | Unchanged. |
| Step 1 `thusa run` | **0**: the build is releasable. **2**: data-quality failed; do not publish; follow RB-01; record an incident. | Unchanged. Step 4, including the site push, still runs only if step 1 returned 0. |
| Step 2 sources | Report each source's status. For any source that is not `ok`: if a known error already matches it (`itil/knowledge/known-errors.md`), name that known error; otherwise record an incident on `incidents/local`. Never bypass a block (403, login, WAF). | Unchanged. A source that is not `ok` is still named as a known error when one matches, or recorded as an incident when it is new. |
| Step 3 coverage and flags | Report the coverage headline, flag counts, and new or "evidence changed" flags. | Unchanged. |
| Step 4 only if step 1 is 0 | If step 1 is not 0, or this is a run on request without an owner publish ask: skip step 4, add no publish ACTION line, report the step 1 result. | Unchanged. No site push in those cases either. |
| Step 4 "on main" | If HEAD is not `main`: `ACTION: publish blocked (not on main)`; no publish. | Unchanged. No data push and no site push. |
| Step 4 guard again | Non-zero: `ACTION: account or origin check failed`; no publish. | Unchanged, then the site-remote guard before the site push. |
| Step 4 POPIA candidate check | PASS: go on. BLOCK: `ACTION: publish blocked (POPIA)`, no publish. Candidate export exit 3: skip the check and go on to the publish command (it will refuse the same way). Any other non-zero: treat as BLOCK. A blocked publish has that one ACTION line only. | Unchanged, and a second POPIA check runs on the staging tree before the site push (section 4.2). |
| Step 4 data publish | `scripts/publish-public-data.sh --push`. Exit **0**: committed and pushed, or nothing to push (no change, or timestamps only). Exit **3**: export refused; nothing committed or pushed; `ACTION: publish refused`; wrapper `check_live: SKIPPED` exit 3. Exit **4**: nothing pushed; `ACTION: publish failed`; incident; wrapper skipped, exit 3; stop after the wrapper; do not retry. Any other non-zero: `ACTION: publish failed`; wrapper `check_live: FAILED CHECK` exit 2; incident; stop and report; check by hand if data went live; do not retry. | Unchanged for the data push. The site push runs only after a data-publish exit 0 (including "nothing to commit" or timestamps only, which still leave a current tree to assemble). After exit 3 or 4, there is no site push. After any other non-zero data-publish exit, there is no site push (the wrapper already cannot tell if data went live). |
| Evidence guard | Only a bare `evidence_guard: pass` is quiet. Any other line or a missing line is not a pass; `ACTION: publish needs attention` follows the publish ACTION line, or leads the report when the data publish exited 0. Never describe `UNKNOWN` or a missing line as a pass. | Unchanged for the data publish. |
| Live check wrapper | Today it runs immediately after the data publish, whatever that exit code. Exit **0**: OK, or WARN only; report [WARN] and carry on. Exit **1**: [BREACH]; report it as a breach, not a success; the wrapper still runs the review-app health check where the skill says. Exit **2**: failed check, crash, time limit, or it cannot tell if the publish pushed; stop and report. Exit **3**: skipped, because the log or exit code shows the publish did not push, including `nothing to commit` and `only timestamps changed`. `check_live` warns at 30 h of data age and breaches at 48 h. `RAW_URL` is the data repository raw manifest. | After S11 the wrapper takes the site-push result as an input, as well as the data-publish result. It runs the live check whenever the site pushed, including on a night when the data publish had nothing to commit or only timestamps changed (for example, a `CNAME` add after S6). If the site push failed, the live check still runs. If neither push pushed, the live check is skipped (exit 3), as today. `RAW_URL` points at the site repository. The other exit codes and ACTION rules stay. After cutover, a skipped or failed site push can make the live tree stale; exit 1 or a [WARN] reports that. |
| State backup (CHG-2026-044) | Only if step 1 returned 0 and the data publish exited 0, after the live check, also when the wrapper said stop. Exit 0: put the `backup: ok` line in the report; no ACTION line. Any other exit: `ACTION: backup failed` after any publish ACTION line, and quote the `backup: FAILED` line. Do not retry or delete a backup. The routine also sends that failed line only, no data, to the orchestrator. Backups stay on this computer; never commit, push or publish them. | Unchanged. The backup still follows the live check. A failed site push after a data-publish exit 0 does not skip the backup. The `backup: FAILED` alert to the orchestrator is still sent. |
| Step 5 review-app health | Check `curl -s http://127.0.0.1:8765/healthz`. If it is not ok, run `scripts/review-app.sh restart`. A broken audit chain is a security incident: stop and tell the owner. The wrapper may already run part of the health check after a live-check breach. | Unchanged. The restart and the stop on a broken audit chain stay. |
| Step 6 | Never confirm or reject flags here. Never push anything except the step 4 publish, and never merge PRs. | Unchanged, except that step 4 may also push the allowlist tree to the site repository, under Q2 and the site-remote guard. Still never merge PRs. |
| Routine report order | ACTION lines first, in the skill's order; then step 0 and step 1; sources; coverage and flags; publish exit and evidence guard; live-check RESULT / check_live / healthz / NEXT and [BREACH] or [WARN]; backup line; review-app health. A BREACH, a failed check, or a refused, blocked, failed or skipped publish is reported as that, never as success. | Unchanged, with any site-publish ACTION line placed after the data-publish ACTION lines and before the live-check lines. |

## 5. Hostname cutover

The owner keeps control of DNS. This record does not change DNS. Measured by the author on 18 Nov 2026 08:27 SAST, with DNS-over-HTTPS at Cloudflare and at Google (`dig` was not installed on this computer): `publicfunds.grokforum.site` is a CNAME to `grokforum.github.io.` (TTL 3,600 seconds). So S7 is a confirmation, not a change: DNS already points at `grokforum.github.io`.

The live site sends HSTS. Measured with `curl -sI https://publicfunds.grokforum.site/` at 18 Nov 2026 08:27 SAST: `strict-transport-security: max-age=31556952`, HTTP 200. After the custom domain is moved from the data repository to the new repository, browsers that already have this HSTS policy will use only HTTPS. Until GitHub issues a certificate for the domain on the new repository, that is a hard HTTPS outage. The same applies to a rollback. GitHub's guide "Troubleshooting custom domains and GitHub Pages" (https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages, read 18 Nov 2026) says it can take up to an hour for the site to become available over HTTPS after the custom domain is configured. That "up to 1 hour" figure is **[unverified]** (it comes from those docs, not from a measured cutover).

Before S5, the custom domain `publicfunds.grokforum.site` must already be verified for the GrokForum account (GitHub Pages domain verification). Do not start S5 until that verification is in place.

Steps, in an execution window, after the plan GO and a separate execution GO:

| # | Step | Stop if |
|---|---|---|
| S0 | The owner gives the execution GO. The author records the time. | No GO. |
| S1 | The owner or the orchestrator, with the account that can create GrokForum repositories, creates the public repository under GrokForum with the name chosen at Q1. It starts with fresh history. No commits are copied from GrokForum/publicfunds-sa. | The repository cannot be created, or it already holds other history. |
| S2 | Enable GitHub Pages on that repository, from `main`, path `/`. | Pages cannot be enabled. |
| S3 | First publish of the allowlist tree, after PR #18 and the first masked nightly, with all gates in section 4, **without a `CNAME` file**. Wait until the Pages build status is `built`. | Any gate fails, or the build fails. Then nothing is moved; the live hostname is unchanged. |
| S4 | Verify on the `github.io` URL (`https://grokforum.github.io/<name>/`). A project site is served under a `/<name>/` prefix, so links that start at the domain root (for example `/privacy/` and `/apps/public-dashboard/`) may not resolve there. Verify the served files, `robots.txt`, the DRAFT label, the privacy page, the masked award files (0 hits for the private list) and sample manifest bytes, by URLs that match how GitHub serves a project site, or by fetching the published files. This step is not the `check_live` of the custom domain. Confirm there is no `CNAME` file in this first tree. | The files are wrong, or the mask scan fails, or a file not on the allowlist is present. Then do not move the custom domain. |
| S5 | Confirm that `publicfunds.grokforum.site` is verified for the GrokForum account. Then remove that custom domain from Pages on GrokForum/publicfunds-sa. The hard HTTPS outage starts here. | The domain is not verified for the account. Do not remove it from the data repository. |
| S6 | Add that custom domain to Pages on the new repository immediately. Do not wait for a `CNAME` file to be in the tree; that file joins the allowlist from the next publish after this step. PR #18's contact test reads `SITE_DOMAIN` from the repository `CNAME` file, so that test is updated or pointed at the site repository's `CNAME` when the domain moves (S11). | The domain cannot be added. Then roll back (section 6). |
| S7 | Confirm that DNS for `publicfunds.grokforum.site` is still a CNAME to `grokforum.github.io`. No DNS change is required. | The CNAME does not point at `grokforum.github.io`. Then stop and fix DNS before waiting for the certificate, or roll back. |
| S8 | Wait for the HTTPS certificate on the new repository (up to 1 hour **[unverified]**, see above), and confirm that HTTPS is enforced. | The certificate does not appear in that window. Then roll back. |
| S9 | Run `scripts/check_live.py` against `https://publicfunds.grokforum.site` (the default site URL; the bytes now come from the new repository). Confirm `/robots.txt`, `/privacy/` and the DRAFT label. Confirm the Pages custom-domain setting. `/CNAME` may be absent until the next publish after S6. | `check_live` is not OK. Then roll back. |
| S10 | Turn off Pages on GrokForum/publicfunds-sa, or leave it without a custom domain, so the advertised hostname is only the new repository. The data repository stays public until the later change. | — |
| S11 | Change the refresh skill, the routine prompt, `scripts/nightly_check_live.py` (`RAW_URL` to the site repository; the wrapper takes the site-push result as an input and runs the live check whenever the site pushed) and, if needed, a small publish helper so that step 4 is: data push, then site push, then the live check, with the gates in section 4 and the duties in section 4.5. PR #18's contact test (`tests/test_site_draft_privacy.py`) reads `SITE_DOMAIN` from the repository `CNAME` file, so that test is updated or pointed at the site repository's `CNAME` when the domain moves. Deploy the skill, the routine and that test change together, as in CHG-2026-065 and CHG-2026-066. The data-repository origin guard stays. A second guard covers the site-repository URL. From this publish on, `CNAME` is on the allowlist. | The deploy fails. Then keep the previous skill pair and the previous contact test, and keep serving the already published tree. |

The git publish itself is short. The certificate wait may be up to 1 hour **[unverified]**. Plan a daytime window, not within 2 hours of 03:00 SAST, and only after the first masked nightly (Q6). Do not start S5 until the full certificate window can be watched.

## 6. How to revert

- **Before the custom domain is moved (after S3 or S4 only):** stop publishing to the site repository. Leave the custom domain on GrokForum/publicfunds-sa. The live hostname is unchanged. There is no HSTS outage.
- **After the custom domain is moved:** remove the custom domain from Pages on the new repository. Add it back to Pages on GrokForum/publicfunds-sa immediately. DNS does not need to change. Wait for a new HTTPS certificate (up to 1 hour **[unverified]**). That wait is again a hard HTTPS outage, because of HSTS. Run `check_live` against `https://publicfunds.grokforum.site/`. The data repository still holds the site files at its tip, so Pages there can serve the site again, **only while that repository stays public**. Once it goes private (section 8), this rollback path ends.
- **Skill and routine:** `git revert` of the later implementation commit, then redeploy the previous skill and prompt pair, including the previous `RAW_URL`.
- The new repository can stay unused, or be archived, as the owner chooses. A rollback does not delete it unless the owner asks.

## 7. Privacy mailbox

The role mailbox is a test mailbox for the PublicFunds pilot only. The production mail domain is left until the four sites are planned as one. The other three watcher sites get no privacy mailbox until that planning.

The hosting operator created the mailbox on `grokforum.site` as `privacy@grokforum.site`, not on the `publicfunds` subdomain, and a test mail was delivered, as relayed by the orchestrator. The owner confirms this address at the GO (Q4). This RFC does not create or change mail.

## 8. Later change: the data repository goes private

Only the website gets advertised. The plan, as relayed with the 08:11 SAST decision, is that GrokForum/publicfunds-sa goes private when the merged site goes live with its own public repository. That is a later change. This RFC does not change the visibility of the data repository, and it does not merge other watcher sites.

## 9. Effect on CHG-2026-068

CHG-2026-068 (PR #19) plans a history rewrite of GrokForum/publicfunds-sa so that the 5 titled supplier values are in no branch or tag. After that rewrite, `refs/pull/*` stay advertised, so any `git clone --mirror` or fetch of those refs still downloads the old commits with the values, without a SHA (CHG-2026-068 Q7, open).

This site-repository change does not rewrite or hide that history by itself. The values stay in the data repository until a rewrite runs, or until that repository is no longer public.

Q5 of this record and CHG-2026-068 Q10 are **one owner question**. It is asked once and recorded in both records.

Options (the owner chooses; this record does not decide):

| Option | Order | Effect on the public | Effect on CHG-2026-068 and Q7 |
|---|---|---|---|
| a | Do this site-repository change first, move the hostname, then make the data repository private as a later change. Defer or drop the history rewrite. | Once the data repository is private, the advertised website has fresh history and no `refs/pull` residue, and the public cannot clone the data repository or fetch its `refs/pull/*`. | The public leftover in Q7 becomes moot. A private repository still keeps the values in its history and in its `refs/pull/*` for anyone with access. Q7 would be reframed as: does the owner accept that residual for anyone with access, or still want a rewrite? |
| b | Do this site-repository change first (and later make the data repository private), and still run the CHG-2026-068 rewrite, before or after the repository is private. | The public site is as in (a). Branches and tags of the data repository no longer hold the values, for anyone with access. `refs/pull/*` may still hold them for anyone with access (no GitHub Support purge). | The rewrite still runs. Q7 is about the residual for anyone with access, not about a public `ls-remote`. |
| c | Run the CHG-2026-068 rewrite first, as that RFC now plans, then this site-repository change, then the later private change. | Until the data repository is private, the public data repository has rewritten branches and tags, and the advertised `refs/pull/*` residual stays public until visibility changes. | CHG-2026-068 Q7 stays as it is until the data repository is private. |

Author's recommendation, not a decision: option a for the order (site repository first, hostname cutover, data repository private later), because that ends the public `refs/pull` exposure without a force-push of the data repository. Whether the rewrite still runs (a versus b) is left to the owner. Option c remains available if the owner wants the rewrite while the data repository is still public.

## 10. Risks

| # | Risk | Likelihood × impact | Mitigation |
|---|---|---|---|
| R1 | The allowlist is too wide, and source or records go to the public site repository. | 2 × 4 = 8 | Only the listed files in section 3 are copied. The allowlist test fails on any file it does not expect, including `README.md` and `GROK_BUILD_PROMPT.md` under `apps/public-dashboard/`. The first tree is reviewed before the first push. |
| R2 | The first publish runs before the masked nightly, and the site repository's history holds the values. | 2 × 5 = 10 | Section 4.2 item 7 and the dependency in the header: the first publish is only after PR #18 and the first masked nightly, and only if the mask scan on the staging tree passes. |
| R3 | After S5, HSTS makes the wait for a new certificate a hard HTTPS outage (up to 1 hour **[unverified]**). The same applies to rollback. | 5 × 4 = 20 | Domain verified for the GrokForum account before S5. S6 follows S5 immediately. Watch the window (Q6). Roll back if the certificate does not appear. Tell the owner the outage is expected and time-bounded. |
| R4 | The custom domain is not verified for the account, and S5 starts anyway. | 2 × 4 = 8 | S5 stops unless verification is in place. |
| R5 | The push token can write more than the site repository. | 2 × 4 = 8 | A token scoped to the site repository; the site-remote URL guard (section 4.2). |
| R6 | The `github.io` project-site prefix misleads the pre-cutover check. | 3 × 2 = 6 | S4 states the limit. The binding check is `check_live` on the custom domain at S9. |
| R7 | Pages on the data repository stays on after the cutover and serves a second copy, including source. | 2 × 3 = 6 | S10 turns Pages off on the data repository, or at least removes the custom domain. |
| R8 | The standing data-publish approval is taken as approval to push the site repository. | 2 × 3 = 6 | Q2. No site-repository push until that standing approval exists. |
| R9 | `nightly_check_live.py` keeps `RAW_URL` on the data repository, so after cutover (and after that repository goes private) the live check reads the wrong origin or cannot read it. | 5 × 3 = 15 | S11 moves `RAW_URL` to the site repository, and the live check runs after the site push. |
| R10 | Option a keeps every published tree in public git, and a later mask leaves old values reachable (the CHG-2026-068 problem). | 3 × 3 = 9 | Q3 states the trade-off. A private bundle of each tip is recommended with option a. Option b avoids public history, if the owner chooses it. |

## 11. Approval

1. Two independent reviewer PASSes on the exact head of this RFC.
2. The owner's GO naming that head. This approves the plan only. The GO also confirms the `privacy@grokforum.site` mailbox (Q4).
3. At execution time, a separate explicit owner GO for creating the repository, the first publish and the hostname cutover. The author does not create the repository, publish into it, or change DNS without that GO.
4. If the nightly is to push the site repository after the cutover, a new standing approval is required (Q2).
5. DNS already points at `grokforum.github.io`. This record does not change it. S7 only confirms it.

## 12. Questions for the owner

| # | Question | Author's recommendation |
|---|---|---|
| Q1 | What is the name of the new public GrokForum repository? | `publicfunds-site` (section 2). |
| Q2 | May the nightly push to the site repository after the cutover, under a new standing approval? Which token (or permission), scoped only to that repository, is used? | Yes, after the execution GO and a standing approval that names the site repository. Use a token that can write contents only on that repository, with the URL guard in section 4.2. |
| Q3 | One commit on `main` for each successful publish, or a single orphan commit that replaces `main` each time? | See the trade-off in section 4.4. Option a keeps every published tree in public git forever (the CHG-2026-068 problem if a later mask is needed). Option b needs a private rollback copy. Rollback through the data repository's Pages ends once that repository goes private. Recommendation: option a, plus a private bundle or tag of each tip. |
| Q4 | Where is the `privacy@` test mailbox for this pilot hosted? | Recorded. The hosting operator created `privacy@grokforum.site`, not on the `publicfunds` subdomain, and a test mail was delivered, as relayed by the orchestrator. The owner confirms this address at the GO. This change does not create or change mail. The mailbox stays a test mailbox for the PublicFunds pilot only. The production mail domain is left until the four sites are planned as one. |
| Q5 | In what order do this change, the later private change of the data repository, and the CHG-2026-068 history rewrite run? Does the rewrite still run? How should CHG-2026-068 Q7 be read after that? | This is the same question as CHG-2026-068 Q10. It is asked once and recorded in both. Option a in section 9 for the order. Whether the rewrite still runs (a versus b) is for the owner. This record does not decide. |
| Q6 | When is the cutover window? | The first daytime period after PR #18 is on `main` and the first masked nightly has passed, not within 2 hours of 03:00 SAST, and long enough to watch the certificate window (up to 1 hour **[unverified]**). |

## 13. Seen, not touched

- Making GrokForum/publicfunds-sa private (later change, section 8).
- Merged-site planning for the other watcher sites, and privacy mailboxes for those sites.
- The CHG-2026-068 history rewrite itself (PR #19).
- Real HTTP response headers, a CDN, and `www` HTTPS (CHG-2026-067 Q5 and F-18).
- The implementation of the allowlist, the site-remote guard, the `RAW_URL` change and the skill text (this record is the plan only).

## 14. Testing of this record

- Docs only. The full test suite ran on the branch (counts in the Revisions section).
- The added lines were checked for the 5 values (`grep -c -F -f` on the private list: 0 hits), for names, ids, e-mail addresses of private persons, private paths and stale words.

## Revisions

- Draft (18 Nov 2026): first version. Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 08:18 SAST). Added lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.
- Rev 3 (18 Nov 2026): Reviewers A and B (on `a4e6b336`, each PASS_WITH_CONCERNS). (1) The 08:11 SAST decision was given by the owner in the orchestrator's chat and relayed to the author; the reviewers did not hear it first-hand (header and section 1). (2) Q4 states that the production mail domain is left until the four sites are planned as one. (3) The section 4.5 duties table now includes: the `backup: FAILED` alert to the orchestrator; the review-app restart when healthz is not ok, and that a broken audit chain is a security incident (stop); and step 2's duty to name the matching known error. (4) `nightly_check_live.py` skips the live check on `nothing to commit` or `only timestamps changed`; after S11 the wrapper takes the site-push result as an input and runs the live check whenever the site pushed (for example, a `CNAME` add after S6). (5) S6 and S11 record that PR #18's contact test reads `SITE_DOMAIN` from the repository `CNAME` file, so that test is updated or pointed at the site repository's `CNAME` when the domain moves. Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 08:51 SAST). Added and changed lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses of private persons, 0 private paths, 0 ids.
- Rev 2 (18 Nov 2026): Reviewer A (on `3756dcd3`, PASS_WITH_CONCERNS). (1) The allowlist names each needed file; `apps/public-dashboard/` is not copied as a directory (`README.md` and `GROK_BUILD_PROMPT.md` are excluded). Root `index.html` loads the dashboard and `og-card.png`; after PR #18 the privacy page, `404.html` and `robots.txt` are required. The planned allowlist test fails on any file it does not expect. (2) S3 publishes without `CNAME`; S6 sets the domain; `CNAME` joins the allowlist from the next publish on. (3) DNS already points at `grokforum.github.io` (Cloudflare and Google DNS-over-HTTPS, 18 Nov 2026 08:27 SAST); S7 is a confirmation, not a change. The live site sends HSTS (`max-age=31556952`, `curl -sI` at 08:27 SAST), so the wait for a new certificate is a hard HTTPS outage, also on rollback; "up to 1 hour" **[unverified]** from GitHub Pages documentation. The custom domain must be verified for the GrokForum account before S5. (4) `nightly_check_live.py` hard-codes `RAW_URL` to the data repository; S11 moves it to the site repository. Step 4 is data push, then site push, then the live check. Section 4.5 lists every current refresh-skill and routine duty, with its exit-code rules, and how it is kept. (5) Q3 states the option-a public-history trade-off against option b's private rollback copy, and that Pages rollback through the data repository ends when that repository goes private. Q5 and CHG-2026-068 Q10 are one owner question, asked once and recorded in both. Q4: the hosting operator created `privacy@grokforum.site` and a test mail was delivered, as relayed by the orchestrator; the owner confirms it at the GO. Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 08:34 SAST). Added and changed lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses of private persons, 0 private paths, 0 ids.

## Post-implementation review

- Outcome: not started (draft).
