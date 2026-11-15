-- CHG-2026-062 Phase 1: fruitless and wasteful (F&W) expenditure as a share of audited spending, per municipality.
-- Inputs are already in the warehouse; no new source:
--   F&W amount : curated.uifw_line, uifw_type 'fruitless_wasteful' (Municipal Money uifwexp cube, AFS notes)
--   denominator: curated.muni_total, amount_type 'AUDA', total_expenditure_cents (audited operating expenditure)
-- Years: amounts for financial years ending 2018 to 2024 (FW_FYE_MIN / FW_FYE_MAX in thusa/fw_metric.py). Shares only for
-- 2020 to 2024 (FW_SHARE_FYE_MIN). A test keeps the SQL numbers equal to the Python constants.
-- Years ending 2012 to 2017 are left out until a manual spot check passes (RFC CHG-2026-062, test T5).
-- Share rule (documented calculation, CHG-2026-057): percentage points, cut (truncated toward zero) to 4 decimal
-- places with integer arithmetic. Nothing is rounded. A known 0 stays 0.
-- The share is NULL (not available) and share_status gives the reason, checked in this order:
--   fw_unknown                  : no F&W amount
--   denominator_unknown         : no audited spending
--   denominator_not_positive    : audited spending is zero or less
--   denominator_incomplete_year : years ending 2018 and 2019. Audited spending at the source is summed from sparse line
--                                 items and is incomplete for many municipalities (reviewer finding on 180154f7)
--   denominator_no_reference    : 2020-2024, but the municipality has no OTHER year 2020-2024 with audited spending > 0,
--                                 so the completeness check cannot run
--   denominator_incomplete      : 2020-2024, audited spending is under 50% of the median of the municipality's audited
--                                 spending in its OTHER years 2020-2024 (only years with spending > 0 count)
--   share_over_100              : fallback. The check above passed, but F&W is still larger than audited spending
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
), ref AS (
  -- reference for each body-year: median audited spending over the body's OTHER years 2020-2024 with spending > 0
  SELECT k.gov_body_id, k.fye, count(o.denom_cents)::INTEGER AS denom_ref_years,
         median(o.denom_cents::DECIMAL(38,1))::DECIMAL(38,1) AS denom_ref_median
  FROM k LEFT JOIN den o
    ON o.gov_body_id = k.gov_body_id AND o.fye <> k.fye AND o.fye BETWEEN 2020 AND 2024 AND o.denom_cents > 0
  GROUP BY k.gov_body_id, k.fye
), j AS (
  SELECT k.gov_body_id, g.name, g.province, g.body_type, k.fye,
         (k.fye - 1)::VARCHAR || '/' || right(k.fye::VARCHAR, 2) AS fy_label,
         fw.fw_cents, den.denom_cents, den.denom_derivation, ref.denom_ref_years, ref.denom_ref_median,
         CASE WHEN fw.fw_cents IS NULL THEN 'fw_unknown'
              WHEN den.denom_cents IS NULL THEN 'denominator_unknown'
              WHEN den.denom_cents <= 0 THEN 'denominator_not_positive'
              WHEN k.fye < 2020 THEN 'denominator_incomplete_year'
              WHEN ref.denom_ref_years = 0 THEN 'denominator_no_reference'
              WHEN den.denom_cents * 2 < ref.denom_ref_median THEN 'denominator_incomplete'
              ELSE 'ok' END AS share_status,
         coalesce(fw.source_id, den.source_id) AS source_id,
         coalesce(fw.source_file, den.source_file) AS source_file,
         coalesce(fw.source_sha256, den.source_sha256) AS source_sha256,
         coalesce(fw.fetched_at_utc, den.fetched_at_utc) AS fetched_at_utc,
         coalesce(fw.source_locator, den.source_locator) AS source_locator,
         den.source_sha256 AS denom_source_sha256
  FROM k
  JOIN curated.gov_body g ON g.gov_body_id = k.gov_body_id AND g.sphere = 'local'
  JOIN ref ON ref.gov_body_id = k.gov_body_id AND ref.fye = k.fye
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
       s.denom_ref_years,
       s.denom_ref_median,            -- in cents; DECIMAL because a median of an even count can end in .5
       CASE WHEN s.share_calc > 100 THEN 'share_over_100' ELSE s.share_status END AS share_status,
       CASE WHEN s.share_calc <= 100 THEN s.share_calc END::DECIMAL(18,4) AS fw_share_pct,
       p.fw_cents::BIGINT AS fw_prev_cents,
       CASE WHEN p.fw_cents IS NOT NULL AND s.fw_cents IS NOT NULL THEN s.fw_cents - p.fw_cents END::BIGINT AS fw_change_cents,
       s.source_id, s.source_file, s.source_sha256, s.fetched_at_utc, s.source_locator, s.denom_source_sha256
FROM s
-- prior year: the same body, fye - 1, and only inside the range (2018 has no prior year here)
LEFT JOIN s p ON p.gov_body_id = s.gov_body_id AND p.fye = s.fye - 1;

-- National view: one row per financial year.
--   fw_total_cents : sum of every known municipal F&W amount (all rows with an amount, hidden shares included)
--   share base     : ONLY rows with share_status 'ok'. A municipality-year whose share is hidden is left out of BOTH the
--                    F&W part (fw_share_base_cents) and the audited-spending part (denom_share_base_cents).
--   n_share_hidden : rows with an amount whose share is hidden (any status other than ok and fw_unknown)
--   national_share_status: denominator_incomplete_year for 2018 and 2019 (no national share), no_base when no row is
--                    ok, else ok. national_share_pct uses the same cut-not-round rule.
CREATE OR REPLACE TABLE marts.fw_national AS
WITH a AS (
  SELECT fye, any_value(fy_label) AS fy_label,
         count(*) AS n_rows,
         count(fw_cents) AS n_fw_known,
         count(*) FILTER (WHERE share_status = 'ok') AS n_share_known,
         count(*) FILTER (WHERE share_status NOT IN ('ok', 'fw_unknown')) AS n_share_hidden,
         sum(fw_cents)::BIGINT AS fw_total_cents,
         coalesce(sum(fw_cents) FILTER (WHERE share_status = 'ok'), 0)::BIGINT AS fw_share_base_cents,
         coalesce(sum(denom_cents) FILTER (WHERE share_status = 'ok'), 0)::BIGINT AS denom_share_base_cents
  FROM marts.fw_metric
  GROUP BY fye
)
SELECT a.*,
       CASE WHEN fye < 2020 THEN 'denominator_incomplete_year'
            WHEN denom_share_base_cents <= 0 THEN 'no_base'
            ELSE 'ok' END AS national_share_status,
       CASE WHEN fye >= 2020 AND denom_share_base_cents > 0 THEN
         (sign(fw_share_base_cents) * ((abs(fw_share_base_cents)::HUGEINT * 1000000) // denom_share_base_cents::HUGEINT))::DECIMAL(18,0)
           * 0.0001::DECIMAL(5,4)
       END::DECIMAL(18,4) AS national_share_pct
FROM a;
