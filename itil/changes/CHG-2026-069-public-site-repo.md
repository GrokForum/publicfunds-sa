# CHG-2026-069: Serve the PublicFunds public site from a separate GrokForum GitHub repository (DRAFT)

| Field | Value |
|---|---|
| Requested by / date (SAST) | Owner decision, 18 Nov 2026 08:11 SAST, given in another chat and relayed by the orchestrator to the author. This record is the plan. |
| Status | **DRAFT RFC.** Drafted on 18 Nov 2026 on branch `chg-2026-069-public-site-repo` from `main` `76688eca`. This record is not an execution GO. Nothing was published to a new repository, and the custom domain was not moved. |
| Type | **Normal-high** (`itil/change-enablement.md`: distribution, GitHub Pages, the publishing pipeline, secrets and auth). Two independent reviewer PASSes on the exact RFC head, then the owner's GO naming that head. Creating the repository, the first publish and the hostname cutover need a second, separate owner GO at execution time (section 11). |
| Environment | DEV: a local staging tree of the site files, held on the author's computer. TEST: GitHub Pages on the new repository at its `github.io` URL, before the custom domain is moved. PROD: `https://publicfunds.grokforum.site/` served from the new repository. The hostname cutover is PROD. |
| Depends on | PR #18 (CHG-2026-067 code) merged, and the first nightly publish after that merge masked the live data, before the first publish into the new repository. |
| CIs affected | A new public GitHub repository under GrokForum and its Pages settings; DNS and `CNAME` for `publicfunds.grokforum.site`; the nightly refresh skill and routine prompt; `scripts/check_live.py` (the default hostname stays the same after the cutover); Pages settings on GrokForum/publicfunds-sa; this record; `itil/registers/change-log.md`; `STATUS.md`. |
| Linked records | CHG-2026-067 (Q7: serve only the site files from Pages, as a separate change; DRAFT label, robots, privacy page, title masks, PR #18); CHG-2026-068 (history rewrite of the data repository, PR #19, RFC head `ace55d61` at the time this record was drafted); CHG-2026-007 (GitHub Pages); CHG-2026-061 (`check_live`); CHG-2026-063 (robots); CHG-2026-065 and CHG-2026-066 (skill master and nightly publish); CHG-2026-050 (fresh repository, Pages and DNS). |
| Rollback | Move the custom domain back to Pages on GrokForum/publicfunds-sa, restore DNS if it was changed, wait for HTTPS, and run `check_live` against `https://publicfunds.grokforum.site/`. See section 6. |

## 1. What and why

Owner decision, 18 Nov 2026 08:11 SAST, given in another chat and relayed by the orchestrator to the author: the PublicFunds public webpage is served from a separate public GitHub repository under GrokForum. Only the website gets advertised. The data repository goes private when the merged site goes live with its own public repository. That visibility change is a later change. This RFC does not make GrokForum/publicfunds-sa private.

This record is the separate follow-up named in CHG-2026-067 Q7. The owner's answer to that question (18 Nov 2026 05:40 SAST, as relayed by the orchestrator to the author) was to serve only the site files from GitHub Pages, in a separate change. This RFC replaces that follow-up.

Today, GitHub Pages on GrokForum/publicfunds-sa is a legacy build from `main`, path `/` (measured in CHG-2026-068). It serves the whole repository root, including review-app templates and records (CHG-2026-067, finding N-3). A new repository that holds only the built site files, with fresh history, removes that. It also avoids copying the data repository's history and its `refs/pull/*` residue into the host of the public site.

## 2. Proposed repository (Q1)

The author's recommendation is the name `publicfunds-site`, so the repository is GrokForum/publicfunds-site. The owner chooses the name (Q1).

Checked by the author on 18 Nov 2026 08:15 SAST, after confirming the origin of the data worktree was `https://github.com/GrokForum/publicfunds-sa.git`, with read-only `gh api` and the GrokForum token: among GrokForum repositories whose names contain `publicfunds`, only `publicfunds-sa` was listed. A read of `repos/GrokForum/publicfunds-site` returned HTTP 404. Whether a private repository with that name exists is **[unverified]**.

The new repository is public. It carries only the built site files listed in section 3. It has fresh history: no commits are copied from GrokForum/publicfunds-sa, and it has no `refs/pull/*` residue from that repository.

## 3. What is published into it

There is no `dist/public/` output in the tree today. `config/publication.yaml` uses that path as the name of a public snapshot. GitHub Pages today serves the repository root. The published tree is an assembled allowlist from the data-repository checkout, after a successful export.

Allowlist, from the tree on `main` `76688eca` and from the CHG-2026-067 code in PR #18:

- `index.html`
- `apps/public-dashboard/` (the dashboard page and any assets it needs)
- `public-data/v1/` (the dashboard data; the dashboard reads it from a same-origin relative path)
- `robots.txt` (`Disallow: /`)
- `CNAME` (`publicfunds.grokforum.site`), after the cutover
- `.nojekyll`
- After PR #18 is on `main`: `privacy/index.html`, `404.html`, and the DRAFT label and `noindex, nofollow` meta tag on every site page

No other path is copied. In particular, `scripts/`, `tests/`, `thusa/`, `itil/`, records, source, lock files and review-app templates are not copied.

The exact allowlist is fixed in the later implementation and is covered by a test. GitHub Pages on the new repository uses the DRAFT label, `robots.txt` with `Disallow: /` plus `noindex`, the privacy page, and the mask scan on the tree that is published into it.

## 4. How the nightly publishes into it

This design is grounded in `scripts/publish-public-data.sh` and `docs/bot/live-skill/publicfunds-refresh.MASTER.md`, which were read and were not run.

Today the nightly, at step 4, and only if step 1 returned 0, runs a POPIA candidate check and then `scripts/publish-public-data.sh --push`. That script runs `uv run pf publish-data`, refuses on a data-quality, safety or evidence-guard failure (exit 3), commits only `public-data/`, and pushes only from `main` as a fast-forward to `origin/main` of GrokForum/publicfunds-sa. The standing pre-approval in `changes/CAB-DECISION.md` covers that data push only. The account and origin guard (CHG-2026-066) takes `GH_TOKEN` from `gh auth token --user GrokForum` and requires that origin to match `github.com/GrokForum/publicfunds-sa`. After PR #18, `pf publish-data` also runs the fail-closed titled-supplier scan and writes the masks and `doc` `null`. The live check then runs `scripts/nightly_check_live.py` and `scripts/check_live.py` against `https://publicfunds.grokforum.site`.

The implementation of the site-repository publish is a later code change, after this plan is approved. The plan is as follows.

### 4.1 Build output

After a successful export, assemble a staging tree from the allowlist in section 3, using the exported `public-data/v1` and the site pages from `main`. That staging tree is the only input to the push to the site repository. There is no separate front-end build step today.

### 4.2 Gates before the push

All of these must pass. Stop on any failure. Nothing is pushed to the site repository if a gate fails.

1. The existing nightly pre-checks still pass: step 1 returned 0; the checkout is on `main`; the account and origin guard for the data repository passed; the POPIA candidate check passed; `pf publish-data` exited 0, including the evidence guard and, after PR #18, the titled-supplier scan.
2. A second mask scan on every file in the staging tree: 0 hits for the private titled-supplier list (exact and case-insensitive), and the same fail-closed titled-person rule as the export. A masked row in the tree must have `doc` `null`.
3. A POPIA release check on the staging tree (the popia-review release check), not only on `public-data/`.
4. A site-remote guard: the push URL is exactly `github.com/GrokForum/<name chosen at Q1>`. The token used for this push writes to that repository and is not used, in the same command, to push the data repository.
5. The first publish runs only after PR #18 is on `main` and the first masked nightly has passed, so the new repository's history never holds the unmasked values.

### 4.3 Push identity and token scope

Pushes to the site repository go out as the GrokForum account, as with the data-repository publish. The author's recommendation is a token (or a fine-grained permission) that can write contents only on the site repository, stored privately, not in git. The standing approval for `public-data/` on GrokForum/publicfunds-sa does not cover this push. A new standing approval is needed before the nightly may push to the site repository (Q2).

### 4.4 History of the site repository (Q3)

| Option | Action | Effect |
|---|---|---|
| a | One new commit on `main` for each successful publish (author's recommendation). | The history is a record of what went live. The first commit is the first masked tree, so the site repository never holds the unmasked values. A bad publish can be replaced by publishing the previous tree again. |
| b | Each publish is a single orphan commit that replaces `main`. | The site repository then holds only the latest tree. Older published trees are not in git. Rollback of a bad publish needs a private copy or tag of the previous tip. |

The author's recommendation is option a, and to record the SHA (or a snapshot tag) of each published tip.

The data-repository publish of `public-data/` to GrokForum/publicfunds-sa can continue until the later change that makes that repository private. After the hostname cutover, Pages on the data repository is turned off, or is left without the custom domain, so that repository does not serve a second public copy of the site.

## 5. Hostname cutover

The owner makes the DNS and `CNAME` change himself. This record does not change DNS.

Steps, in an execution window, after the plan GO and a separate execution GO:

| # | Step | Stop if |
|---|---|---|
| S0 | The owner gives the execution GO. The author records the time. | No GO. |
| S1 | The owner or the orchestrator, with the account that can create GrokForum repositories, creates the public repository under GrokForum with the name chosen at Q1. It starts with fresh history. No commits are copied from GrokForum/publicfunds-sa. | The repository cannot be created, or it already holds other history. |
| S2 | Enable GitHub Pages on that repository, from `main`, path `/`. | Pages cannot be enabled. |
| S3 | First publish of the allowlist tree, after PR #18 and the first masked nightly, with all gates in section 4. Wait until the Pages build status is `built`. | Any gate fails, or the build fails. Then nothing is moved; the live hostname is unchanged. |
| S4 | Verify on the `github.io` URL (`https://grokforum.github.io/<name>/`). A project site is served under a `/<name>/` prefix, so links that start at the domain root (for example `/privacy/` and `/apps/public-dashboard/`) may not resolve there. Verify the served files, `robots.txt`, the DRAFT label, the privacy page, the masked award files (0 hits for the private list) and sample manifest bytes, by URLs that match how GitHub serves a project site, or by fetching the published files. This step is not the `check_live` of the custom domain. | The files are wrong, or the mask scan fails. Then do not move the custom domain. |
| S5 | Remove the custom domain `publicfunds.grokforum.site` from Pages on GrokForum/publicfunds-sa. | — |
| S6 | Add that custom domain to Pages on the new repository. The `CNAME` file is already in the published tree. | The domain cannot be added. Then roll back (section 6). |
| S7 | The owner makes the DNS change if it is needed, so that the `CNAME` for `publicfunds.grokforum.site` points at the GitHub Pages host for the new repository (typically `<account>.github.io`). | The owner stops; roll back if the hostname is down. |
| S8 | Wait for the HTTPS certificate on the new repository, and confirm that HTTPS is enforced. | The certificate does not appear in a reasonable time. Then roll back. |
| S9 | Run `scripts/check_live.py` against `https://publicfunds.grokforum.site` (the default site URL; the bytes now come from the new repository). Confirm `/robots.txt`, `/CNAME`, `/privacy/` and the DRAFT label. | `check_live` is not OK. Then roll back. |
| S10 | Turn off Pages on GrokForum/publicfunds-sa, or leave it without a custom domain, so the advertised hostname is only the new repository. The data repository stays public until the later change. | — |
| S11 | Change the refresh skill, the routine prompt and, if needed, a small publish helper so that each successful nightly export also publishes the allowlist tree to the site repository, after the gates in section 4, and so that `check_live` still uses the custom domain. Deploy the skill and the routine together, as in CHG-2026-065 and CHG-2026-066. The data-repository origin guard stays. A second guard covers the site-repository URL. | The deploy fails. Then keep the previous skill pair, and keep serving the already published tree. |

The git publish itself is short. DNS and the certificate may take longer. Plan a daytime window, not within 2 hours of 03:00 SAST, and only after the first masked nightly (Q6).

## 6. How to revert

- **Before the custom domain is moved (after S3 or S4 only):** stop publishing to the site repository. Leave the custom domain on GrokForum/publicfunds-sa. The live hostname is unchanged.
- **After the custom domain is moved:** remove the custom domain from Pages on the new repository. Add it back to Pages on GrokForum/publicfunds-sa. The owner restores DNS if it was changed. Wait for HTTPS. Run `check_live` against `https://publicfunds.grokforum.site/`. The data repository still holds the site files at its tip, so Pages there can serve the site again.
- **Skill and routine:** `git revert` of the later implementation commit, then redeploy the previous skill and prompt pair.
- The new repository can stay unused, or be archived, as the owner chooses. A rollback does not delete it unless the owner asks.

## 7. Privacy mailbox

The role mailbox `privacy@` on the site's domain is a test mailbox for the PublicFunds pilot only. The other three watcher sites get no privacy mailbox until the merged-site planning.

Work on PR #18 found that the site domain is not an e-mail domain on the hosting account. How that is resolved is owner-decided (Q4). This RFC does not create or change mail.

## 8. Later change: the data repository goes private

Only the website gets advertised. The plan, as relayed with the 08:11 SAST decision, is that GrokForum/publicfunds-sa goes private when the merged site goes live with its own public repository. That is a later change. This RFC does not change the visibility of the data repository, and it does not merge other watcher sites.

## 9. Effect on CHG-2026-068

CHG-2026-068 (PR #19, RFC head `ace55d611a720e88f23525082b1001fc6ffa51d0` at the time this record was drafted) plans a history rewrite of GrokForum/publicfunds-sa so that the 5 titled supplier values are in no branch or tag. After that rewrite, `refs/pull/*` stay advertised, so any `git clone --mirror` or fetch of those refs still downloads the old commits with the values, without a SHA (CHG-2026-068 Q7, open).

This site-repository change does not rewrite or hide that history by itself. The values stay in the data repository until a rewrite runs, or until that repository is no longer public.

Options (Q5; the owner chooses; this record does not decide):

| Option | Order | Effect on the public | Effect on CHG-2026-068 and Q7 |
|---|---|---|---|
| a | Do this site-repository change first, move the hostname, then make the data repository private as a later change. Defer or drop the history rewrite. | Once the data repository is private, the advertised website has fresh history and no `refs/pull` residue, and the public cannot clone the data repository or fetch its `refs/pull/*`. | The public leftover in Q7 becomes moot. A private repository still keeps the values in its history and in its `refs/pull/*` for anyone with access. Q7 would be reframed as: does the owner accept that residual for anyone with access, or still want a rewrite? |
| b | Do this site-repository change first (and later make the data repository private), and still run the CHG-2026-068 rewrite, before or after the repository is private. | The public site is as in (a). Branches and tags of the data repository no longer hold the values, for anyone with access. `refs/pull/*` may still hold them for anyone with access (no GitHub Support purge). | The rewrite still runs. Q7 is about the residual for anyone with access, not about a public `ls-remote`. |
| c | Run the CHG-2026-068 rewrite first, as that RFC now plans, then this site-repository change, then the later private change. | Until the data repository is private, the public data repository has rewritten branches and tags, and the advertised `refs/pull/*` residual stays public until visibility changes. | CHG-2026-068 Q7 stays as it is until the data repository is private. |

Author's recommendation, not a decision: option a for the order (site repository first, hostname cutover, data repository private later), because that ends the public `refs/pull` exposure without a force-push of the data repository. Whether the rewrite still runs (a versus b) is left to the owner. Option c remains available if the owner wants the rewrite while the data repository is still public.

## 10. Risks

| # | Risk | Likelihood × impact | Mitigation |
|---|---|---|---|
| R1 | The allowlist is too wide, and source or records go to the public site repository. | 2 × 4 = 8 | The allowlist is named in section 3 and is covered by a test in the implementation. The first tree is reviewed before the first push. |
| R2 | The first publish runs before the masked nightly, and the site repository's history holds the values. | 2 × 5 = 10 | Section 4.2 item 5 and the dependency in the header: the first publish is only after PR #18 and the first masked nightly, and only if the mask scan on the staging tree passes. |
| R3 | DNS or the certificate is slow, and the custom domain is down. | 3 × 3 = 9 | Daytime window. Rollback by moving the domain back to the data repository (section 6). |
| R4 | After S5 and before S6 or S8, the custom domain has no Pages host. | 3 × 3 = 9 | Add the domain to the new repository immediately after removing it from the old one. Roll back if HTTPS fails. |
| R5 | The push token can write more than the site repository. | 2 × 4 = 8 | A token scoped to the site repository; the site-remote URL guard (section 4.2). |
| R6 | The `github.io` project-site prefix misleads the pre-cutover check. | 3 × 2 = 6 | S4 states the limit. The binding check is `check_live` on the custom domain at S9. |
| R7 | Pages on the data repository stays on after the cutover and serves a second copy, including source. | 2 × 3 = 6 | S10 turns Pages off on the data repository, or at least removes the custom domain. |
| R8 | The standing data-publish approval is taken as approval to push the site repository. | 2 × 3 = 6 | Q2. No site-repository push until that standing approval exists. |

## 11. Approval

1. Two independent reviewer PASSes on the exact head of this RFC.
2. The owner's GO naming that head. This approves the plan only.
3. At execution time, a separate explicit owner GO for creating the repository, the first publish and the hostname cutover. The author does not create the repository, publish into it, or change DNS without that GO.
4. If the nightly is to push the site repository after the cutover, a new standing approval is required (Q2).
5. The DNS change is made by the owner.

## 12. Questions for the owner

| # | Question | Author's recommendation |
|---|---|---|
| Q1 | What is the name of the new public GrokForum repository? | `publicfunds-site` (section 2). |
| Q2 | May the nightly push to the site repository after the cutover, under a new standing approval? Which token (or permission), scoped only to that repository, is used? | Yes, after the execution GO and a standing approval that names the site repository. Use a token that can write contents only on that repository, with the URL guard in section 4.2. |
| Q3 | One commit on `main` for each successful publish, or a single orphan commit that replaces `main` each time? | Option a in section 4.4: one commit per publish, and record the SHA or a tag of each tip. |
| Q4 | The site domain is not an e-mail domain on the hosting account (found in the work on PR #18). How is the `privacy@` test mailbox for this pilot hosted? | The owner decides. This change does not create or change mail. The mailbox stays a test mailbox for the PublicFunds pilot only. |
| Q5 | In what order do this change, the later private change of the data repository, and the CHG-2026-068 history rewrite run? Does the rewrite still run? How should CHG-2026-068 Q7 be read after that? | Option a in section 9 for the order. Whether the rewrite still runs (a versus b) is for the owner. This record does not decide. |
| Q6 | When is the cutover window? | The first daytime period after PR #18 is on `main` and the first masked nightly has passed, not within 2 hours of 03:00 SAST. |

## 13. Seen, not touched

- Making GrokForum/publicfunds-sa private (later change, section 8).
- Merged-site planning for the other watcher sites, and privacy mailboxes for those sites.
- The CHG-2026-068 history rewrite itself (PR #19).
- Real HTTP response headers, a CDN, and `www` HTTPS (CHG-2026-067 Q5 and F-18).
- The implementation of the allowlist, the site-remote guard and the skill text (this record is the plan only).

## 14. Testing of this record

- Docs only. The full test suite ran on the branch (counts in the Revisions section).
- The added lines were checked for the 5 values (`grep -c -F -f` on the private list: 0 hits), for names, ids, e-mail addresses, private paths and stale words.

## Revisions

- Draft (18 Nov 2026): first version. Full test suite on the branch: 961 passed, 61 skipped (18 Nov 2026 08:18 SAST). Added lines: 0 hits for the private list (exact and case-insensitive), 0 name words, 0 e-mail addresses, 0 private paths, 0 ids.

## Post-implementation review

- Outcome: not started (draft).
