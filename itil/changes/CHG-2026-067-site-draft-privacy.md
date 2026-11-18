# CHG-2026-067: DRAFT label, privacy and contact notice, medium audit findings and supplier title masks on the public site

| Field | Value |
|---|---|
| Requested by / date (SAST) | The owner set the scope on 18 Nov 2026 at 05:12 SAST, as reported to the author (PublicFunds) by the orchestrator. The scope comes from a read-only QC audit of the live site (18 Nov 2026, 04:51 to 05:10 SAST; 0 critical, 2 high, 7 medium, 8 low findings). This record is a draft RFC. It is not a merge GO and not a deploy GO. |
| Status | RFC drafted on 18 Nov 2026 (05:30 SAST) on branch `chg-2026-067-site-draft-privacy` from `main` `d688b031` (the nightly data refresh of 18 Nov 2026, build `B20261118T012055Z`). The record holds no code change. The owner's answers to Q1 to Q7 are recorded in section 12 (Owner answers, 18 Nov 2026 05:40 SAST, as relayed by the orchestrator to the author). The RFC was squash-merged into `main` as `76688eca` (PR #17, 18 Nov 2026 07:04 SAST, after the owner's GO as reported by the orchestrator to the author; rollback tag `snapshot-2026-11-18-pre-pf-pr17` on `d688b031`; post-merge tag `snapshot-2026-11-18-0704`; check_live RESULT: OK at 07:05 SAST). The author implemented the RFC on 18 Nov 2026 on branch `chg-2026-067-impl` from `main` `76688eca` (section 14). The code merge and the deploy need two reviewer PASSes on the exact head of that branch and the owner's GO naming that head. |
| Type | **Normal-high** (`itil/change-enablement.md`: publishing pipeline and distribution). Item 4 changes `thusa/publish_data.py`, which the nightly publish runs. A merge needs two independent reviewer PASSes on the exact head and then the owner's GO naming that head. The nightly data-refresh exemption does not cover this change. |
| Environment | DEV: a local worktree of the branch. TEST: a local static server of the exact head on 127.0.0.1 with headless Chrome. PROD: GitHub Pages from `main` (https://publicfunds.grokforum.site/). |
| CIs affected | CI-105 (`apps/public-dashboard/index.html`); root `index.html`; new `404.html` and `privacy/index.html` (new CIs at the build); CI-104 (`thusa/publish_data.py`, `public-data/v1/` at the next nightly publish); `thusa/detectors.py`; `thusa/report.py`; `config/public-data.yaml`; tests; this record; `itil/registers/change-log.md`; `STATUS.md`. |
| Linked records | QC audit of 18 Nov 2026 (findings F-01 to F-18); CHG-2026-012 (repo references removed from served files; issue link removed); CHG-2026-040 and CHG-2026-041 (evidence guard); CHG-2026-061, CHG-2026-065, CHG-2026-066 (nightly publish and live check); CHG-2026-063 (robots); CI-117; KE-001; SLO-PD-1 |
| Rollback | Pre-merge tag `snapshot-YYYY-MM-DD-pre-pf-prNN` on the `main` commit before the merge (NN is the PR number of this change). Then `git revert -m 1 <merge sha>`. See section 9. |

## 1. What and why

The audit found that the public site has no DRAFT label and no privacy notice or contact for data subjects (2 high findings). It also found broken or weak official-source links, freshness pills that say "stale" for sources that the nightly run checked, an unexplained pair of municipality counts, missing security headers and a data parameter that accepts any HTTPS origin (7 medium findings). The published award files hold supplier names as eTenders publishes them, and some of these names carry a personal title.

This change does the owner's scope in one PR:

1. A visible DRAFT label on every site page.
2. A privacy and contact notice page, linked from every page.
3. Fixes for the medium findings F-03 to F-09.
4. A mask for supplier values that carry a personal title, in the export, so that each nightly publish keeps it.

It also fixes three small source-claim problems that the author found during the claim check (section 7): F-10 and two footer claims.

## 2. Evidence (audit, rechecked by the author on 18 Nov 2026)

The author rechecked each medium finding from the box between 05:15 and 05:28 SAST. The box has the same network limit as the audit host: plain HTTP on port 80 goes to a local proxy (`198.18.0.1`, `Server: Pingora`, HTTP 500 in about 2 ms, also for `http://example.com/`). So no result below proves anything about plain HTTP.

| Finding | Audit evidence | Author recheck |
|---|---|---|
| F-01 DRAFT label | No "draft" text in the stub (1,446 bytes), the dashboard (105,556 bytes) or the 10 rendered views. | `grep -ci draft` on `origin/main` `apps/public-dashboard/index.html` and `index.html`: 0 and 0. The live files are byte-identical to `origin/main` (section 10). |
| F-02 privacy and contact | `/privacy`, `/popia`, `/contact` and 8 other paths return GitHub's 404. No contact for data subjects. | Confirmed in the code: no privacy text, no `mailto:`. The repo has no generic contact address (`git grep` for e-mail patterns outside `public-data/`: only upstream publisher addresses and test fixtures). CHG-2026-012 removed the GitHub issue link from the site and made a new channel an owner decision. |
| F-03 district profile links | 5 of 5 district URLs `…/profiles/municipality-DCnn/` return 404. | Municipal Money uses `…/profiles/district-CODE/` for districts. All **44 of 44** current districts returned 200 with `district-CODE/` (1 request each, 1.1 s apart). 3 of 3 districts returned 404 with `municipality-CODE/`. 8 of 8 metros, 6 of 6 sampled current locals and 6 of 6 sampled ceased locals returned 200 with `municipality-CODE/`. |
| F-04 `http://mfma.treasury.gov.za/Documents/` links | 2,351 relative report paths use that prefix; 857 links are absolute `https://lg.treasury.gov.za/supportingdocs/…`. The HTTPS form of a sample redirects to an ASP.NET error URL. | Counts confirmed: 2,351 relative (financial years ending 2011 to 2020) and 857 absolute (2021 to 2024, all on `lg.treasury.gov.za`). HTTPS sample: **0 of 12** worked. Each went `302` to `Default.aspx` in the same folder, then `302` to `http://mfma.treasury.gov.za/?aspxerrorpath=…`. Plain HTTP: not testable here **[unverified]**. The paths come as published from the Municipal Money API field `opinion.report_url` (`thusa/staging.py` line 137). |
| F-05 freshness pills | The pill compares "last new data" with the SLO. `muni_api`, `nt_budget` and `rsr` show "stale" after a successful check that morning. | Confirmed in the code (`apps/public-dashboard/index.html` lines 334 to 338) and in the manifest of build `B20261118T012055Z`. `itil/sla-slo.md` defines source age as now minus the latest successful snapshot of a published upstream release. An unchanged check is such a snapshot. So the pill does not follow our own SLO definition. |
| F-06 257 vs 292 | `counts.municipalities` = 292; `coverage.headline.entities` = 257. | Confirmed. `municipalities.json`: 205 local, 44 district and 8 metro records have no `exists_to` (257); 35 local records have `exists_to` 2016-08-03. The 257 in the coverage headline counts municipalities with core data due in 2019/20 to 2024/25 (`thusa/report.py` `headline()`), so the 35 fall out. The two figures are both correct. The page does not say what each one counts. |
| F-07 security headers | 200 responses carry HSTS and `access-control-allow-origin: *` only. The dashboard has a CSP meta tag; the stub has none. | Confirmed with `curl -I` on the dashboard. GitHub Pages does not let a site set response headers. |
| F-08 `?data=` | Any `http:` or `https:` URL is accepted; `connect-src` allows `https:` and localhost. | Confirmed (lines 105 to 111 and line 7). The only in-repo user of `?data=` is `scripts/dashboard_check.py` line 552, which passes a same-origin URL. |
| F-09 no custom 404 | GitHub's generic 404 page, no DRAFT label. | Confirmed: no `404.html` in the repo. |
| Item 4 title names | 6 unique supplier values (6 rows) begin with a personal title. | The author found **5** unique values (5 rows) with a personal title, all "DR": 4 begin with it and 1 is the whole value in brackets. The author's first broad pattern also matched 2 values that begin with "ME"; both are the same company name (a business name, not a title). So the audit's 6 is most likely 4 "DR" values plus the 2 "ME" values, and it missed the bracketed one **[the audit's exact pattern is unverified]**. The 5 rows are in `awards-2021.json`, `awards-2023.json` (2), `awards-2024.json` and `awards-2025.json`. In those rows no other column holds a part of the name. |

## 3. Scope and proposed edits, file by file

No edit below is made in this record. The build commit makes exactly these edits and no others.

### 3.1 Item 1: DRAFT label on every page (F-01, F-09, F-13 in part, F-15 in part)

Site pages are the HTML pages of the site: `index.html`, `apps/public-dashboard/index.html`, the new `404.html` and the new `privacy/index.html`. (GitHub Pages also serves other repo files; see N-3 in section 8.)

- `apps/public-dashboard/index.html`:
  - Add a static banner as the first element after the skip link: `<div class="draft" role="note"><p><strong>DRAFT.</strong> This site is a draft. It is built only from the public record: official published data, shown as found, with each source cited. <a href="/privacy/">Privacy and contact</a></p></div>`. It is static HTML, so it shows on every hash route and without JavaScript.
  - Add one CSS rule for `.draft` (a high-contrast band; contrast at least 4.5:1 in the light and dark themes; checked in TEST).
  - Prefix `document.title` with `DRAFT · ` in `setView()`, and the static `<title>`, `og:title` and `twitter:title` with `DRAFT · `.
  - Add `<noscript><p>The interactive views need JavaScript. The open data is at <a href="../../public-data/v1/manifest.json">public-data/v1/manifest.json</a>.</p></noscript>` inside `#view` (F-15).
- `index.html` (stub): add the same banner text above the link, set `lang="en-ZA"`, prefix the title with `DRAFT · `, set `og:url` to the canonical dashboard URL (F-13). The 0-second refresh stays (check_live `site.home` and current behaviour).
- New `404.html` (GitHub Pages serves it for unknown paths): DRAFT banner, the robots `noindex, nofollow` meta tag, the CSP and referrer meta tags of section 3.3 (e), a heading "Page not found", and absolute links to `/apps/public-dashboard/` and `/privacy/`. Absolute links, because the page is served at any path.

### 3.2 Item 2: privacy and contact notice (F-02)

- New `privacy/index.html` (served at `/privacy/`; GitHub Pages redirects `/privacy` to it). Static HTML, no script. It has the DRAFT banner, the robots meta tag, the CSP and referrer meta tags, and these sections in plain language:
  1. **What this site is.** A draft dashboard of South African public money. It shows indicators, not findings. It is built only from official public records.
  2. **What data it shows.** Official published data only, each figure with its source link (see Sources & method). Tender award records include supplier names as National Treasury's eTenders portal publishes them. A supplier value that carries a personal title is masked (first character, five asterisks, last character). Unconfirmed automated leads are never published, only counted. The export removes anything shaped like an SA ID number.
  3. **Purpose and basis.** The purpose is public accountability: to help people follow how public money is budgeted, spent, audited and awarded. The site processes only information that public bodies have already published in official public records, and shows it as found with its source. The lawful basis is the processing of information in public records that the data subject or a public body made public, for this accountability purpose **[legal wording unverified]**.
  4. **What the site does not do.** No cookies, no analytics, no trackers, no forms, no accounts. (Checked: the dashboard has 0 uses of `cookie`, `localStorage`, `sessionStorage` or analytics code; its only 2 `fetch` calls go to the same-origin data path; the CHG-2026-012 headless Chrome network log showed only same-origin requests.)
  5. **Corrections and removal.** How to ask for a correction or a removal, by e-mail to the role mailbox on the site's own domain (Q1). The text asks the person to identify the record by its page link and award id, and not to send ID numbers, phone numbers or addresses.
  6. **How long data stays.** Each nightly build replaces the published files. Earlier versions stay in the site's version history, and earlier data commits keep the supplier values as they were published then; the masks apply from the first nightly publish after the merge (Q4).
  7. **Who is responsible.** The responsible party is GrokForum, with the role mailbox as its contact (Q2). No personal name and no personal contact.
  8. **Your rights.** A person can ask for a correction of their information, or object to its processing, through the role mailbox (Q1). A person can also complain to the Information Regulator (South Africa).
  This list follows the notice items of POPIA section 18(1) (purpose, responsible party, source, rights). The Information Regulator's contact details are linked to its official website, checked at the build.
- Link "Privacy and contact" (`/privacy/`) from: the DRAFT banner on every page, the dashboard footer, the stub, `404.html`, and the privacy page itself (link to the dashboard).
- Contact channel (Q1): a role mailbox on the site's own domain (for example a `privacy@` alias), which the owner creates. A data subject can write without making the request public. The site gets no public issue link; CHG-2026-012 item 2 stays as it is, and no issue form is added.
  - The privacy page gives the address as a `mailto:` link. The build test fails if the address is not on the site's own domain, if it is on a personal mailbox domain (for example gmail, outlook, yahoo, icloud), if its local part looks like a personal name rather than a role word, or if any page links to a GitHub issue form.

### 3.3 Item 3: medium findings

**(a) District Municipal Money links (F-03).**
- `thusa/publish_data.py` line 159: build `profile` as `https://municipalmoney.gov.za/profiles/district-{code}/` when `body_type` is `district`, else `…/municipality-{code}/`. One helper `muni_profile_url(code, body_type)` in `thusa/publish_data.py`.
- `thusa/detectors.py` lines 17, 112 and 265 (flag evidence links) and `thusa/report.py` line 217 (local report): use the same helper. These have the same bug; flag evidence links go public when a flag is confirmed.

**(b) `http://mfma.treasury.gov.za/Documents/` links (F-04).** The sample shows that the HTTPS form does **not** work (0 of 12). So the author proposes **no rewrite to https**. A rewrite would publish 2,351 broken links and would change the official URL, which breaks the rule to present sources as found.
- `apps/public-dashboard/index.html` lines 473 to 474: keep the official link; show its text as `report (http, official link)` for a link that starts with the `report_prefix`; add a `title` attribute: "Official link as published by Municipal Money. The HTTPS form of this address does not serve the file."
- `thusa/publish_data.py` `municipalities()` `about`: add one line: "audit.report paths under report_prefix are published by Municipal Money as http links; the https form does not serve the file (sample of 12, 18 Nov 2026)."
- The 857 `lg.treasury.gov.za` HTTPS links stay as they are.
- Q3: the owner chose to keep the http links as found, with the label `http, official link`.

**(c) Freshness pills (F-05).**
- `apps/public-dashboard/index.html` lines 334 to 338: put the pill rule in one pure function `freshPill(s, nowMs)` between markers `/* fresh:begin */` and `/* fresh:end */` (so a node test can run it, as for the ceiling block). Rule:
  - no `freshness_slo_days`: "no target" (as now);
  - no `last_checked_sast`: "not checked yet" (amber);
  - `last_run_status` matches `failed|blocked`: "last check failed" (red);
  - now minus `last_checked_sast` is more than the SLO: "stale: last checked <date> (target N days)" (red);
  - else: "checked <date>" (green).
- Keep the "Last new data" column as it is, and add the words "no new data from the source since <date>" under it when that date is older than the SLO. So the page shows both facts and does not mix them.
- The overall "Data published … up to date" pill (SLO-PD-1, 48 hours) does not change.
- F-11 (`agsa_annexures.last_checked_sast` is 20 Oct 2026): the author found the cause. `thusa/connectors/agsa.py` does not fetch an annexure again once it is stored, because published annexures do not change (its docstring). So the date is true: that source was last checked on 20 Oct 2026. Under the new rule it shows "checked 20 Oct 2026" (SLO 400 days). No code change.

**(d) 257 vs 292 (F-06).** Both figures are correct; the page must say what each one counts.
- `thusa/publish_data.py` export (line 501): add `municipalities_current` (records with no `exists_to`; 257 today) and `municipalities_ceased` (records with an `exists_to`; 35 today) to `counts`. Add both keys to `COUNT_LABELS` (line 537).
- `apps/public-dashboard/index.html` line 324: the KPI reads "292 municipalities and districts in the records: 257 exist now, 35 have an end date in the source data". The figures come from `counts`, not from the page code.
- Line 322 (coverage KPI): "… 257 municipalities with core data due, 2019/20–2024/25" (adds "with core data due").

**(e) Security headers (F-07).** GitHub Pages cannot send custom response headers. The author proposes the meta equivalents where they exist, and records the rest as limits.

| Control | Can a meta tag set it? | Proposed |
|---|---|---|
| Content-Security-Policy | Yes, except `frame-ancestors`, `report-uri` and `sandbox`, which browsers ignore in a meta tag. A meta CSP covers only the HTML page, not JSON, PNG or `/CNAME`. | Dashboard: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'`. The same on `404.html` and `privacy/index.html` (no script: `script-src 'none'`). Stub: `default-src 'none'; base-uri 'none'; form-action 'none'`. |
| `frame-ancestors` / `X-Frame-Options` | No. | Not set. Limit recorded. The site has no forms or actions, so the framing risk is low. |
| `X-Content-Type-Options: nosniff` | No. | Not set. Limit recorded. |
| Referrer-Policy | Yes (`<meta name="referrer">`). | `<meta name="referrer" content="no-referrer">` on all four pages. |
| Permissions-Policy | No (there is no meta form). | Not set. Limit recorded. The pages use no camera, microphone, location or similar feature. |
| HSTS | GitHub sends `max-age=31556952`; `includeSubDomains` and `preload` cannot be set. | No change. |

The only way to send real headers is a proxy or CDN in front of GitHub Pages. Q5: the owner accepted the GitHub Pages header limits for now. They are revisited with the Q7 follow-up change if the hosting moves.

**(f) `?data=` restricted to our origin (F-08).**
- `apps/public-dashboard/index.html` lines 108 to 109: accept the `?data=` value or `window.PUBLICFUNDS_DATA_BASE` only if `new URL(v, location.href).origin === location.origin`. Otherwise ignore it and use the default same-origin path. Put the block between markers `/* database:begin */` and `/* database:end */` for a node test.
- With (e), `connect-src 'self'` blocks any other origin as a second layer.
- `apps/public-dashboard/README.md` line 10: say that `?data=` accepts a same-origin path only. Line 17 (local example on 127.0.0.1) stays valid, because it is same-origin.

**F-09 (custom 404).** See 3.1.

### 3.4 Item 4: mask supplier values that carry a personal title

- Where: `thusa/publish_data.py`, function `tenders()`, line 242 to 248, where `supplier` is set for each award row. After the existing `(name withheld)` rule and before `scrub()`, call a new function `mask_titled_person(name)`. `pf publish-data` runs this code on every nightly publish and in the POPIA release check (the candidate export), so the mask stays.
- Rule (the watchers' fixed-length mask):
  - A value is a titled person if, after removing outer brackets, it begins with one of the titles `Mr`, `Mrs`, `Ms`, `Miss`, `Mx`, `Dr`, `Prof`, `Adv` (any case, optional full stop) followed by a space and more text, and it holds no organisation word (`Pty`, `Ltd`, `CC`, `Inc`, `Limited`, `Municipality`, `Trust`, `NPC`, `SOC`, `Holdings`, `Trading`, `Enterprise(s)`, `Group`, `JV`, `Joint Venture`, `t/a`). Organisation words match as whole words, case-insensitive (so `Inc` does not match inside a longer word).
  - Exception for `Inc`: when a personal title leads the value, `Inc` does not count as an organisation word. In South Africa an `Inc` is a personal-liability company, and its name usually carries the practitioner's own name. So a value such as `DR AB Example Inc` is masked.
  - The mask is the first letter or digit (upper case), then exactly five asterisks, then the last letter or digit (lower case): always 7 characters. A value with fewer than two letters or digits becomes `*******`.
  - On the build of 18 Nov 2026 the rule masks exactly 5 values (5 rows). The author checked the rule against the 9,551 award rows again on 18 Nov 2026 (05:40 SAST): with the `Inc` exception it gives 5 values (5 rows); without the exception it gives 4, because 1 of the 5 values ends in `Inc`. All 5 masks begin with `D`, because the first character is the title's first letter.
- Fail closed: a new final scan in the export raises `UnsafeExport` (nothing written; publish exit 3, `ACTION: publish refused` in the nightly report) if any award `supplier` cell still matches the titled-person rule. The scan uses the same rule as the mask. So it catches a mask that is lost or made a no-op (for example by a later code change), not a gap in the rule itself. A titled person that the rule does not match passes both the mask and the scan; the must-fail tests and the nightly POPIA release check are the controls for gaps in the rule.
- What does not change: municipality names, buyer names and other columns. (6 official municipality names begin with "Dr"; they are public bodies and must stay as published.) `tenders-summary.json` has no supplier names.
- Masked rows (Q6): keep `ocid`, `award_id`, `reference` and `src`; set `doc` (the tender document link) to null. Unmasked rows keep `doc`. The same `tenders()` code does this, so each nightly publish keeps it.
- Out of scope, noted only: about 2,057 unique supplier values (2,806 rows; audit count) are two to four words with no organisation word. Some may be private persons. They go to a separate later review. The author's own broader pattern found 2,870 such values; the count depends on the word list, so the later review must fix the rule first.

## 4. Tests

The build adds these tests. Each must-fail case is a test that checks the bad input is refused or changed.

| Test | Checks | Must-fail cases |
|---|---|---|
| `tests/test_site_draft_privacy.py` (new) | Every tracked site page (`index.html`, `apps/public-dashboard/index.html`, `404.html`, `privacy/index.html`) has the DRAFT banner text, a link to `/privacy/`, the robots meta tag once, a CSP meta tag and the referrer meta tag. `404.html` links are absolute. The privacy page has the 8 sections, including "Purpose and basis" and "Your rights" with a link to the Information Regulator. | A copy of a page without the banner, without the privacy link, or with a second robots meta tag fails. The privacy page names GrokForum as the responsible party and gives the role `mailto:` address; a page without that name fails. A contact address off the site's domain, on a personal mail domain, or with a personal-name local part fails. Any link to a GitHub issue form on a site page fails. |
| same file | Dashboard CSP: `connect-src 'self'` only; no `https:`, `http:`, `127.0.0.1` or `localhost` source; `base-uri 'none'`, `form-action 'none'`, `object-src 'none'` present. | A CSP with `connect-src 'self' https:` fails. |
| node test of `database:begin..end` | Same-origin `?data=` path is used; default is used when no value. | `?data=https://evil.example/`, `//evil.example/`, `http://127.0.0.1:9/` (page on https), `javascript:alert(1)` and `data:,x` are all ignored (the default base is used). |
| node test of `fresh:begin..end` | The three audit rows (`muni_api`, `nt_budget`, `rsr` on the 18 Nov manifest) give "checked …", not "stale". | `last_checked_sast` older than the SLO gives "stale"; no `last_checked_sast` gives "not checked yet"; `failed` or `blocked` status gives "last check failed". |
| `tests/test_publish_data.py` (added cases) | `profile` uses `district-` for `body_type` `district` and `municipality-` for others; `counts` has `municipalities_current` + `municipalities_ceased` = `municipalities`; the new `about` line is there. | A district with `municipality-` fails. |
| `tests/test_supplier_mask.py` (new) | `DR AB Example` gives `D*****e`; `(DR AB Example)` gives `D*****e`; `Mrs. Q Z` gives `M*****z`; `DR AB Example Inc` gives `D*****c` (the `Inc` exception); a stem with fewer than 2 letters or digits gives `*******`; every mask is 7 characters. | Not masked: `ME Example Builders` (invented company name), `DRYDOCK EXAMPLE TRADING` (invented; no title), `Dr Example Local Municipality` (organisation word), `Dr Example Holdings` (organisation word), `(name withheld)`. A masked row has `doc` null and keeps `ocid`, `award_id` and `reference`; an unmasked row keeps `doc`; a masked row with a non-null `doc` fails. The export raises `UnsafeExport` when `mask_titled_person` is replaced by a no-op and a titled value reaches an award row. Municipality names that begin with "Dr" are unchanged in `municipalities.json`. |
| existing suite | `uv run pytest -q` on the base `d688b031`: 961 passed, 61 skipped (18 Nov 2026, 05:27 SAST). All existing tests must still pass; the robots test (`test_every_served_html_document_has_noindex_meta`) then also covers the two new pages. | |
| TEST, not pytest | `scripts/dashboard_check.py` on a local server of the exact head: no problems. Headless Chrome with axe on the same 10 views as the audit plus `/privacy/` and a 404 path: 0 violations; DRAFT banner visible; no console errors; network log shows only same-origin requests. | |

## 5. Risks

| Risk | Likelihood × impact | Control |
|---|---|---|
| The mask rule misses a titled person, or masks a company. | 2 × 3 = 6 | Fixed title list, organisation-word list with the `Inc` exception, must-fail tests, and the nightly POPIA release check, which reads the full diff. The export's fail-closed scan catches a lost or no-op mask only, not a gap in the rule. |
| Masked names stay public until the first publish after the merge, and stay in the public git history of earlier data commits. | 4 × 3 = 12 | The PR does not touch `public-data/`. Q4: the masks take effect at the first nightly publish after the merge, and there is no history rewrite. Earlier data commits keep the names. |
| A masked row is still traceable through `ocid`, `award_id` and `reference` to the eTenders record. | 3 × 2 = 6 | The mask is pseudonymisation against casual matching, not anonymity. Q6: the `doc` link is dropped on masked rows; `ocid`, `award_id` and `reference` stay. |
| The first nightly after the merge shows changed award files in "What's new" and in the POPIA candidate diff. | 5 × 1 = 5 | Expected. The diff shows 5 supplier cells that change to masks and 5 `doc` cells that change to null (a reduction of personal data, so PASS). Recorded here so that the nightly reviewer is not surprised. |
| A tighter CSP blocks something the page needs. | 2 × 3 = 6 | The page fetches only same-origin JSON (2 `fetch` calls, both from `BASE`). TEST runs headless Chrome and checks the console. |
| `no-referrer` breaks an outbound official link that needs a referrer. | 1 × 2 = 2 | TEST samples the outbound links. |
| An http audit-report link is blocked or warned by a browser as an insecure download from an HTTPS page. | 3 × 2 = 6 **[unverified]** | The link text says "http, official link" (Q3). |
| A change to the dashboard breaks check_live. | 1 × 4 = 4 | `site.app` looks for `PublicFunds` in the page; the new title and banner keep it. check_live runs after the merge. |
| The DRAFT banner or footer link is lost in a later Grok Build regeneration of the page. | 2 × 3 = 6 | The new test fails if the banner or link is missing. |

Does it change which suppliers or people are flagged publicly? No. It reduces which names are shown.

## 6. Implementation plan (DEV, TEST, PROD)

**DEV** (a local worktree of the branch `chg-2026-067-site-draft-privacy`):
1. Make the edits of section 3, and only those, in forward commits.
2. Add the tests of section 4. Run `uv run pytest -q`. All pass.
3. Run the export into a temp folder against a read-only copy of the warehouse (never into `public-data/`, never `scripts/publish-public-data.sh`). Compare with the current `public-data/v1`: the only content changes are 5 supplier cells (to masks), the `doc` cells of the same 5 rows (to null), the district `profile` URLs (44), the new `counts` keys, the new `about` line, and the manifest hashes, sizes and time stamp.
4. POPIA check of the diff (popia-review). Grep the changed lines for names, ids, e-mail addresses and stale words.

**TEST** (local, exact head):
5. Serve the worktree at 127.0.0.1 and run `scripts/dashboard_check.py`, headless Chrome with axe (section 4), and a sample of the new district links and the outbound links.
6. Two independent reviewers check the exact head (expert, shadow, charter, drift).

**PROD** (only after the owner's GO naming the exact head):
7. The orchestrator pushes the branch and opens the PR. Before the merge: tag `snapshot-YYYY-MM-DD-pre-pf-prNN` on the `main` commit, push the tag.
8. Merge the PR (merge commit). GitHub Pages deploys from `main`.
9. Tag `snapshot-YYYY-MM-DD-HHMM` (SAST) on the merge, run `python3 scripts/check_live.py`, and check by hand: DRAFT banner on `/`, the dashboard, `/privacy/` and a 404 path; a district profile link; the freshness column.
10. The first nightly publish after the merge writes the masked award files and the new `counts` (Q4). Check the nightly report and the live `awards-*.json`: 0 unmasked titled values, and `doc` null on the 5 masked rows.

## 7. Claim check (each published claim against its source link)

The owner's rule of 17 Nov 2026 is to cite references and present everything exactly as found. The author checked the fixed claims of the site and the source links on 18 Nov 2026 (1 request per second).

| Claim or link on the site | Source link | Result |
|---|---|---|
| 12 source pages in the Sources table (`manifest.json` `sources[].page`) | each page | 11 returned 200. `https://data.imf.org/en/datasets/IMF.STA:CPI` returned 403 to this client (Akamai; the audit saw the same); the IMF data API link in `prices.json` returned 200. |
| Glossary: definitions, the laws, audit outcomes, eTenders, restricted suppliers, procurement limits | PFMA, MFMA, the SCM regulations, the OCPO instruction note, AGSA pages, eTenders, the restricted-supplier report | All 10 links returned 200. The PFMA link redirects to `archive.treasury.gov.za` (F-17; deferred). |
| Footer: "Statistics South Africa (via the OECD)" | `prices.json` `cpi.publisher` | **Out of date.** CPI now comes from the IMF's republication of Stats SA CPI (`imf_cpi`, status ok), with the OECD series as a secondary series. Proposed footer text: "Statistics South Africa (via the IMF and the OECD)". |
| Footer: National Anti-Corruption Hotline 0800 701 701 | **no source link on the site** | The number is on `https://www.gov.za/faq/justice-and-crime-prevention/how-do-i-report-fraud-or-corruption-state-department-or-state` (200; checked 18 Nov 2026). Proposed: link the line to that page. |
| `dmpr_fuel` licence text with `https://www.dmpr.gov.za/Terms-Conditions;` | the DMPR terms page | The URL with the semicolon returns 404; without it, 200 (F-10). Proposed: `config/public-data.yaml` line 41, write the URL without the semicolon and put a full stop after a space. |
| Home: "data-quality checks: 58 passed, 1 warning(s), 0 failed" | **no description of the warning** | The warning is `award_buyer_match_rate_info` (207, build `B20261118T012055Z`, read-only query of `ops.dq_result`). F-12; deferred (needs a manifest schema change). |
| Home: "292 municipalities and districts" | `manifest.json` `counts` | Correct, but it does not say what it counts. Fixed by 3.3 (d). |
| Sources: "Public data is refreshed … (itil/sla-slo.md, SLO-PD-1)" | **no link** (CHG-2026-012 removed repo links) | Left as it is; noted. |
| Sources: licence or terms | `manifest.json` | 5 sources have no licence text: `agsa_annexures`, `agsa_mfma`, `agsa_pfma`, `s71_noncompliance`, `statssa_cpi`. Noted for a later change. |
| Audit-report links (2,351 http, 857 https) | Municipal Money API | As found; see 3.3 (b). Some official `lg.treasury.gov.za` file names end in what looks like an uploader's user name. They are official URLs, shown as found; noted for the later privacy review. |

## 8. Low findings and other items: in scope or deferred

| Item | Decision |
|---|---|
| F-09 no custom 404 (medium) | In scope (3.1). |
| F-10 semicolon in the DMPR terms URL | In scope (section 7; one config line). |
| F-11 `agsa_annexures.last_checked_sast` | Explained (3.3 c); no code change. |
| F-12 one data-quality warning without a description | Deferred. Warning name recorded in section 7. |
| F-13 stub metadata | In scope in part: `lang`, title, `og:url`, DRAFT banner, CSP and referrer meta. The 0-second refresh stays. |
| F-14 large JSON for lists and maps | Deferred (performance). |
| F-15 no-JS "Loading…" | In scope: one `<noscript>` note (3.1). |
| F-16 `CNAME` and `.nojekyll` served | Deferred (GitHub Pages serves them; harmless). |
| F-17 one meta description; PFMA link redirects | Deferred. |
| F-18 `www` HTTPS | Deferred; revisited with the Q7 follow-up change if the hosting moves (Q5). |
| N-1 (author) footer CPI source out of date | In scope (section 7). |
| N-2 (author) hotline number without a source link | In scope (section 7). |
| N-3 (author) GitHub Pages serves the whole repo root, including 14 review-app templates under `thusa/review/templates/` as `text/html` (for example `login.html`, 200) and the records as `text/markdown` | Follow-up change, out of scope here (Q7: the owner chose to serve only the site files from GitHub Pages, in a separate change). These are not site pages, so they get no DRAFT label in this change. |
| N-4 (author) the same district URL bug in `thusa/detectors.py` and `thusa/report.py` | In scope with (a). |
| About 2,057 short supplier strings | Out of scope; separate later review (3.4). |

### Seen, not touched
- `script-src 'unsafe-inline'` stays; moving the single-file app to hashed scripts is a separate change.
- `apps/public-dashboard/GROK_BUILD_PROMPT.md` does not mention the DRAFT banner or the privacy link; the build adds one line so a regenerated page keeps them.

## 9. How to revert

1. Before the merge, the orchestrator sets the tag `snapshot-YYYY-MM-DD-pre-pf-prNN` on the `main` commit before the merge (NN is the PR number of this change), and pushes it.
2. To revert: `git revert -m 1 <merge sha>` on a branch from `main`, then the same review and GO path (two reviewer PASSes on the exact head, then the owner's GO naming it). GitHub Pages deploys the reverted pages.
3. The next nightly publish after the revert writes the award files without masks again (the export code is reverted). If the masks must stay while the site changes are reverted, revert only the site files in a new change.
4. No skill, routine, secret or data file changes in this PR, so nothing outside git needs a restore.

## 10. Duties kept (diff against live)

Live, `origin/main` and the live skill were compared on 18 Nov 2026 at 05:20 SAST:
- Live site vs `origin/main` `d688b031`: `index.html`, `apps/public-dashboard/index.html`, `robots.txt`, `public-data/v1/manifest.json` and `CNAME` are byte-identical (`cmp`).
- The live skill (outside the repo) vs `docs/bot/live-skill/publicfunds-refresh.MASTER.md`: byte-identical (sha256 `c80a5133…`). This change does not edit either.

| Duty (live today) | Where | After this change |
|---|---|---|
| Nightly publish path: step 4 of the skill, `scripts/publish-public-data.sh --push`, only `public-data/` committed, only on `main` | skill; script | Unchanged. The PR does not touch the script, the skill or the routine prompt. The test that the script stages only `public-data/` stays. |
| Standing pre-approved change (nightly data refresh only) | `changes/CAB-DECISION.md`; skill | Unchanged. It does not cover this code change. |
| Evidence guard (`_evidence_guard`, `thusa/evidence_guard.py`, guard line) | export; skill | Unchanged. Coverage data does not change. |
| POPIA release check before the publish (candidate export and full diff) | skill step 4 | Unchanged. It now also sees the masks. |
| Export safety: `scrub()`, `assert_public_safe()`, `FORBIDDEN_KEYS`, restricted-register person names withheld, refusal writes nothing | `thusa/publish_data.py` | Unchanged; one more fail-closed scan added (stricter). |
| Hidden leads never exported; confirmed flags only; four-eyes for named suppliers | `flags()`; `config/publication.yaml` | Unchanged. |
| check_live after the publish (`scripts/nightly_check_live.py`, `scripts/check_live.py`: home 200, app contains `PublicFunds`, manifest, sample file sizes and sha256, data age) | skill; scripts | Unchanged. The new pages keep `PublicFunds` in the app page. |
| Manifest file hashes and sizes | `manifest()` | Unchanged logic. |
| `robots.txt` with `Disallow: /` and the `noindex, nofollow` meta tag on every served HTML page | CI-117; `tests/test_robots_noindex.py` | Unchanged; the two new pages carry the meta tag, and the existing test enforces it. |
| Source citation: each figure and award row has its `src` reference and source URL | export; dashboard | Unchanged. Masked rows keep `src`. |
| Same-origin data only (CHG-2026-012) | dashboard | Kept and made stricter (3.3 f). |
| Indicators-not-findings notice, footer open-data link, data feed link, hotline line | dashboard | Kept. The hotline line gets its source link; the CPI source wording is corrected. |
| Overall freshness pill (SLO-PD-1, 48 hours) | dashboard | Unchanged. |
| Accessibility (skip link, `lang`, labelled nav, focus outlines, captions) | dashboard | Kept; axe check in TEST. |
| Number formats (CHG-2026-047, CHG-2026-057, CHG-2026-059) | dashboard | Unchanged; new figures use the same helpers. |
| CSP directives `base-uri 'none'`, `form-action 'none'`, `default-src 'self'` | dashboard meta | Kept; `connect-src` narrowed; `object-src 'none'` added. |
| Ceiling block markers (CHG-2026-033 parity test) | dashboard | Unchanged. |
| Wait for another run, account and origin guard, incidents branch, state backup, review-app health check | skill | Not touched. |

No existing duty is removed or weakened.

## 11. Approval

| Role | Name | Commit approved | Date |
|---|---|---|---|
| Reviewer 1 (independent) | | exact head | |
| Reviewer 2 (independent) | | exact head | |
| Owner GO naming the exact head | | exact head | |

A new head needs new reviews. An agent's report of approval is not approval.

## 12. Owner answers to the open questions

Owner answers, 18 Nov 2026 05:40 SAST, as relayed by the orchestrator to the author. The record stays a draft. The merge and the deploy need the owner's GO naming the exact head.

| Question | Answer | Where the plan follows it |
|---|---|---|
| Q1. Contact channel | A role mailbox on the site's own domain. No public issue link. | 3.2; tests (section 4) |
| Q2. Responsible party | GrokForum, with the role mailbox as contact (Owner answer, 18 Nov 2026 06:32 SAST, as relayed by the orchestrator to the author; it replaced the 05:40 SAST placeholder answer). Not a person. | 3.2 item 7; tests |
| Q3. http audit-report links | Keep the http Treasury links as found, labelled `http, official link`. | 3.3 (b) |
| Q4. Timing and history | The masks take effect at the first nightly publish after the merge. No history rewrite. Earlier data commits keep the names. | 3.2 item 6; section 5; section 6 step 10 |
| Q5. Real headers | The GitHub Pages header limits are accepted for now. Revisit them with Q7 if the hosting moves. | 3.3 (e); section 8 (F-18) |
| Q6. Masked rows | Keep `ocid`, `award_id` and `reference`. Drop the `doc` link. | 3.4; tests; section 5 |
| Q7. Served repo files | Serve only the site files from GitHub Pages, in a separate follow-up change. Out of scope here. | section 8 (N-3) |

## 13. POPIA review of this record

popia-review: **PASS**. The record names no private person, no supplier name, no owner account and no agent. It gives counts, file names and masks of the form `D*****e` only. The 6 municipality names that begin with "Dr" are not written out.

## 14. Implementation (18 Nov 2026, DEV)

The author implemented sections 3 and 4 on 18 Nov 2026 between 07:06 and 07:22 SAST, in a local worktree of branch `chg-2026-067-impl` from `main` `76688eca`. The commit did not touch `public-data/`, the publish script, the live skill or the routine prompt.

**Files changed:** `apps/public-dashboard/index.html`, `index.html`, new `404.html`, new `privacy/index.html`, `.gitignore`, `thusa/publish_data.py`, `thusa/detectors.py`, `thusa/report.py`, `config/public-data.yaml`, `apps/public-dashboard/README.md`, `apps/public-dashboard/GROK_BUILD_PROMPT.md`, new `tests/test_site_draft_privacy.py`, new `tests/test_supplier_mask.py`, `tests/test_publish_data.py`, this record, `itil/registers/change-log.md`, `itil/registers/ci-register.md`, `STATUS.md`.

**What was built (as in section 3):**
- Item 1: the DRAFT banner (static HTML) on the dashboard (first element after the skip link), the stub, `404.html` and `privacy/index.html`; `DRAFT · ` in the static titles, `og:title`, `twitter:title` and in `setView()`; one `.draft` CSS rule (white on `#4a1d0a`, the same in the light and dark themes); the `<noscript>` note in `#view`; stub `lang="en-ZA"` and `og:url` set to the dashboard URL. The 0-second refresh stayed.
- Item 2: `privacy/index.html` with the 8 sections of 3.2, no script, GrokForum as responsible party, the role mailbox `privacy@` on the site's own domain (the `CNAME` domain) as a `mailto:` link, **[legal wording unverified]** on the legal-basis wording only, and a link to the Information Regulator's website. "Privacy and contact" (`/privacy/`) is linked from the banner on every page, the dashboard footer, the stub and `404.html`.
- Item 3: (a) `muni_profile_url(code, body_type)` in `thusa/publish_data.py`, used by the export, by the D1 and D8 evidence links in `thusa/detectors.py` (the two queries now also read `g.body_type`) and by the local report in `thusa/report.py`; (b) the label `report (http, official link)` with the `title` text of 3.3 (b) on links under `report_prefix`, and the new `about` line in `municipalities.json`; (c) `freshPill(s, nowMs)` and `noNewDataNote(s, nowMs)` between `/* fresh:begin */` and `/* fresh:end */`; (d) `municipalities_current` and `municipalities_ceased` in `counts` and `COUNT_LABELS`, the new KPI wording and "with core data due"; (e) the meta CSP of 3.3 (e) and `<meta name="referrer" content="no-referrer">` on the four pages; (f) `dataBase(v, pageHref)` between `/* database:begin */` and `/* database:end */`, and the README line.
- Item 4: `is_titled_person()`, `mask_value()` and `mask_titled_person()` in `thusa/publish_data.py`; `tenders()` calls the mask after the `(name withheld)` rule and before `scrub()`, and sets `doc` to null on a masked row. `assert_no_titled_supplier()` runs in `export()` before anything is written and raises `UnsafeExport` (publish exit 3).
- Section 7: footer "Statistics South Africa (via the IMF and the OECD)"; the hotline line links to the gov.za page (link text "source: gov.za"); the DMPR terms URL in `config/public-data.yaml` has no semicolon.
- Section 8, "Seen, not touched": one line in `GROK_BUILD_PROMPT.md` keeps the banner, the privacy link and the `?data=` rule in a regenerated page.

**Departures from the RFC (each one small; reviewers please check):**
1. `.gitignore`: two negation lines (`!/404.html`, `!/privacy/index.html`). The repo ignores `*.html` except named files, so without them the two new pages could not be committed or served.
2. Official municipality names: `is_titled_person()` returns false for a supplier value that equals an official municipality name (short or long name from `curated.gov_body`, sphere local, case and spacing ignored). This applies the 3.4 rule "municipality names do not change" to supplier cells too, as the orchestrator's build brief asked. On the 18 Nov 2026 warehouse, 0 supplier values equal an official name, so the count stayed at 5.
3. The fail-closed scan also refuses a supplier cell in mask form (`X*****y` or `*******`) that still has a `doc` link. This makes the section 4 case "a masked row with a non-null `doc` fails" a check in the export. 0 supplier values in the warehouse contain `*`.
4. The mask is two functions: `mask_value()` (the pure 7-character mask) and `mask_titled_person()`. A value that matches the rule always has at least 2 letters (the title), so `*******` can only come from `mask_value()`; the test calls it directly.
5. Freshness: a `last_checked_sast` that does not parse gives "not checked yet". Dates show in the `en-ZA` short form with a two-digit day ("01 Nov 2026"). The "Last new data" note is `noNewDataNote()` in the same marked block, so the node test covers it.
6. KPI: when the manifest has no sub-counts (the live manifest until the first nightly publish after the merge), the KPI keeps the old label "municipalities and districts".
7. Stub CSP: `default-src 'none'; img-src data:; base-uri 'none'; form-action 'none'`. `img-src data:` was added because headless Chrome logged a CSP error for the stub's inline `data:` favicon with the RFC's policy.
8. Privacy page section 6 says the masks apply "from the first nightly publish after this notice took effect" (plain words for the public) instead of "after the merge".
9. No `about` line was added to the award files (the RFC names none), so award files change only in the masked cells.
10. The Information Regulator link (`https://inforegulator.org.za/`) did not answer from the box on 18 Nov 2026 (curl: 4 tries, 15 to 20 s each, no response; a web fetch: HTTP 504); a web search index lists it as the regulator's home page. **[link not checked from the box; unverified]**

**Tests (DEV):** `uv run pytest -q` on the worktree before the commit (18 Nov 2026, 07:21 SAST): 1,052 passed, 61 skipped (base `76688eca`: 961 passed, 61 skipped; 91 new tests). New tests: `tests/test_site_draft_privacy.py` (pages, banner, robots, CSP, referrer, privacy sections, contact rules, issue-form links, node tests of `database` and `fresh` with must-fail cases), `tests/test_supplier_mask.py` (rule, masks, Inc exception, organisation words, official names, export on a copy of the synthetic warehouse, no-op mask refused, masked row with `doc` refused, district profile and counts) and 4 cases in `tests/test_publish_data.py`.

**Candidate export (DEV, step 3):** `pf publish-data --out` into a temp folder outside the repo, holding a copy of `public-data/v1` from `76688eca`, against a copy of the warehouse of build `B20261118T012055Z` (and a copy of the review DB). The same export with the base code first reproduced every data file of `public-data/v1` byte for byte (only `manifest.json` differed: generated time). The new code changed:
- 4 award files: 5 supplier cells to masks (`D*****e` 2, `D*****s` 2, `D*****c` 1) and the `doc` cells of the same 5 rows to null; no other cell changed. Full original values found in the candidate files: 0. No other column of the 5 rows holds a part of a name.
- `municipalities.json`: 44 `profile` cells (all `district` type) to `district-CODE/`, and 1 new `about` line.
- `manifest.json`: `counts.municipalities_current` = 257 and `counts.municipalities_ceased` = 35 (sum 292), the `dmpr_fuel` licence text, file hashes and sizes, generated time.
- `changes.json` and `feed.json`: 1 new entry ("Figures updated or corrected in: awards-2021.json, awards-2023.json, awards-2024.json, awards-2025.json, municipalities.json.").
- Evidence guard: pass. Counts otherwise unchanged (9,551 awards, 349 hidden leads, 0 confirmed flags).

**TEST (local):** `scripts/dashboard_check.py` with axe-core on a local server of the worktree: problems `[]`. Headless Chrome on `/privacy/`, a 404 path (served as on GitHub Pages) and the dashboard, light and dark: banner visible, titles start with `DRAFT · `, 0 requests to another origin, 0 axe WCAG 2 A/AA violations on `/privacy/` and the 404 page; no console errors apart from the 404 status of the 404 path. The dashboard home on the candidate data showed "257 exist now, 35 have an end date in the source data" and "checked 18 Nov 2026" for `muni_api`, `nt_budget` and `rsr`. The stub redirected to the dashboard with no console error.

**Effects to expect at the first nightly after the merge:**
- The award files, `municipalities.json`, the manifest counts and "What's new" change as in the candidate export (section 5 row 4).
- The D1 and D8 evidence links of leads on district municipalities change to `district-CODE/` (36 D1 and 20 D8 leads on the 18 Nov 2026 build). Their evidence hash changes. The review DB had 0 decisions on 18 Nov 2026, so no review is affected today.
- The privacy page gives the role address from the merge. The owner creates the alias on the site's domain (3.2); mail delivery to it was not tested **[unverified]**.

**Seen, not touched:**
- `thusa/review/templates/entity.html` (local review app) has the same `municipality-CODE/` link for districts. It is not a site page and not in section 3.
- Dark theme: the current nav item on the dashboard has a contrast of 4.03:1 (axe `color-contrast`, serious). The same result on the base code; not in scope.

**POPIA (popia-review):** PASS. The change reduces published personal data (5 masks, 5 `doc` links removed). This record, the tests and the commit name no private person, no supplier name and no owner account; tests use invented names only.

## Revisions

- Rev 1 (18 Nov 2026, 05:43 SAST, commit `cdba9ab6`), after reviewer A's PASS with concerns on `0a21e0e0`: (1) the mask rule exempts `Inc` when a personal title leads the value, and organisation words match as whole words, case-insensitive; a recheck on the data gave 5 values (4 without the exception); (2) the record says that the export scan catches a lost or no-op mask, not a gap in the rule; (3) the privacy page plan has "Purpose and basis" and "Your rights" sections (POPIA section 18(1)); (4) box paths were replaced by role wording ("the live skill (outside the repo)", "a local worktree"). No code changed.
- Rev 1, same commit: the owner's answers to Q1 to Q7 were recorded in section 12 (Owner answers, 18 Nov 2026 05:40 SAST, as relayed by the orchestrator to the author), and sections 3.2, 3.3 (b) and (e), 3.4, 4, 5, 6, 8 and the header were updated to match them (role mailbox only, no issue form; project named as responsible party, [unverified]; http links kept with a label; masks from the first nightly after the merge, no history rewrite; header limits accepted; `doc` dropped on masked rows; served-files change as a follow-up).
- Rev 2 (18 Nov 2026, on `cdba9ab6`): the responsible party is GrokForum (Owner answer, 18 Nov 2026 06:32 SAST, as relayed by the orchestrator to the author); the placeholder and its [unverified] flag were removed, and [unverified] stays only on the legal-basis wording; the Q2 entry in section 12 and the privacy-page test were updated; the change-log row states that the owner decided the contact channel (role mailbox, Q1, 18 Nov 2026 05:40 SAST); the Rev 1 time was corrected to the commit time (05:43 SAST); the STATUS line was updated. No code changed.

- Rev 3 (18 Nov 2026, implementation on branch `chg-2026-067-impl` from `76688eca`): section 14 added; the Status field records the RFC merge, the post-merge tag and the implementation.

## Post-implementation review
- Outcome: (written after the build, review and GO)
