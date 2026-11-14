"""Display-only number format (CHG-2026-057).

Use these helpers only for text that a person reads: the public site, the review app,
case packs, and HTML/Markdown/PDF reports. Do not use them in CSV, JSON, database or
public-data/v1 export paths. Those stay as plain machine-readable decimals.

Rules (owner decisions, 13 Nov 2026 19:30 SAST and 14 Nov 2026 16:46 SAST; exact words
are in the private approval record):

- Separators: comma thousands and a point decimal (1,234,567.89; 1,234).
- Two contexts. TABLES (figures that are listed or added up) show the full figure:
  format_rand (R1,234,567.89), format_amount and format_count (1,234). PROSE and
  headline text (sentences, cards, summary lines) may use the readable short form
  format_rand_short (R1.2 m, R3.45 bn). Where the exact value matters in prose (a
  flag's evidence amount, a threshold), use the full figure.
- No rounding in the formatter. A value is shown at its source precision: the digits
  the data holds. Money held in integer cents shows exactly two decimals, because that
  is the data's precision. A value whose precision is set by a documented calculation
  (for example a stored percentage computed to one decimal) is shown at that precision:
  the caller passes it as ``places``, which only pads with zeros and never cuts digits.
  Where a computed value needs fewer digits, the calculation does that, with its own
  documented rule, before it calls a formatter. Only the short form drops digits, and
  only in prose (see format_rand_short).
- Percentages show the precision the data holds: a stored 75.7 shows as 75.7%, not
  75.70%; a stored share 0.9707 shows as 97.07%.
- Years, dates, financial-year labels, IDs, SHAs, build IDs, change and incident
  numbers, and version numbers are not formatted here and must be left unchanged.
- A negative number takes a leading ASCII hyphen-minus (U+002D). A rand amount puts
  the minus before the R: -R1,234.50. Zero is never signed: -0.0 shows as 0.00 (money)
  or 0.

None, NaN and non-finite values: format_amount and format_count return an empty
string; format_rand and format_rand_short return "unknown"; format_pct and
format_pct_points return None. Callers may then show their own placeholder.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP  # ROUND_HALF_UP: short form only
from math import isfinite

# Column names that hold whole-number counts in review-app and case-pack tables.
COUNT_COLUMNS = frozenset({"awards", "n", "present", "partial", "missing", "flags"})


def is_count_column(col: str) -> bool:
    """True for a table column that holds a count (shown as 1,234). IDs, years and scores are not counts."""
    c = col or ""
    return c in COUNT_COLUMNS or c.endswith(("_n", "_count", "_lines")) or c.startswith("n_")


def _to_decimal(value) -> Decimal | None:
    """The value as an exact Decimal with the digits it holds, or None. No rounding."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float):
        if not isfinite(value):
            return None
        d = Decimal(repr(value))          # shortest repr: the digits the float holds (as JS String(n))
        if d == d.to_integral_value():
            d = d.quantize(Decimal(1))    # 1.0 → 1, as JS shows it
        return d
    try:
        d = value if isinstance(value, Decimal) else Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    return d if d.is_finite() else None


def _parts(value) -> tuple[bool, str, str] | None:
    """(negative, integer digits, fraction digits) at the value's source precision. No rounding."""
    d = _to_decimal(value)
    if d is None:
        return None
    s = f"{abs(d):f}"
    intp, _, frac = s.partition(".")
    return d < 0, intp.lstrip("0") or "0", frac


def _shift(p: tuple[bool, str, str], k: int) -> tuple[bool, str, str]:
    """Move the decimal point k places (k=2: fraction to percent; k=-2: cents to rand). Exact."""
    neg, intp, frac = p
    digits, point = intp + frac, len(intp) + k
    if point <= 0:
        digits, point = "0" * (1 - point) + digits, 1
    if point > len(digits):
        digits += "0" * (point - len(digits))
    return neg, digits[:point].lstrip("0") or "0", digits[point:]


def _render(p: tuple[bool, str, str], places: int = 0) -> str:
    neg, intp, frac = p
    if len(frac) < places:
        frac = frac.ljust(places, "0")
    if set(intp + frac) <= {"0"}:
        neg = False                       # never -0 or -0.00
    body = f"{int(intp):,}" + (f".{frac}" if frac else "")
    return ("-" if neg else "") + body


def format_amount(value, places: int = 0) -> str:
    """Comma thousands, point decimal, at source precision. ``places`` pads with zeros only."""
    p = _parts(value)
    return "" if p is None else _render(p, places)


def format_count(value) -> str:
    """1,234: a count with comma thousands. No decimals are added; none are cut."""
    return format_amount(value)


def _rand_body(cents) -> tuple[bool, str] | None:
    p = _parts(cents)
    if p is None:
        return None
    q = _shift(p, -2)
    body = _render((False,) + q[1:], 2)
    return (q[0] and body.strip("0.,") != ""), body


def format_rand(cents) -> str:
    """Full rand figure from cents, for tables and exact prose: R1,234.56 or -R1,234.50."""
    r = _rand_body(cents)
    if r is None:
        return "unknown"
    neg, body = r
    return ("-R" if neg else "R") + body


def format_rand_short(cents) -> str:
    """Readable short form for prose and headline text: R1.2 m, R3.45 bn.

    Same rule as the public page before CHG-2026-057: a billion or more shows up to two
    decimals and " bn"; a million or more up to one decimal and " m"; trailing zeros are
    dropped. The abbreviation is the one place where digits are dropped; the dropped
    part is rounded half away from zero, as the page's toLocaleString did. Under a
    million, the full figure is shown (no digits dropped). The full figure stays in the
    table (and, on the page, in the hover title).
    """
    p = _parts(cents)
    if p is None:
        return "unknown"
    neg, intp, frac = _shift(p, -2)
    rand = Decimal(intp + ("." + frac if frac else ""))
    for div, places, suffix in ((Decimal(10) ** 9, 2, " bn"), (Decimal(10) ** 6, 1, " m")):
        if rand >= div:
            q = (rand / div).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP).normalize()
            return ("-R" if neg else "R") + f"{q:,f}" + suffix
    return format_rand(cents)


def format_pct(fraction) -> str | None:
    """A stored fraction as a percent at source precision: 0.9707 → '97.07%', 0.5 → '50%'."""
    p = _parts(fraction)
    if p is None:
        return None
    return _render(_shift(p, 2)) + "%"


def format_pct_points(value, places: int = 0) -> str | None:
    """A value already in percentage points: 75.7 → '75.7%'. ``places`` pads only (a calc's precision)."""
    body = format_amount(value, places)
    return f"{body}%" if body else None
