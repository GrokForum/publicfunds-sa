# Source pack plan, November 2026

Planning only. This document maps a source pack dated 20 Nov 2026 (Africa/Johannesburg) to the existing improvement backlog. It does not ingest new data, change a loader, or publish anything.

The pack was an external planning list of official public sources. This plan uses role words only. Licence and access notes below repeat what the pack stated, or what this repository already records (known errors and the CSI register). Live HTTP results in the pack are dated 20 Nov 2026 and are marked as such; they were not re-checked in this change.

Related backlog: `docs/roadmap/improvements-2026-10.md` and `itil/registers/csi-register.md`. Manual-drop path: `RB-06` and `thusa/connectors/ppd.py` (already in the tree).

## How to read the table

- **Access** is how this project would obtain the file, not a request to collect it now.
- **Effort** uses the pack's scale: S = small (loader already exists or a short parse), M = medium, L = large (PDF or many entities).
- **POPIA risk** is about later publication, not about reading a public page. Named private persons and one-person supplier names stay masked or unpublished until four-eyes review, as in the design and ADR-0005 / ADR-0008.

## Proposed order

1. CSI-026 — Procurement Payments Dashboard (PPD) BAS/LOGIS transaction CSV, owner manual drop into the existing `ppd.py` loader. This also unlocks CSI-029 (unit-price outlier detector).
2. CSI-037 — Census 2022 population per municipality, owner manual drop of an official table.
3. CSI-035 — Presidency SIU reports and Department of Justice Special Tribunal records, at institution or entity level first.
4. CSI-039 — Provincial budgets and in-year spending (EPRE/IYM) from Vulekamali public dataset pages.
5. CSI-030 — AGSA MFMA and PFMA reports for 2024–25 (audit outcomes, material irregularities, UIF&W).
6. CSI-046 — Irregular and fruitless and wasteful expenditure, and audit outcomes, from major SOE annual reports (start with Eskom, Transnet and SANRAL).

Each later item can start earlier if a file is already in hand, but the order above is the recommended sequence: first the drop that the current loader already accepts, then population (needed for per-resident figures), then new collectors in rising effort.

## Source map

| Order | CSI | Source | Licence / terms (as stated) | Access method | Effort | POPIA risk |
|---|---|---|---|---|---|---|
| 1 | CSI-026 (unlocks CSI-029) | National Treasury Procurement Payments Dashboard: BAS/LOGIS transaction list (`Procurement_Spend_Transaction_List.csv`). User guide and portal on `data.etenders.gov.za` (pack recorded HTTP 200 on 20 Nov 2026). | The pack states National Treasury Section 8 open reuse with attribution. Confirm the licence on the file before any publish. | Manual export from the Power BI dashboard by the operator, then a drop into `manual_drop/` for the existing `ppd.py` loader (`RB-06`). No automated scrape. Known blocker: KE-009 (the PPD source still needs a manual drop; the existing loader records that state). The portal excludes SOEs, municipalities, Defence, SAPS, SARS and SSA. | S (loader already in the tree) | Medium. Supplier names can appear in the CSV. Leads that name a supplier or a person stay out of the public export until four-eyes review. This is the same rule as other payment sources. |
| 1b | CSI-029 | Unit-price outlier detector (fuel first: rand per litre on awards or payments versus the DMPR on-the-glass price for that month and zone). | Not a new dataset. Uses CSI-026 payments plus the existing DMPR fuel series. | No ingest in this plan. A later Normal change would add the detector after a PPD drop is loaded. | S–M after CSI-026 is loaded | Medium, same as other detectors that can name a supplier. Public flags stay behind four-eyes review. |
| 2 | CSI-037 | Census 2022 population per municipality. The pack notes that the HDX COD-PS South Africa table (`data.humdata.org/dataset/cod-ps-zaf`, pack recorded HTTP 200 on 20 Nov 2026) holds 2020 district and local projections, not Census 2022. Municipal Money (`municipalmoney.gov.za`) is an OpenUp / National Treasury site (pack recorded HTTP 200). | HDX table: the pack states CC BY-IGO (UN OCHA / Stats SA 2020 projections). Census 2022: use the licence printed on the official Stats SA table; record it when the file is dropped. | Scripted fetch from `statssa.gov.za` is blocked (KE-003). A genuine Census 2022 municipal table needs one manual browser download by the operator into `manual_drop/`. Do not substitute the 2020 HDX projections if the official 2022 counts are the target. | S–M | Low for counts by municipality (no natural-person rows). Keep any microdata out of the drop. |
| 3 | CSI-035 | Presidency SIU reports (`thepresidency.gov.za/tso/siu-reports`) and Department of Justice Special Tribunal pages (`justice.gov.za/tribunal/index.html`). The pack recorded HTTP 200 for both on 20 Nov 2026. It also recorded that `siu.org.za` failed a TLS trust check from the pack's environment, and that `saflii.org/za/cases/ZAST/` returned HTTP 403; those two hosts are not proposed as first access methods. | The pack describes these as South African government public records. Confirm any notice on each PDF or page before reuse. | Fetch the official HTML and PDF lists (gazettes, judgments, reports, media statements) from the two hosts above. Start at institution or entity level. Do not ingest in this change. | M–L | High if texts name private persons or one-person firms. First publication must link institutions, organs of state, and court or tribunal orders only. Any supplier or private-person wording needs legal and four-eyes review before it is public. |
| 4 | CSI-039 | Vulekamali provincial budgeted and actual expenditure (`vulekamali.gov.za/datasets/budgeted-and-actual-provincial-expenditure`, pack recorded HTTP 200 on 20 Nov 2026, including 2025/2026 pages). | The pack states National Treasury / Imali Yethu open budget data. Confirm the licence on each resource file. | Same pattern as the national budget-versus-actual load (`nt_budget` / KE-002): follow public dataset pages to CSV or XLSX. The CKAN API on `data.vulekamali.gov.za` remains failed (KE-002). If a resource link points only at that API host, use a manual operator download. | M | Low to medium. These are departmental budget and spending tables. Keep any unexpected personal fields out of the publish set. |
| 5 | CSI-030 | Auditor-General MFMA 2024–25 (`mfma-2025.agsa.co.za`) and PFMA 2024–25 (`agsa.co.za` PFMA 2024-2025 report pages). The pack recorded HTTP 200 on 20 Nov 2026. | The pack describes these as AGSA public audit reports; attribute Auditor-General of South Africa. Confirm any reuse notice on the site or PDF. | The 2023–24 Excel annexures are already loaded. KE-013 records that 2024–25 MFMA annexures are PDF-only (no Excel workbook like 2023–24) and that PFMA 2024–25 links PDFs rather than Excel. Material irregularities sit in report chapters and per-municipality MFMA pages. A later parser would read those PDFs or pages. This also bears on KE-006 (Municipal Money audit opinions stop at FYE 2024). | L | Medium. Auditee names are public entities. Do not copy private-person names from narrative chapters into the public export without review. |
| 6 | CSI-046 | Annual reports of major state-owned entities, starting with Eskom, Transnet and SANRAL investor or corporate annual-report pages (the pack recorded HTTP 200 on 20 Nov 2026 for the three index pages it listed). | SOE public statutory reports. Confirm the reuse notice in each report. | Manual or later-assisted download of the PDF annual financial statements and PFMA notes; extract irregular and fruitless and wasteful expenditure and the audit opinion. No ingest in this change. | L | Medium. Statutory reports may name individuals in remuneration or legal notes. Extract only entity-level UIF&W and audit-opinion figures for a first load. |

## What stays the same

- No new connector, no new drop, and no change to published data in this change.
- Four-eyes review and masking rules stay as they are.
- Certificate verification on collectors stays enabled.
- The PPD loader already accepts a well-formed manual drop; this plan does not alter it.

## Follow-up (later changes)

Each source above, when work starts, needs its own change record, tests, a recorded licence check, and a rollback note. CSI-029 is a detector change (Normal-high) and must not run on public output until the review rule is met.
