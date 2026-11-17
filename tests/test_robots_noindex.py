"""CHG-2026-063: hide the public site from search engines. CHG-2026-064 variant B: robots.txt allows crawling, so crawlers
can see the noindex meta tag (revert the CHG-2026-064 commit B to get variant A, `Disallow: /`).

GitHub Pages serves this repo from branch `main`, folder `/`, with `.nojekyll` (CI-111). So `robots.txt` at the repo
root is served at https://publicfunds.grokforum.site/robots.txt. These tests check that:
- robots.txt is at the served root, is tracked by git, and has the exact content (variant B: empty `Disallow:`);
- every served HTML document (each tracked .html file with a <head>) has the noindex meta tag;
- the nightly publish code cannot remove robots.txt or change the HTML pages.
"""
import re
import subprocess
from pathlib import Path

from thusa import publish_data as pdx

ROOT = Path(__file__).resolve().parent.parent
ROBOTS = "User-agent: *\nDisallow:\n"      # CHG-2026-064 variant B: empty Disallow (allow all)
META = '<meta name="robots" content="noindex, nofollow">'
SCRIPT = ROOT / "scripts" / "publish-public-data.sh"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _tracked_html() -> list[Path]:
    out = _git("ls-files", "-z", "--", "*.html", "*.htm").stdout
    return [ROOT / n for n in out.split("\0") if n]


def test_robots_txt_exact_content_at_served_root():
    p = ROOT / "robots.txt"
    assert p.is_file()
    assert p.read_bytes() == ROBOTS.encode("ascii")      # exact bytes: no BOM, LF line ends, one final newline


def test_robots_txt_is_tracked_and_not_ignored():
    assert _git("ls-files", "--error-unmatch", "robots.txt").returncode == 0
    assert _git("check-ignore", "-q", "robots.txt").returncode == 1        # 1 = not ignored


def test_pages_serves_the_repo_root_without_jekyll():
    """With .nojekyll, Pages copies files as they are, so Jekyll cannot exclude robots.txt."""
    assert (ROOT / ".nojekyll").is_file()
    assert not (ROOT / "_config.yml").exists()
    assert (ROOT / "CNAME").read_text().strip() == "publicfunds.grokforum.site"


def test_every_served_html_document_has_noindex_meta():
    docs = [p for p in _tracked_html() if re.search(r"<head[\s>]", p.read_text(encoding="utf-8"), re.I)]
    names = {p.relative_to(ROOT).as_posix() for p in docs}
    assert {"index.html", "apps/public-dashboard/index.html"} <= names
    for p in docs:
        head = re.search(r"<head[\s>].*?</head>", p.read_text(encoding="utf-8"), re.I | re.S)
        assert head, p
        assert head.group(0).count(META) == 1, p


def test_publish_script_only_stages_and_commits_public_data():
    """scripts/publish-public-data.sh must only add, commit or restore paths under public-data/ (read, not run)."""
    lines = [l.strip() for l in SCRIPT.read_text(encoding="utf-8").splitlines()]
    git_writes = [l for l in lines if re.search(r"\bgit (add|commit|checkout|rm|clean|reset|restore|mv)\b", l)]
    assert git_writes, "expected git add/commit lines in the publish script"
    for l in git_writes:
        assert re.search(r"\bgit (rm|clean|reset|restore|mv)\b", l) is None, l
        assert re.search(r"-- public-data/", l), l
    assert not any(re.search(r"\brm\b|robots|index\.html", l) for l in lines if not l.startswith("#")), \
        "the publish script must not delete files or touch robots.txt or HTML pages"


def test_export_leaves_robots_and_html_alone(paths, tmp_path):
    """pf publish-data writes only into public-data/v1 and only deletes stale *.json files there."""
    site = tmp_path / "site"
    out = site / "public-data" / "v1"
    out.mkdir(parents=True)
    (site / "robots.txt").write_text(ROBOTS)
    (site / "index.html").write_text(f"<html><head>{META}</head></html>")
    (out / "robots.txt").write_text(ROBOTS)                # a non-JSON file next to the data must survive too
    (out / "stale.json").write_text("{}")
    before = {p: p.read_bytes() for p in (site / "robots.txt", site / "index.html", out / "robots.txt")}
    pdx.export(paths, out)
    assert {p: p.read_bytes() for p in before} == before
    assert not (out / "stale.json").exists()               # the stale-file clean-up still works
