# Operator release notes (DRAFT)

Plain notes for the operator. Newest first. Each note has a date, what you will notice, what can break the routine, and what to do if it fails.

GitHub Releases cut from a `snapshot-YYYY-MM-DD-HHMM` tag are the backup copy of the same facts.

---

## How to read a note

- **Date (SAST):** when the change reached `main` or when the data build published.
- **What you will notice:** what changes on the live site or in the nightly report.
- **What can break the routine:** steps that may stop the nightly refresh or the live check.
- **If it fails:** the first action. Prefer the named runbook.

---

## Template (copy for each release)

### YYYY-MM-DD HH:MM SAST — short title

- **Tag / build:** `snapshot-…` or build id `B…`
- **What you will notice:** …
- **What can break the routine:** … (or "none")
- **If it fails:** … (runbook RBxx, or report and stop)

---

## Entries

### 2026-11-06 — site DNS restored; old public repo made private

- **Tag / build:** live data build `B20261106T010934Z` (nightly); no new code snapshot required for the DNS fix
- **What you will notice:** https://publicfunds.grokforum.site/ loads with a valid certificate. The changes page and dashboard answer.
- **What can break the routine:** if the CNAME for `publicfunds` leaves `grokforum.github.io`, the live check will BREACH and Pages will look down.
- **If it fails:** run `python3 scripts/check_live.py` (RB-12). Check DNS at dns.google for `publicfunds.grokforum.site`. Do not re-publish to "fix" DNS.

### 2026-11-01 — public repo under GrokForum; clean history

- **Tag / build:** rewrite root and follow-up merges on GrokForum/publicfunds-sa (see CHG-2026-050 / CHG-2026-051 records)
- **What you will notice:** public clone and Pages come from GrokForum/publicfunds-sa. Bootstrap defaults to that repo.
- **What can break the routine:** a skill or script that still points at the old public clone URL.
- **If it fails:** confirm `scripts/bootstrap.sh` default `PF_REPO_URL` and the live setup skill curl URL both name GrokForum/publicfunds-sa. Report and stop; do not force-push.

---

## Backup: GitHub Releases

When a merge to `main` gets a `snapshot-YYYY-MM-DD-HHMM` tag, cut a GitHub Release from that tag with the same four fields as the template above. The Release body is the backup if this file lags.
