"""CHG-2026-070 (CHG-2026-069 step S11): the site-repository publish helper, thusa/site_repo.py.

Temporary local git repositories only: a data repository with the site pages and public-data/v1, and a bare
repository that stands in for the site repository. No network, no GitHub, no publish script.
The titled value used here is made up for the test; the private list is never read by the tests.
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

from thusa import site_repo as sr

ROOT = Path(__file__).resolve().parent.parent
FAKE_TITLED = "Dr Qzxv Testperson"           # made up; masks to D*****n
COLS = ['ocid', 'award_id', 'date', 'date_basis', 'buyer', 'supplier', 'value', 'value_note', 'reference', 'method',
        'category', 'doc', 'src']


def git(cwd, *args, env=None, input_bytes=None):
    e = {**os.environ, **sr.IDENTITY, **(env or {})}
    p = subprocess.run(["git", *args], cwd=str(cwd), env=e, capture_output=True, input=input_bytes)
    assert p.returncode == 0, p.stderr.decode()
    return p.stdout.decode().strip()


def award_file(supplier="Example Supplies (Pty) Ltd", doc="x.pdf"):
    row = ["ocds-1", "1", "2024-01-01", "release", "281", supplier, 100.0, None, "R1", "open", "goods", doc, "abc"]
    return {"schema": 1, "kind": "awards", "year": 2024, "columns": COLS, "rows": [row]}


def write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))


@pytest.fixture
def env(tmp_path):
    """A data repository on main (origin URL of the data repository, never contacted), a site bare repository with a
    first published tip, the recorded tip file and a private list file, all under tmp_path."""
    data = tmp_path / "data"
    data.mkdir()
    git(data, "init", "-q", "-b", "main")
    pages = {"index.html": "<html><head></head><body>stub</body></html>\n",
             "apps/public-dashboard/index.html": "<html><body><a href=\"/privacy/\">privacy</a></body></html>\n",
             "apps/public-dashboard/og-card.png": b"\x89PNG\r\n\x1a\nfake",
             "apps/public-dashboard/README.md": "not published\n",
             "apps/public-dashboard/GROK_BUILD_PROMPT.md": "not published\n",
             "robots.txt": "User-agent: *\nDisallow: /\n", ".nojekyll": "",
             "privacy/index.html": "<html><body>privacy@grokforum.site</body></html>\n",
             "404.html": "<html><body>not found</body></html>\n",
             "CNAME": "publicfunds.grokforum.site\n", "thusa/x.py": "print(1)\n", "itil/r.md": "record\n",
             "public-data/v1/manifest.json": json.dumps({"build": {"id": "B1"}}),
             "public-data/v1/feed.json": json.dumps({"items": []}),
             "public-data/v1/awards-2024.json": json.dumps(award_file())}
    for n, c in pages.items():
        write(data / n, c)
    git(data, "add", "-A")
    git(data, "commit", "-q", "-m", "data")
    git(data, "remote", "add", "origin", "https://github.com/GrokForum/publicfunds-sa.git")
    site = tmp_path / "site.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(site))
    # first published tip (S3): a root commit without CNAME
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q", "-b", "main")
    write(seed / "index.html", "old\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "first publish")
    git(seed, "push", "-q", str(site), "main:main")
    tip = git(seed, "rev-parse", "HEAD")
    tip_file = tmp_path / "private" / "site-tip"
    write(tip_file, tip + "\n")
    titled = tmp_path / "private" / "titled.txt"
    write(titled, FAKE_TITLED + "\n")
    return {"tmp": tmp_path, "data": data, "site": site, "seed": seed, "tip": tip, "tip_file": tip_file,
            "titled": titled}


def run_publish(e, **kw):
    args = dict(remote=str(e["site"]), tip_file=e["tip_file"], titled_file=e["titled"], guard_remote=False,
                check_data_remote=False, workdir=e["tmp"])
    args.update(kw)
    return sr.publish(e["data"], **args)


def site_main(e):
    return git(e["tmp"], f"--git-dir={e['site']}", "rev-parse", "refs/heads/main")


def cname_commit(e, content: bytes, extra: dict | None = None, mode_exec=False):
    """GitHub's S6 commit on top of the recorded tip: adds CNAME (and, for the bad cases, other files)."""
    git(e["seed"], "pull", "-q", str(e["site"]), "main")
    write(e["seed"] / "CNAME", content)
    for n, c in (extra or {}).items():
        write(e["seed"] / n, c)
    git(e["seed"], "add", "-A")
    if mode_exec:
        git(e["seed"], "update-index", "--chmod=+x", "CNAME")
    git(e["seed"], "commit", "-q", "-m", "Create CNAME")
    git(e["seed"], "push", "-q", str(e["site"]), "main:main")
    return git(e["seed"], "rev-parse", "HEAD")


# ---------------------------------------------------------------------------------------------- source of truth
def test_expected_cname_and_urls():
    assert sr.EXPECTED_CNAME == b"publicfunds.grokforum.site\n"
    assert sr.ACCEPTED_CNAME == (b"publicfunds.grokforum.site", b"publicfunds.grokforum.site\n")
    assert sr.SITE_REMOTE_URL == "https://github.com/GrokForum/publicfunds-site.git"
    assert sr.SITE_RAW_MANIFEST == "https://raw.githubusercontent.com/GrokForum/publicfunds-site/main/public-data/v1/manifest.json"


# ---------------------------------------------------------------------------------------------- guards
@pytest.mark.parametrize("url", ["https://github.com/GrokForum/publicfunds-site.git", "https://github.com/GrokForum/publicfunds-site"])
def test_site_remote_guard_accepts_only_the_site_repo(url):
    sr.check_site_remote(url)


@pytest.mark.parametrize("url", ["https://github.com/GrokForum/publicfunds-sa.git", "https://github.com/other/publicfunds-site.git",
                                 "https://github.com/GrokForum/publicfunds-site.git.evil", "git@github.com:GrokForum/publicfunds-site.git",
                                 "https://user@github.com/GrokForum/publicfunds-site.git", "/tmp/site.git", ""])
def test_site_remote_guard_rejects_anything_else(url):
    with pytest.raises(sr.Blocked, match="site remote guard"):
        sr.check_site_remote(url)


def test_guarded_publish_to_a_local_path_is_blocked(env):
    r = run_publish(env, guard_remote=True)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (site remote guard: the push URL is not GrokForum/publicfunds-site)"
    assert site_main(env) == env["tip"]


def test_data_origin_guard_and_main_check(env):
    git(env["data"], "remote", "set-url", "origin", "https://github.com/someone/else.git")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (account or origin check failed (data repository))"
    git(env["data"], "remote", "set-url", "origin", "https://github.com/GrokForum/publicfunds-sa.git")
    git(env["data"], "checkout", "-q", "-b", "other")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (not on main)"
    assert site_main(env) == env["tip"]


def test_data_push_not_finished_is_blocked(env, monkeypatch):
    real = sr._git
    remote = {"sha": "f" * 40}

    def fake(*args, **kw):
        if args[:1] == ("ls-remote",) and args[1] == "origin":          # the data repository: never contacted
            return subprocess.CompletedProcess(args, 0, f"{remote['sha']}\trefs/heads/main\n".encode(), b"")
        return real(*args, **kw)
    monkeypatch.setattr(sr, "_git", fake)
    r = run_publish(env, check_data_remote=True)
    assert r.code == 3 and r.lines[0] == ("ACTION: site publish blocked (data push not finished: remote main of the data "
                                          "repository is not the local HEAD)")
    assert site_main(env) == env["tip"]
    remote["sha"] = git(env["data"], "rev-parse", "HEAD")
    assert run_publish(env, check_data_remote=True).code == 0


@pytest.mark.parametrize("which,content,word", [
    ("titled", None, "PF_TITLED_VALUES_FILE is not set"),
    ("titled", "\n# comment\n\n", "the private list is empty"),
    ("tip", None, "PF_SITE_TIP_FILE is not set"),
    ("tip", "abc\n", "does not hold one 40-hex commit id"),
])
def test_missing_private_inputs_block(env, which, content, word):
    if content is None:
        kw = {"titled_file": None} if which == "titled" else {"tip_file": None}
    else:
        write(env[which if which == "titled" else "tip_file"], content)
        kw = {}
    r = run_publish(env, **kw)
    assert r.code == 3 and word in r.lines[0] and r.lines[0].startswith("ACTION: site publish blocked (")
    assert site_main(env) == env["tip"]


# ---------------------------------------------------------------------------------------------- staging and allowlist
def test_staging_holds_only_the_allowlist_and_the_expected_cname(env, tmp_path):
    head = git(env["data"], "rev-parse", "HEAD")
    write(env["data"] / "CNAME", "wrong.example\n")          # the data-repo CNAME is never copied
    git(env["data"], "commit", "-qam", "cname changed")
    head = git(env["data"], "rev-parse", "HEAD")
    st = tmp_path / "st"
    files = sr.build_staging(env["data"], head, st)
    assert files == sorted([".nojekyll", "404.html", "CNAME", "apps/public-dashboard/index.html",
                            "apps/public-dashboard/og-card.png", "index.html", "privacy/index.html", "robots.txt",
                            "public-data/v1/awards-2024.json", "public-data/v1/feed.json", "public-data/v1/manifest.json"])
    assert (st / "CNAME").read_bytes() == b"publicfunds.grokforum.site\n"
    assert (st / "apps/public-dashboard/og-card.png").read_bytes() == b"\x89PNG\r\n\x1a\nfake"
    assert sr.allowlist_problems(st) == []


def test_staging_works_when_the_data_repo_has_no_cname(env, tmp_path):
    git(env["data"], "rm", "-q", "CNAME")
    git(env["data"], "commit", "-qm", "no cname")
    st = tmp_path / "st"
    sr.build_staging(env["data"], git(env["data"], "rev-parse", "HEAD"), st)
    assert (st / "CNAME").read_bytes() == sr.EXPECTED_CNAME and sr.allowlist_problems(st) == []


@pytest.mark.parametrize("extra", ["apps/public-dashboard/README.md", "apps/public-dashboard/GROK_BUILD_PROMPT.md",
                                   "thusa/x.py", "itil/r.md", "public-data/v2/x.json", "uv.lock", "public-data/v1"])
def test_allowlist_fails_on_any_other_file(env, tmp_path, extra):
    st = tmp_path / "st"
    sr.build_staging(env["data"], git(env["data"], "rev-parse", "HEAD"), st)
    if extra == "public-data/v1":
        (st / "public-data/v1").rename(st / "pd")            # required data files missing
        problems = sr.allowlist_problems(st)
        assert any(p.startswith("missing: public-data/v1/") for p in problems)
        return
    write(st / extra, "x")
    assert sr.allowlist_problems(st) == [f"not on the allowlist: {extra}"]


def test_allowlist_fails_on_wrong_cname_bytes_and_symlinks(env, tmp_path):
    st = tmp_path / "st"
    sr.build_staging(env["data"], git(env["data"], "rev-parse", "HEAD"), st)
    write(st / "CNAME", "publicfunds.grokforum.site\r\n")
    assert sr.allowlist_problems(st) == ["CNAME bytes differ from the expected domain"]
    write(st / "CNAME", sr.EXPECTED_CNAME)
    (st / "public-data/v1/link.json").symlink_to(st / "index.html")
    assert sr.allowlist_problems(st) == ["symlink not allowed: public-data/v1/link.json"]


# ---------------------------------------------------------------------------------------------- mask scan and POPIA
@pytest.mark.parametrize("supplier,doc,word", [
    (FAKE_TITLED, None, "private list value found"),                          # unmasked value, exact
    (FAKE_TITLED.upper(), None, "private list value found"),                  # case-insensitive
    ("Prof Someone Else", None, "titled-person rule"),                       # the titled-person rule, not on the list
    ("D*****n", "x.pdf", "masked supplier row still has a doc link"),       # masked row must have doc null
])
def test_mask_scan_failure_blocks_the_push(env, supplier, doc, word):
    write(env["data"] / "public-data/v1/awards-2024.json", json.dumps(award_file(supplier, doc)))
    git(env["data"], "commit", "-qam", "unmasked")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (mask scan)"
    assert any(word in l for l in r.lines)
    assert not any(FAKE_TITLED.lower() in l.lower() for l in r.lines)     # the report never shows the value
    assert site_main(env) == env["tip"]


def test_masked_rows_pass_the_mask_scan(env, tmp_path):
    write(env["data"] / "public-data/v1/awards-2024.json", json.dumps(award_file("D*****n", None)))
    git(env["data"], "commit", "-qam", "masked")
    st = tmp_path / "st"
    sr.build_staging(env["data"], git(env["data"], "rev-parse", "HEAD"), st)
    assert sr.mask_problems(st, [FAKE_TITLED]) == []


def test_mask_scan_covers_the_site_pages(env):
    write(env["data"] / "index.html", f"<html><body>{FAKE_TITLED.lower()}</body></html>\n")
    git(env["data"], "commit", "-qam", "page")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (mask scan)"
    assert "site_publish:   private list value found in index.html" in r.lines


@pytest.mark.parametrize("path,content,word", [
    ("privacy/index.html", "<p>mail someone@gmail.com</p>", "e-mail address that is not a role mailbox"),
    ("404.html", "<p>call 082 555 1234</p>", "phone number"),
    ("public-data/v1/feed.json", json.dumps({"items": [{"text": "8001015009087"}]}), "SA-ID-like number"),
    ("public-data/v1/feed.json", json.dumps({"items": [{"username": "x"}]}), "forbidden key"),
    ("robots.txt", "User-agent: *\nDisallow: /\n# 8001015009087\n", "SA-ID-like number"),
])
def test_popia_failure_blocks_the_push(env, path, content, word):
    write(env["data"] / path, content)
    git(env["data"], "commit", "-qam", "popia")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (POPIA)"
    assert any(word in l for l in r.lines)
    assert site_main(env) == env["tip"]


def test_popia_check_passes_the_role_mailbox(env, tmp_path):
    st = tmp_path / "st"
    sr.build_staging(env["data"], git(env["data"], "rev-parse", "HEAD"), st)
    assert sr.popia_problems(st) == []


# ---------------------------------------------------------------------------------------------- gate 8 and the push
def test_recorded_tip_is_accepted_and_the_push_is_a_fast_forward(env):
    r = run_publish(env)
    assert r.code == 0, r.lines
    new = site_main(env)
    assert r.lines[-1] == f"site_publish: pushed {new}"
    assert git(env["tmp"], f"--git-dir={env['site']}", "rev-parse", f"{new}^") == env["tip"]   # option a: one parent
    assert env["tip_file"].read_text() == new + "\n"                                          # recorded privately
    assert oct(env["tip_file"].stat().st_mode & 0o777) == "0o600"
    names = git(env["tmp"], f"--git-dir={env['site']}", "ls-tree", "-r", "--name-only", new).splitlines()
    assert "CNAME" in names and "thusa/x.py" not in names and "apps/public-dashboard/README.md" not in names
    assert git(env["tmp"], f"--git-dir={env['site']}", "cat-file", "blob", f"{new}:CNAME") == "publicfunds.grokforum.site"
    # the next run sees its own recorded tip and has nothing to push
    r2 = run_publish(env)
    assert r2.code == 0 and r2.lines[-1] == "site_publish: no change; nothing pushed" and site_main(env) == new


def test_pushed_tree_is_exactly_the_scanned_tree(env, tmp_path):
    r = run_publish(env)
    new = site_main(env)
    st = tmp_path / "st"
    sr.build_staging(env["data"], git(env["data"], "rev-parse", "HEAD"), st)
    work = tmp_path / "w.git"
    git(tmp_path, "init", "-q", "--bare", str(work))
    assert r.code == 0 and sr.write_tree(work, st) == git(env["tmp"], f"--git-dir={env['site']}", "rev-parse", f"{new}^{{tree}}")
    # no file of the old tip rides along: the old tip had only index.html with other bytes
    assert git(env["tmp"], f"--git-dir={env['site']}", "cat-file", "blob", f"{new}:index.html").startswith("<html>")


@pytest.mark.parametrize("content", [b"publicfunds.grokforum.site", b"publicfunds.grokforum.site\n"])
def test_tip_plus_one_cname_only_commit_is_accepted(env, content):
    gh = cname_commit(env, content)
    r = run_publish(env)
    assert r.code == 0, r.lines
    new = site_main(env)
    assert git(env["tmp"], f"--git-dir={env['site']}", "rev-parse", f"{new}^") == gh        # built on GitHub's commit
    assert git(env["tmp"], f"--git-dir={env['site']}", "cat-file", "-p", f"{new}:CNAME") == "publicfunds.grokforum.site"
    assert env["tip_file"].read_text().strip() == new


@pytest.mark.parametrize("content,extra,mode_exec", [
    (b"publicfunds.grokforum.site\r\n", None, False),                 # CRLF
    (b"publicfunds.grokforum.site\r", None, False),                   # CR
    (b"publicfunds.grokforum.site\n\n", None, False),                 # two LFs
    (b"other.example\n", None, False),                                # wrong domain
    (b"publicfunds.grokforum.site\nextra\n", None, False),            # extra line
    (b" publicfunds.grokforum.site\n", None, False),                  # leading space
    (b"publicfunds.grokforum.site\n", {"extra.html": "x"}, False),    # an extra file in the same commit
    (b"publicfunds.grokforum.site\n", None, True),                    # executable mode
])
def test_bad_cname_commit_is_rejected(env, content, extra, mode_exec):
    gh = cname_commit(env, content, extra, mode_exec)
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (unexpected remote commit)"
    assert site_main(env) == gh and env["tip_file"].read_text().strip() == env["tip"]


def test_two_commits_on_top_of_the_tip_are_rejected(env):
    cname_commit(env, b"publicfunds.grokforum.site\n")
    write(env["seed"] / "x.txt", "x")
    git(env["seed"], "add", "-A")
    git(env["seed"], "commit", "-qm", "second")
    git(env["seed"], "push", "-q", str(env["site"]), "main:main")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (unexpected remote commit)"


def test_cname_modify_commit_is_rejected(env):
    """Gate 8 accepts only a commit that adds CNAME; a commit that changes an existing CNAME is not accepted."""
    assert run_publish(env).code == 0               # our tip now holds CNAME
    git(env["seed"], "pull", "-q", str(env["site"]), "main")
    write(env["seed"] / "CNAME", b"publicfunds.grokforum.site")
    git(env["seed"], "commit", "-qam", "Update CNAME")
    git(env["seed"], "push", "-q", str(env["site"]), "main:main")
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (unexpected remote commit)"


def test_unknown_tip_is_rejected(env, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    git(other, "init", "-q", "-b", "main")
    write(other / "index.html", "forged\n")
    git(other, "add", "-A")
    git(other, "commit", "-qm", "forged")
    git(other, "push", "-q", "--force", str(env["site"]), "main:main")      # stands in for a remote that was replaced
    forged = site_main(env)
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (unexpected remote commit)"
    assert site_main(env) == forged and env["tip_file"].read_text().strip() == env["tip"]


def test_recorded_tip_that_is_an_older_ancestor_is_rejected(env):
    first = run_publish(env)
    assert first.code == 0
    write(env["tip_file"], env["tip"] + "\n")        # recorded tip is now one commit behind remote main
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (unexpected remote commit)"


def test_remote_without_main_is_blocked(env, tmp_path):
    empty = tmp_path / "empty.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(empty))
    r = run_publish(env, remote=str(empty))
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (unexpected remote commit)"
    assert git(tmp_path, f"--git-dir={empty}", "for-each-ref") == ""


def test_failed_fetch_is_blocked(env, tmp_path):
    r = run_publish(env, remote=str(tmp_path / "missing.git"))
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (fetch failed)"


def test_tree_hash_mismatch_blocks(env, monkeypatch):
    real = sr._git

    def fake(*args, **kw):
        p = real(*args, **kw)
        if args[:1] == ("rev-parse",) and args[1].endswith("^{tree}") and not args[1].startswith(env["tip"]):
            return subprocess.CompletedProcess(p.args, 0, b"0" * 40 + b"\n", b"")
        return p
    monkeypatch.setattr(sr, "_git", fake)
    r = run_publish(env)
    assert r.code == 3 and r.lines[0] == "ACTION: site publish blocked (tree hash mismatch)"
    assert site_main(env) == env["tip"]


def test_refused_push_is_a_failed_publish(env):
    hook = env["site"] / "hooks" / "pre-receive"
    write(hook, "#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    r = run_publish(env)
    assert r.code == 4 and r.lines[0].startswith("ACTION: site publish failed (push refused or failed")
    assert site_main(env) == env["tip"] and env["tip_file"].read_text().strip() == env["tip"]


def test_tip_not_recorded_is_a_failed_publish(env, monkeypatch):
    def boom(path, sha):
        raise OSError("read-only")
    monkeypatch.setattr(sr, "record_tip", boom)
    r = run_publish(env)
    new = site_main(env)
    assert r.code == 4 and r.lines[0] == f"ACTION: site publish failed (pushed {new}, but the tip was not recorded)"


def test_private_bundle_of_the_published_tip(env, tmp_path):
    bdir = tmp_path / "bundles"
    bdir.mkdir()
    r = run_publish(env, bundle_dir=bdir)
    new = site_main(env)
    assert r.code == 0 and (bdir / f"site-{new[:12]}.bundle").is_file()


def test_push_is_never_forced():
    text = (ROOT / "thusa" / "site_repo.py").read_text()
    assert "--force-with-lease" not in text and '"-f"' not in text and "+refs/heads/main\"" not in text.split("push", 1)[1].split("\n", 1)[0]
    push_lines = [l for l in text.splitlines() if '"push"' in l]
    assert len(push_lines) == 1 and "--force" not in push_lines[0] and ":refs/heads/main" in push_lines[0]
    assert "publish-public-data.sh" not in text.split('"""', 2)[2]


def test_cli_takes_no_arguments():
    lines = []
    assert sr.main(["--remote", "/tmp/x"], out=lines.append) == 3
    assert lines == ["ACTION: site publish blocked (this command takes no arguments)"]


def test_no_private_path_or_value_in_the_helper():
    for f in (ROOT / "thusa" / "site_repo.py", ROOT / "scripts" / "publish_site_repo.py"):
        t = f.read_text()
        assert "/home/" not in t and "titled-values" not in t


def test_private_settings_env_first_then_config(tmp_path):
    cfg = tmp_path / "site-publish.json"
    cfg.write_text(json.dumps({"titled_values_file": "/x/list", "tip_file": "/x/tip"}))
    got = sr.private_settings({"PF_SITE_TIP_FILE": "/env/tip"}, cfg)
    assert got == {"PF_TITLED_VALUES_FILE": "/x/list", "PF_SITE_TIP_FILE": "/env/tip", "PF_SITE_BUNDLE_DIR": None}
    assert sr.private_settings({}, tmp_path / "missing.json") == dict.fromkeys(sr.CONFIG_KEYS)
    cfg.write_text("not json")
    assert sr.private_settings({}, cfg) == dict.fromkeys(sr.CONFIG_KEYS)
    assert sr.PRIVATE_CONFIG.parts[-3:] == (".config", "thusa", "site-publish.json")


def test_site_commit_uses_the_neutral_role_identity(env, monkeypatch):
    """Owner decision, 18 Nov 2026: author and committer of a site commit are the neutral role identity."""
    for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(k, "Grok Bot (for the owner)" if k.endswith("NAME") else "grokbot@localhost")
    r = run_publish(env)
    assert r.code == 0, r.lines
    new = site_main(env)
    fmt = git(env["tmp"], f"--git-dir={env['site']}", "log", "-1", "--format=%an|%ae|%cn|%ce", new)
    assert fmt == "PublicFunds publisher|noreply@publicfunds.grokforum.site|PublicFunds publisher|noreply@publicfunds.grokforum.site"
    raw = git(env["tmp"], f"--git-dir={env['site']}", "cat-file", "commit", new)
    assert "grok bot" not in raw.lower() and "grokbot" not in raw.lower()
    assert "Grok Bot" not in (ROOT / "thusa" / "site_repo.py").read_text()
