"""CHG-2026-062 Phase 1: fruitless and wasteful (F&W) expenditure metric for municipalities.

The mart is plain SQL (thusa/models/marts/110_fw_metric.sql). This module holds the constants that the export,
the data-quality checks and the tests share, so the year range and the status codes are written in one place.
"""
from __future__ import annotations

# Financial years ending 2018 to 2024 only. Years ending 2012 to 2017 stay out until a manual spot check passes
# (RFC CHG-2026-062, test T5). The SQL model repeats these two numbers; tests/test_fw_metric.py keeps them equal.
FW_FYE_MIN = 2018
FW_FYE_MAX = 2024

# share_status codes in marts.fw_metric. Only 'ok' has a share; every other code means "not available".
SHARE_STATUS = {
    "ok": "share available",
    "fw_unknown": "F&W amount not available",
    "denominator_unknown": "audited spending not available",
    "denominator_not_positive": "audited spending is zero or less",
    "share_over_100": "F&W is larger than audited spending, so one figure is likely incomplete",
}

# The share is percentage points cut (not rounded) to this many decimal places (CHG-2026-057 documented calculation).
SHARE_PLACES = 4
