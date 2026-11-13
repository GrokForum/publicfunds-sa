"""Display-only number format (CHG-2026-057).

Use these helpers only for text that a person reads: the public site, the review app,
case packs, and HTML/Markdown/PDF reports. Do not use them in CSV, JSON, database or
public-data/v1 export paths. Those stay as plain machine-readable decimals.

Rules (open question in CHG-2026-057, for the owner to confirm):
- Money and measured amounts (rands, c/l, the numeric part of a percentage, rates):
  1,234,567.89 — comma thousands, point decimal, exactly two decimals.
- Whole-number counts (flags, rows, entities, cells): 1,234 — no decimals.
- Years, dates, financial-year labels, IDs, SHAs, build IDs, change and incident
  numbers, and version numbers are not formatted here and must be left unchanged.

Rounding is Decimal ROUND_HALF_UP (half away from zero). Example: 1.225 → 1.23,
-1.225 → -1.23. This is not banker's rounding (ROUND_HALF_EVEN).

A negative number takes a leading ASCII hyphen-minus (U+002D). A rand amount puts
the minus before the R: -R1,234.50. Parentheses and en-dashes are not used.

None, NaN and non-finite values: format_amount and format_count return an empty
string; format_rand returns "unknown"; format_pct returns None. Callers may then
show their own placeholder.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import isfinite

_TWO = Decimal("0.01")
_ONE = Decimal("1")
_HUNDRED = Decimal("100")


def _decimal(value) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float) and not isfinite(value):
        return None
    try:
        d = Decimal(str(value)) if isinstance(value, float) else Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not d.is_finite():
        return None
    return d


def format_amount(value) -> str:
    """1,234,567.89 — two decimals, comma thousands, point decimal."""
    d = _decimal(value)
    if d is None:
        return ""
    q = d.quantize(_TWO, rounding=ROUND_HALF_UP)
    return f"{q:,.2f}"


def format_count(value) -> str:
    """1,234 — a whole number with comma thousands and no decimals."""
    d = _decimal(value)
    if d is None:
        return ""
    q = d.quantize(_ONE, rounding=ROUND_HALF_UP)
    return f"{q:,.0f}"


def format_rand(cents) -> str:
    """Rand from integer (or exact) cents: R1,234.56 or -R1,234.50. None → 'unknown'."""
    d = _decimal(cents)
    if d is None:
        return "unknown"
    amount = (d / _HUNDRED).quantize(_TWO, rounding=ROUND_HALF_UP)
    body = format_amount(abs(amount))
    if not body:
        return "unknown"
    return f"-R{body}" if amount < 0 else f"R{body}"


def format_pct(fraction) -> str | None:
    """A fraction (0.757) as a percentage string ('75.70%'). None → None."""
    d = _decimal(fraction)
    if d is None:
        return None
    body = format_amount(d * _HUNDRED)
    return f"{body}%" if body else None


def format_pct_parts(complete, applicable) -> str:
    """complete/applicable as a percentage with two decimals, half-up, integer arithmetic.

    Matches the public-page helper (CHG-2026-057). The result is only the numeric
    part, for example '90.82', so the caller can add '%'.
    """
    d_c, d_a = _decimal(complete), _decimal(applicable)
    if d_c is None or d_a is None or d_a == 0:
        return ""
    # Scale to hundredths of a percent, then half-up: floor(10000*c/a + 1/2).
    hundredths = (20000 * d_c + d_a) // (2 * d_a)
    return format_amount(hundredths / _HUNDRED)
