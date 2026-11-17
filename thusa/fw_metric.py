"""CHG-2026-062 Phase 1: fruitless and wasteful (F&W) expenditure metric for municipalities.

The mart is plain SQL (thusa/models/marts/110_fw_metric.sql). This module holds the constants that the export,
the data-quality checks and the tests share, so the year range, the completeness rule and the status codes are
written in one place.
"""
from __future__ import annotations

# Amounts: financial years ending 2018 to 2024. Years ending 2012 to 2017 stay out until a manual spot check passes
# (RFC CHG-2026-062, test T5). The SQL model repeats these numbers; tests/test_fw_metric.py keeps them equal.
FW_FYE_MIN = 2018
FW_FYE_MAX = 2024

# Shares: only from the year ending 2020. For 2018 and 2019 audited spending at the source is incomplete for many
# municipalities (reviewer finding on 180154f7), so the share is hidden for every municipality and nationally.
FW_SHARE_FYE_MIN = 2020

# Completeness check (2020-2024). The reference is the median audited spending of the same municipality in its OTHER
# years 2020-2024 (only years with spending > 0 count; one year is enough). With no such year, the reference is that
# year's adjusted budget (curated.muni_total ADJB total_expenditure_cents), if it is above zero. The share is hidden
# when audited spending is under FW_REF_MIN_RATIO x the reference, or over FW_REF_MAX_RATIO x the reference, or (with
# other years as the reference) over FW_REF_MAX_RATIO x that year's adjusted budget. A missing, zero or negative
# adjusted budget is never used.
FW_REF_MIN_RATIO = 0.5
FW_REF_MAX_RATIO = 2.5

# share_status codes in marts.fw_metric, in the order the SQL checks them. Only 'ok' has a share; every other code
# means "not available".
SHARE_STATUS = {
    "ok": "share available",
    "fw_unknown": "F&W amount not available",
    "denominator_unknown": "audited spending not available",
    "denominator_not_positive": "audited spending is zero or less",
    "denominator_incomplete_year": "audited spending for 2017/18 and 2018/19 is incomplete at the source for many municipalities",
    "denominator_no_reference": "no other year 2019/20-2023/24 with audited spending and no adjusted budget to check this year's figure against",
    "denominator_incomplete": "audited spending is under half of this municipality's usual (median) audited spending, or of that year's adjusted budget when there is no other year, so it is probably incomplete",
    "denominator_implausible_high": "audited spending is over 2.5 times this municipality's usual (median) audited spending or that year's adjusted budget, so the share would be too low",
    "share_over_100": "F&W is larger than audited spending, so one figure is probably incomplete",
}

# Statuses that hide a share although both figures exist (the completeness rules). Counted in a warning check.
GUARD_STATUS = ("denominator_incomplete_year", "denominator_no_reference", "denominator_incomplete",
                "denominator_implausible_high", "share_over_100")

# denom_check_basis in marts.fw_metric (2020-2024): which reference the completeness check used. NULL before 2020 and
# when there is no reference at all.
CHECK_BASIS = ("other_years", "adjusted_budget")

# national_share_status codes in marts.fw_national.
NATIONAL_STATUS = {
    "ok": "national share available",
    "denominator_incomplete_year": "no national share: audited spending for this year is incomplete at the source",
    "no_base": "no municipality has a share for this year",
}

# The share is percentage points cut (not rounded) to this many decimal places (CHG-2026-057 documented calculation).
SHARE_PLACES = 4
