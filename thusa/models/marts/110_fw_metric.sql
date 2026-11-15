-- CHG-2026-062 Phase 1: fruitless and wasteful (F&W) expenditure as a share of audited spending, per municipality.
-- Inputs are already in the warehouse; no new source:
--   F&W amount : curated.uifw_line, uifw_type 'fruitless_wasteful' (Municipal Money uifwexp cube, AFS notes)
--   denominator: curated.muni_total, amount_type 'AUDA', total_expenditure_cents (audited operating expenditure)
-- Years: financial years ending 2018 to 2024 only (FW_FYE_MIN / FW_FYE_MAX in thusa/fw_metric.py; a test keeps them equal).
-- Years ending 2012 to 2017 are left out until a manual spot check passes (RFC CHG-2026-062, test T5).
-- Share rule (documented calculation, CHG-2026-057): percentage points, cut (truncated toward zero) to 4 decimal
-- places with integer arithmetic. Nothing is rounded. The share is NULL (not available) when the F&W amount is
-- unknown, the denominator is unknown, the denominator is zero or less, or the share would be over 100%.
-- A known 0 stays 0. share_status says which case applies.
CREATE OR REPLACE TABLE marts.fw_metric AS
WITH fw AS (
  SELECT gov_body_id, fye, amount_cents AS fw_cents,
         source_id, source_file, source_sha256, fetched_at_utc, source_locator
  FROM curated.uifw_line
  WHERE uifw_type = 'fruitless_wasteful' AND measure = 'reported' AND fye BETWEEN 2018 AND 2024
), den AS (
  SELECT gov_body_id, fye, total_expenditure_cents AS denom_cents, expenditure_basis AS denom_derivation,
         source_id, source_file, source_sha256, fetched_at_utc, source_locator
  FROM curated.muni_total
  WHERE amount_type = 'AUDA' AND fye BETWEEN 2018 AND 2024
), k AS (
  SELECT gov_body_id, fye FROM fw UNION SELECT gov_body_id, fye FROM den
), j AS (
  SELECT k.gov_body_id, g.name, g.province, g.body_type, k.fye,
         (k.fye - 1)::VARCHAR || '/' || right(k.fye::VARCHAR, 2) AS fy_label,
         fw.fw_cents, den.denom_cents, den.denom_derivation,
         CASE WHEN fw.fw_cents IS NULL THEN 'fw_unknown'
              WHEN den.denom_cents IS NULL THEN 'denominator_unknown'
              WHEN den.denom_cents <= 0 THEN 'denominator_not_positive'
              ELSE 'ok' END AS share_status,
         coalesce(fw.source_id, den.source_id) AS source_id,
         coalesce(fw.source_file, den.source_file) AS source_file,
         coalesce(fw.source_sha256, den.source_sha256) AS source_sha256,
         coalesce(fw.fetched_at_utc, den.fetched_at_utc) AS fetched_at_utc,
         coalesce(fw.source_locator, den.source_locator) AS source_locator,
         den.source_sha256 AS denom_source_sha256
  FROM k
  JOIN curated.gov_body g ON g.gov_body_id = k.gov_body_id AND g.sphere = 'local'
  LEFT JOIN fw ON fw.gov_body_id = k.gov_body_id AND fw.fye = k.fye
  LEFT JOIN den ON den.gov_body_id = k.gov_body_id AND den.fye = k.fye
), s AS (
  SELECT j.*,
         CASE WHEN j.share_status = 'ok' THEN
           (sign(j.fw_cents) * ((abs(j.fw_cents)::HUGEINT * 1000000) // j.denom_cents::HUGEINT))::DECIMAL(18,0)
             * 0.0001::DECIMAL(5,4)
         END::DECIMAL(18,4) AS share_calc
  FROM j
)
SELECT s.gov_body_id, s.name, s.province, s.body_type, s.fye, s.fy_label,
       s.fw_cents::BIGINT AS fw_cents,
       s.denom_cents::BIGINT AS denom_cents,
       'audited_total_expenditure' AS denom_basis,
       s.denom_derivation,
       -- share_over_100: the F&W amount is larger than audited spending. One of the two figures is then very likely
       -- incomplete (for example a denominator summed from only a few line items), so the share is not shown.
       CASE WHEN s.share_calc > 100 THEN 'share_over_100' ELSE s.share_status END AS share_status,
       CASE WHEN s.share_calc <= 100 THEN s.share_calc END::DECIMAL(18,4) AS fw_share_pct,
       p.fw_cents::BIGINT AS fw_prev_cents,
       CASE WHEN p.fw_cents IS NOT NULL AND s.fw_cents IS NOT NULL THEN s.fw_cents - p.fw_cents END::BIGINT AS fw_change_cents,
       s.source_id, s.source_file, s.source_sha256, s.fetched_at_utc, s.source_locator, s.denom_source_sha256
FROM s
-- prior year: the same body, fye - 1, and only inside the shown range (2018 has no prior year here)
LEFT JOIN s p ON p.gov_body_id = s.gov_body_id AND p.fye = s.fye - 1;

-- National view: one row per financial year. Two different sums, never mixed:
--   fw_total_cents       : sum of every known municipal F&W amount (municipalities with a known amount)
--   fw_share_base_cents  / denom_share_base_cents : only rows with share_status 'ok' (both values known, denominator
--                          > 0, share not over 100%)
--   national_share_pct   : fw_share_base_cents / denom_share_base_cents, same cut-not-round rule as above
CREATE OR REPLACE TABLE marts.fw_national AS
SELECT fye, any_value(fy_label) AS fy_label,
       count(*) AS n_rows,
       count(fw_cents) AS n_fw_known,
       count(*) FILTER (WHERE share_status = 'ok') AS n_share_known,
       sum(fw_cents)::BIGINT AS fw_total_cents,
       coalesce(sum(fw_cents) FILTER (WHERE share_status = 'ok'), 0)::BIGINT AS fw_share_base_cents,
       coalesce(sum(denom_cents) FILTER (WHERE share_status = 'ok'), 0)::BIGINT AS denom_share_base_cents,
       CASE WHEN coalesce(sum(denom_cents) FILTER (WHERE share_status = 'ok'), 0) > 0 THEN
         (sign(sum(fw_cents) FILTER (WHERE share_status = 'ok'))
          * ((abs(sum(fw_cents) FILTER (WHERE share_status = 'ok'))::HUGEINT * 1000000)
             // (sum(denom_cents) FILTER (WHERE share_status = 'ok'))::HUGEINT))::DECIMAL(18,0) * 0.0001::DECIMAL(5,4)
       END::DECIMAL(18,4) AS national_share_pct
FROM marts.fw_metric
GROUP BY fye;
