"""CHG-2026-067: DRAFT label, privacy and contact notice, meta CSP and referrer, ?data= same-origin rule, freshness pill.

The site pages are the HTML pages of the public site: the stub, the dashboard, 404.html and privacy/index.html.
Each check is a function that returns the problems it finds, so the must-fail cases run the same check on a bad copy.
"""
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"index.html": ROOT / "index.html", "apps/public-dashboard/index.html": ROOT / "apps/public-dashboard/index.html",
         "404.html": ROOT / "404.html", "privacy/index.html": ROOT / "privacy/index.html"}
APP = PAGES["apps/public-dashboard/index.html"]
PRIVACY = PAGES["privacy/index.html"]
SITE_DOMAIN = (ROOT / "CNAME").read_text().strip()
BANNER = ("<strong>DRAFT.</strong> This site is a draft. It is built only from the public record: official published data, "
          "shown as found, with each source cited.")
ROBOTS = '<meta name="robots" content="noindex, nofollow">'
REFERRER = '<meta name="referrer" content="no-referrer">'
PRIVACY_SECTIONS = ["1. What this site is", "2. What data it shows", "3. Purpose and basis", "4. What the site does not do",
                    "5. Corrections and removal", "6. How long data stays", "7. Who is responsible", "8. Your rights"]
PERSONAL_MAIL = {"gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com", "icloud.com",
                 "me.com", "proton.me", "protonmail.com", "aol.com", "gmx.com", "mweb.co.za", "webmail.co.za"}
ROLE_WORDS = {"privacy", "contact", "info", "data", "corrections", "dpo", "popia", "enquiries", "hello", "team"}
ISSUE_FORM = re.compile(r"github\.com/[^\"'\s]*/issues/new|ISSUE_TEMPLATE|template=data-error", re.I)


def _head(html: str) -> str:
    m = re.search(r"<head[\s>].*?</head>", html, re.I | re.S)
    return m.group(0) if m else ""


def _csp(html: str) -> str | None:
    m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html)
    return m.group(1) if m else None


def page_problems(html: str) -> list[str]:
    p = []
    if BANNER not in html:
        p.append("no DRAFT banner")
    if not re.search(r'<div class="draft" role="note"><p><strong>DRAFT\.</strong>[^<]*<a href="/privacy/">Privacy and contact</a></p></div>', html):
        p.append("the DRAFT banner has no Privacy and contact link")
    head = _head(html)
    if head.count(ROBOTS) != 1:
        p.append(f"robots meta tag {head.count(ROBOTS)} times")
    if not _csp(head):
        p.append("no CSP meta tag")
    if head.count(REFERRER) != 1:
        p.append("no referrer meta tag")
    if not re.search(r"<title>DRAFT · ", head):
        p.append("title has no DRAFT prefix")
    if ISSUE_FORM.search(html):
        p.append("links to a GitHub issue form")
    return p


def contact_problems(addr: str, site_domain: str = SITE_DOMAIN) -> list[str]:
    p = []
    m = re.fullmatch(r"([^@\s]+)@([^@\s]+)", addr)
    if not m:
        return ["not an e-mail address"]
    local, domain = m.group(1).lower(), m.group(2).lower()
    if domain in PERSONAL_MAIL:
        p.append("personal mail domain")
    if domain != site_domain.lower():
        p.append("not on the site's own domain")
    if local not in ROLE_WORDS:
        p.append("local part is not a role word")
    return p


def csp_problems(csp: str | None) -> list[str]:
    if not csp:
        return ["no CSP"]
    d = {k: v for k, _, v in (x.strip().partition(" ") for x in csp.split(";") if x.strip())}
    p = []
    if d.get("connect-src") != "'self'":
        p.append(f"connect-src is {d.get('connect-src')!r}, not 'self' only")
    for k in ("base-uri", "form-action", "object-src"):
        if d.get(k) != "'none'":
            p.append(f"{k} is not 'none'")
    if d.get("default-src") != "'self'":
        p.append("default-src is not 'self'")
    if re.search(r"https?:|127\.0\.0\.1|localhost", csp):
        p.append("CSP allows another origin")
    return p


# ------------------------------------------------------------------ every site page
@pytest.mark.parametrize("name", sorted(PAGES))
def test_every_site_page_has_draft_banner_privacy_link_and_meta_tags(name):
    html = PAGES[name].read_text(encoding="utf-8")
    assert page_problems(html) == [], name


def test_new_pages_are_not_git_ignored():
    """The repo ignores *.html except named files; the two new site pages must be committable (and so served)."""
    for name in ("404.html", "privacy/index.html"):
        assert subprocess.run(["git", "check-ignore", "-q", name], cwd=ROOT).returncode == 1, f"{name} is git-ignored"


@pytest.mark.parametrize("mutate,expect", [
    (lambda h: h.replace(BANNER, ""), "no DRAFT banner"),
    (lambda h: h.replace('<a href="/privacy/">Privacy and contact</a></p></div>', "</p></div>", 1), "no Privacy and contact link"),
    (lambda h: h.replace(ROBOTS, ROBOTS + "\n" + ROBOTS, 1), "robots meta tag 2 times"),
    (lambda h: h.replace(REFERRER, ""), "no referrer meta tag"),
    (lambda h: h.replace("<title>DRAFT · ", "<title>"), "title has no DRAFT prefix"),
    (lambda h: h.replace("</body>", '<a href="https://github.com/example/repo/issues/new?template=data-error.yml">Report</a></body>'),
     "links to a GitHub issue form"),
])
@pytest.mark.parametrize("name", sorted(PAGES))
def test_must_fail_page_copies(name, mutate, expect):
    bad = mutate(PAGES[name].read_text(encoding="utf-8"))
    probs = page_problems(bad)
    assert probs, (name, expect)
    if expect.startswith("no Privacy"):
        assert any("Privacy and contact" in x for x in probs)
    else:
        assert expect in probs, (name, probs)


def test_noscript_note_dashboard_title_prefix_and_footer_links():
    html = APP.read_text(encoding="utf-8")
    assert re.search(r'<div id="view"[^>]*>.*?<noscript><p>The interactive views need JavaScript\. The open data is at '
                     r'<a href="\.\./\.\./public-data/v1/manifest\.json">', html, re.S)
    assert 'document.title = "DRAFT · " + title + " · PublicFunds SA";' in html
    for meta in ("og:title", "twitter:title"):
        assert re.search(rf'"{meta}" content="DRAFT · ', html), meta
    foot = re.search(r"<footer>.*?</footer>", html, re.S).group(0)
    assert '<a href="/privacy/">Privacy and contact</a>' in foot
    assert "Statistics South Africa (via the IMF and the OECD)" in foot and "(via the OECD)" not in foot.replace("IMF and the OECD", "")
    assert ('0800 701 701 (<a href="https://www.gov.za/faq/justice-and-crime-prevention/how-do-i-report-fraud-or-corruption-'
            'state-department-or-state">source: gov.za</a>)') in foot
    banner_at = html.index('<div class="draft" role="note">')
    assert html.index('<a class="skip" href="#main">') < banner_at < html.index("<header>")


def test_stub_metadata():
    html = PAGES["index.html"].read_text(encoding="utf-8")
    assert '<html lang="en-ZA">' in html
    assert '<meta property="og:url" content="https://publicfunds.grokforum.site/apps/public-dashboard/">' in html
    assert '<meta http-equiv="refresh" content="0; url=apps/public-dashboard/">' in html     # check_live site.home
    assert _csp(html) == "default-src 'none'; img-src data:; base-uri 'none'; form-action 'none'"   # data: for the inline favicon only


def test_404_links_are_absolute():
    html = PAGES["404.html"].read_text(encoding="utf-8")
    hrefs = re.findall(r'href="([^"]+)"', html)
    assert "/apps/public-dashboard/" in hrefs and "/privacy/" in hrefs and "Page not found" in html
    bad = [h for h in hrefs if not (h.startswith("/") or h.startswith("https://") or h.startswith("data:"))]
    assert bad == [], bad
    assert page_problems(html.replace('href="/privacy/"', 'href="privacy/"')) != []      # must fail: relative privacy link


# ------------------------------------------------------------------ CSP
def test_dashboard_csp_is_same_origin_only():
    assert csp_problems(_csp(APP.read_text(encoding="utf-8"))) == []
    for name in ("404.html", "privacy/index.html"):
        csp = _csp(PAGES[name].read_text(encoding="utf-8"))
        assert csp_problems(csp) == [] and "script-src 'none'" in csp, name


@pytest.mark.parametrize("bad", [
    "default-src 'self'; connect-src 'self' https:; base-uri 'none'; form-action 'none'; object-src 'none'",
    "default-src 'self'; connect-src 'self' http://127.0.0.1:*; base-uri 'none'; form-action 'none'; object-src 'none'",
    "default-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'",
    None])
def test_must_fail_csp(bad):
    assert csp_problems(bad)


# ------------------------------------------------------------------ privacy page
def test_privacy_page_sections_party_contact_and_regulator():
    html = PRIVACY.read_text(encoding="utf-8")
    heads = re.findall(r"<h2>(.*?)</h2>", html)
    assert heads == PRIVACY_SECTIONS
    assert "The responsible party is GrokForum." in html
    assert "<strong>[legal wording unverified]</strong>" in html
    assert html.count("[unverified]") == 0 and html.count("unverified") == 1      # only on the legal-basis wording
    assert re.search(r'<a href="https://inforegulator\.org\.za/">Information Regulator \(South Africa\)</a>', html)
    mails = set(re.findall(r'href="mailto:([^"?]+)"', html))
    assert len(mails) == 1, mails
    assert contact_problems(mails.pop()) == []
    assert 'href="/apps/public-dashboard/"' in html
    assert "<script" not in html.lower()


RIGHTS = {"access": "You can ask whether we hold information about you, and ask for a copy of it, by e-mail to",
          "correction and objection": "You can ask for a correction of your information, or object to its processing, by e-mail to",
          "complaint": "You can also complain to the <a href=\"https://inforegulator.org.za/\">Information Regulator (South Africa)</a>."}


def rights_problems(html: str) -> list[str]:
    """POPIA s18 rights in section 8: access, correction and objection through the role mailbox, and a complaint to the
    Information Regulator."""
    m = re.search(r'<section id="rights">(.*?)</section>', html, re.S)
    if not m:
        return ["no rights section"]
    sec = m.group(1)
    p = [f"no {k} right" for k, text in RIGHTS.items() if text not in sec]
    for k in ("access", "correction and objection"):
        if RIGHTS[k] in sec and not re.search(re.escape(RIGHTS[k]) + r' <a href="mailto:[^"]+">', sec):
            p.append(f"the {k} right has no role mailbox link")
    return p


def test_privacy_page_rights_include_access():
    assert rights_problems(PRIVACY.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("right", sorted(RIGHTS))
def test_must_fail_privacy_page_without_a_right(right):
    html = PRIVACY.read_text(encoding="utf-8").replace(RIGHTS[right], "")
    assert f"no {right} right" in rights_problems(html)


def test_must_fail_access_right_without_the_mailbox():
    html = PRIVACY.read_text(encoding="utf-8").replace(RIGHTS["access"] + " <a href=\"mailto:", RIGHTS["access"] + " <a href=\"https://example.org/", 1)
    assert "the access right has no role mailbox link" in rights_problems(html)


def test_must_fail_privacy_page_without_responsible_party():
    html = PRIVACY.read_text(encoding="utf-8").replace("GrokForum", "Example Org")
    assert "The responsible party is GrokForum." not in html


@pytest.mark.parametrize("addr,why", [
    ("privacy@example.org", "not on the site's own domain"),
    ("privacy@gmail.com", "personal mail domain"),
    ("jane.doe@publicfunds.grokforum.site", "local part is not a role word"),
    ("jdoe@publicfunds.grokforum.site", "local part is not a role word"),
    ("privacy@outlook.com", "personal mail domain"),
])
def test_must_fail_contact_addresses(addr, why):
    assert why in contact_problems(addr)


def test_no_site_page_links_an_issue_form():
    for name, p in PAGES.items():
        assert not ISSUE_FORM.search(p.read_text(encoding="utf-8")), name


# ------------------------------------------------------------------ node blocks
def _node(block: str, expr: str, payload) -> object:
    if not shutil.which("node"):
        if os.environ.get("PF_SKIP_NODE_PARITY") == "1":
            pytest.skip("PF_SKIP_NODE_PARITY=1 and node is not installed: the page code was NOT checked")
        pytest.fail("node is not installed, so the page code was NOT checked")
    src = APP.read_text(encoding="utf-8")
    b, e = f"/* {block}:begin */", f"/* {block}:end */"
    assert src.count(b) == 1 and src.count(e) == 1, f"{block} markers not found exactly once"
    js = src[src.index(b) + len(b):src.index(e)]
    js += f"\nconst d = JSON.parse(require('fs').readFileSync(0, 'utf8')); console.log(JSON.stringify({expr}));"
    r = subprocess.run(["node", "-e", js], input=json.dumps(payload), capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


PAGE = "https://publicfunds.grokforum.site/apps/public-dashboard/?data=x"
DEFAULT = "https://publicfunds.grokforum.site/public-data/v1/"


def test_data_base_same_origin_and_default():
    cases = [None, "", "/public-data/v1/", "../../public-data/v1", "https://publicfunds.grokforum.site/public-data/v2/"]
    got = _node("database", "d.map(v => dataBase(v, '" + PAGE + "'))", cases)
    assert got == [DEFAULT, DEFAULT, DEFAULT, DEFAULT, "https://publicfunds.grokforum.site/public-data/v2/"]
    local = _node("database", "dataBase(d, 'http://127.0.0.1:8000/apps/public-dashboard/index.html')", "http://127.0.0.1:8000/public-data/v1/")
    assert local == "http://127.0.0.1:8000/public-data/v1/"           # README local example: same origin, still works


@pytest.mark.parametrize("bad", ["https://evil.example/", "//evil.example/", "http://127.0.0.1:9/", "javascript:alert(1)",
                                 "data:,x", "http://publicfunds.grokforum.site/public-data/v1/"])
def test_must_fail_data_base_other_origins_are_ignored(bad):
    assert _node("database", "dataBase(d, '" + PAGE + "')", bad) == DEFAULT


# The three audit rows of the 18 Nov 2026 manifest (build B20261118T012055Z), with "now" = its generated time.
NOW = "2026-11-18T03:23:00+02:00"
AUDIT_ROWS = [
    {"id": "muni_api", "last_run_status": "unchanged", "last_new_data_sast": "2026-10-23T03:05:05+02:00",
     "last_checked_sast": "2026-11-18T03:19:47+02:00", "freshness_slo_days": 7},
    {"id": "nt_budget", "last_run_status": "unchanged", "last_new_data_sast": "2026-10-19T09:38:04+02:00",
     "last_checked_sast": "2026-11-18T03:20:46+02:00", "freshness_slo_days": 10},
    {"id": "rsr", "last_run_status": "unchanged", "last_new_data_sast": "2026-10-19T09:37:48+02:00",
     "last_checked_sast": "2026-11-18T03:20:38+02:00", "freshness_slo_days": 8},
]


def _fresh(rows):
    now_ms = int(datetime.fromisoformat(NOW).timestamp() * 1000)
    return _node("fresh", f"d.map(s => [freshPill(s, {now_ms}), noNewDataNote(s, {now_ms})])", rows)


def test_freshness_audit_rows_are_checked_not_stale():
    for (pill, note), row in zip(_fresh(AUDIT_ROWS), AUDIT_ROWS):
        assert pill == {"cls": "ok", "text": "checked 18 Nov 2026"}, row["id"]
        assert note and note.startswith("no new data from the source since "), row["id"]
    agsa = {"id": "agsa_annexures", "last_run_status": "unchanged", "last_new_data_sast": "2026-10-20T08:05:11+02:00",
            "last_checked_sast": "2026-10-20T08:05:11+02:00", "freshness_slo_days": 400}
    assert _fresh([agsa])[0] == [{"cls": "ok", "text": "checked 20 Oct 2026"}, None]        # F-11: true date, within 400 days


def test_must_fail_freshness_cases():
    base = dict(AUDIT_ROWS[0])
    stale = base | {"last_checked_sast": "2026-11-01T03:00:00+02:00"}
    unchecked = base | {"last_checked_sast": None}
    failed = base | {"last_run_status": "failed"}
    blocked = base | {"last_run_status": "blocked"}
    no_target = base | {"freshness_slo_days": None}
    got = [p for p, _ in _fresh([stale, unchecked, failed, blocked, no_target])]
    assert got[0] == {"cls": "bad", "text": "stale: last checked 01 Nov 2026 (target 7 days)"}
    assert got[1] == {"cls": "mid", "text": "not checked yet"}
    assert got[2] == got[3] == {"cls": "bad", "text": "last check failed"}
    assert got[4] == {"cls": None, "text": "no target"}


def test_overall_freshness_pill_unchanged():
    html = APP.read_text(encoding="utf-8")
    assert '"older than our 48-hour target"' in html and "gen != null && gen > 2" in html


# ------------------------------------------------------------------ labels (F-04, F-06)
def test_http_audit_links_labelled_and_counts_labels():
    html = APP.read_text(encoding="utf-8")
    assert '"report (http, official link)"' in html
    assert "Official link as published by Municipal Money. The HTTPS form of this address does not serve the file." in html
    assert "municipalities and districts in the records: ${intg(ctr.municipalities_current)} exist now, " \
           "${intg(ctr.municipalities_ceased)} have an end date in the source data" in html
    assert "municipalities with core data due, ${fyLabel(c.fye_min)}" in html
