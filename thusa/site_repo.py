"""CHG-2026-070 (CHG-2026-069 step S11): publish the allowlist site tree to the site repository.

It runs in step 4 of the nightly, after the data push of `scripts/publish-public-data.sh --push` exited 0, and before
`scripts/nightly_check_live.py`. It never runs the data publish script and never pushes the data repository.

    uv run python scripts/publish_site_repo.py > data/site-publish.log 2>&1; echo $?

Order (CHG-2026-069 sections 4.1, 4.2 and 4.4):
  1. Guards: the data checkout is on `main`, its origin is GrokForum/publicfunds-sa, and the data push has finished
     (remote `main` of the data repository is the local HEAD). The site push URL is GrokForum/publicfunds-site.
  2. Build the staging tree from the allowlist (section 3): the listed site pages and every file under
     `public-data/v1/`, all read from the data commit at HEAD, plus the expected `CNAME` (EXPECTED_CNAME).
  3. Gates 3 to 5 on the staging tree: the mask scan (private list, exact and case-insensitive; the titled-person rule;
     a masked row has `doc` null), the POPIA release check, and the allowlist test.
  4. Gate 8: fetch the remote tip of the site repository. Accept only the recorded last tip, or that tip plus exactly
     one commit, with a single parent, that only adds `CNAME` with the expected bytes (one trailing LF allowed).
  5. Option a: `git write-tree` of the scanned staging tree, `git commit-tree <tree> -p <accepted tip>`, check that the
     commit's tree is the scanned tree, push without force, then record the new tip privately.

Private inputs, never in git: PF_TITLED_VALUES_FILE (the private list of titled values, one per line) and
PF_SITE_TIP_FILE (the recorded last tip: one 40-hex commit id). PF_SITE_BUNDLE_DIR (optional) receives a private bundle
of each published tip. If an environment variable is not set, the helper reads the private config file
`~/.config/thusa/site-publish.json` (mode 0600, written at the deploy, never in git), with the keys
`titled_values_file`, `tip_file` and `bundle_dir`. If neither gives a value, the run is blocked.

Output: lines starting `site_publish:`. On a failure the first line is an ACTION line and nothing is pushed:
    ACTION: site publish blocked (<reason>)   exit 3  (a guard or gate failed; nothing was pushed)
    ACTION: site publish failed (<reason>)    exit 4  (the push or the record of the tip failed)
Exit 0 prints `site_publish: pushed <40-hex>` or `site_publish: no change; nothing pushed`.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SITE_REPO = "GrokForum/publicfunds-site"
SITE_DOMAIN = "publicfunds.grokforum.site"
EXPECTED_CNAME = (SITE_DOMAIN + "\n").encode("ascii")           # the bytes this publish writes into the staging tree
ACCEPTED_CNAME = (SITE_DOMAIN.encode("ascii"), EXPECTED_CNAME)    # the bytes gate 8 accepts in GitHub's CNAME commit
SITE_REMOTE_URL = f"https://github.com/{SITE_REPO}.git"
SITE_RAW_MANIFEST = f"https://raw.githubusercontent.com/{SITE_REPO}/main/public-data/v1/manifest.json"
DATA_ORIGIN_RE = re.compile(r"github\.com[:/]GrokForum/publicfunds-sa(\.git)?$")
SITE_REMOTE_RE = re.compile(r"^https://github\.com/GrokForum/publicfunds-site(\.git)?$")

# Section 3 allowlist. Every file under public-data/v1/ is also allowed.
SITE_PAGES = ("index.html", "apps/public-dashboard/index.html", "apps/public-dashboard/og-card.png", "robots.txt",
              ".nojekyll", "privacy/index.html", "404.html")
DATA_PREFIX = "public-data/v1/"
ALLOWLIST = frozenset(SITE_PAGES + ("CNAME",))
REQUIRED = ALLOWLIST | {DATA_PREFIX + "manifest.json", DATA_PREFIX + "feed.json"}

EXIT_OK, EXIT_BLOCKED, EXIT_FAILED = 0, 3, 4
GIT_TIMEOUT_S = 300
IDENTITY = {"GIT_AUTHOR_NAME": "Grok Bot (for the owner)", "GIT_AUTHOR_EMAIL": "grokbot@localhost",
            "GIT_COMMITTER_NAME": "Grok Bot (for the owner)", "GIT_COMMITTER_EMAIL": "grokbot@localhost"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
PHONE_RE = re.compile(r"(?<![\d+])(?:\+27|0)[ -]?\d{2}[ -]?\d{3}[ -]?\d{4}(?!\d)")
ROLE_MAILBOXES = frozenset({"privacy", "contact", "info", "data", "corrections", "dpo", "popia", "enquiries"})


class Blocked(Exception):
    """A guard or gate failed before any push. Nothing was pushed."""


class Failed(Exception):
    """The push, or the record of a pushed tip, failed."""


def _git(*args: str, cwd: Path | None = None, env: dict | None = None, input_bytes: bytes | None = None,
         check: bool = True) -> subprocess.CompletedProcess:
    full_env = {**os.environ, **(env or {}), "GIT_TERMINAL_PROMPT": "0"}
    p = subprocess.run(["git", *args], cwd=str(cwd) if cwd else None, env=full_env, input=input_bytes,
                       capture_output=True, timeout=GIT_TIMEOUT_S)
    if check and p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, ["git", *args], p.stdout, p.stderr)
    return p


def _out(p: subprocess.CompletedProcess) -> str:
    return p.stdout.decode("utf-8", "replace").strip()


# ------------------------------------------------------------------------------------------------ private inputs
def read_titled_values(path: str | os.PathLike | None) -> list[str]:
    """The private list: one value per line; blank lines and lines starting with # are skipped. Empty means blocked."""
    if not path:
        raise Blocked("mask scan cannot run: PF_TITLED_VALUES_FILE is not set")
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        raise Blocked("mask scan cannot run: the private list is not readable") from None
    values = [l.strip() for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not values:
        raise Blocked("mask scan cannot run: the private list is empty")
    return values


def read_recorded_tip(path: str | os.PathLike | None) -> str:
    if not path:
        raise Blocked("no recorded tip: PF_SITE_TIP_FILE is not set")
    try:
        tip = Path(path).read_text(encoding="ascii").strip()
    except (OSError, UnicodeDecodeError):
        raise Blocked("no recorded tip: the tip file is not readable") from None
    if not SHA_RE.fullmatch(tip):
        raise Blocked("no recorded tip: the tip file does not hold one 40-hex commit id")
    return tip


def record_tip(path: str | os.PathLike, sha: str) -> None:
    """Write the new tip atomically, mode 0600."""
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="ascii") as f:
        f.write(sha + "\n")
    os.replace(tmp, p)


# ------------------------------------------------------------------------------------------------ guards
def check_site_remote(url: str) -> None:
    """Gate 6: the site push URL is exactly GrokForum/publicfunds-site."""
    if not SITE_REMOTE_RE.fullmatch(url or ""):
        raise Blocked("site remote guard: the push URL is not GrokForum/publicfunds-site")


def check_data_checkout(root: Path, run_ls_remote: bool = True) -> str:
    """Gates 1 and 2 (the parts this helper can see): on main, data origin guard, data push finished. Returns HEAD."""
    try:
        branch = _out(_git("rev-parse", "--abbrev-ref", "HEAD", cwd=root))
        origin = _out(_git("remote", "get-url", "origin", cwd=root))
        head = _out(_git("rev-parse", "HEAD", cwd=root))
    except (subprocess.SubprocessError, OSError):
        raise Blocked("data checkout cannot be read") from None
    if branch != "main":
        raise Blocked("not on main")
    if not DATA_ORIGIN_RE.search(origin):
        raise Blocked("account or origin check failed (data repository)")
    if run_ls_remote:
        try:
            remote = _out(_git("ls-remote", "origin", "refs/heads/main", cwd=root)).split()
        except (subprocess.SubprocessError, OSError):
            raise Blocked("data push not confirmed: git ls-remote of the data repository failed") from None
        if not remote or remote[0] != head:
            raise Blocked("data push not finished: remote main of the data repository is not the local HEAD")
    return head


# ------------------------------------------------------------------------------------------------ staging
def build_staging(root: Path, commit: str, staging: Path) -> list[str]:
    """Write the allowlist files of `commit` (the data commit) into `staging`, then the expected CNAME.

    Files are read from git, not from the working tree, so the tree is exactly what the data repository holds."""
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    names = _out(_git("ls-tree", "-r", "--name-only", "-z", commit, cwd=root)).split("\0")
    chosen = [n for n in names if n and (n in SITE_PAGES or n.startswith(DATA_PREFIX))]
    for n in chosen:
        blob = _git("cat-file", "blob", f"{commit}:{n}", cwd=root).stdout
        dest = staging / n
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
    (staging / "CNAME").write_bytes(EXPECTED_CNAME)      # before gates 3 to 5 (section 4.1)
    return sorted(chosen + ["CNAME"])


def staging_files(staging: Path) -> list[str]:
    return sorted(p.relative_to(staging).as_posix() for p in staging.rglob("*") if p.is_file() or p.is_symlink())


def allowlist_problems(staging: Path) -> list[str]:
    """Gate 5: only the listed files, all required files present, no symlinks."""
    problems = []
    files = staging_files(staging)
    for f in files:
        if (staging / f).is_symlink():
            problems.append(f"symlink not allowed: {f}")
        elif f not in ALLOWLIST and not (f.startswith(DATA_PREFIX) and len(f) > len(DATA_PREFIX)):
            problems.append(f"not on the allowlist: {f}")
    for f in sorted(REQUIRED - set(files)):
        problems.append(f"missing: {f}")
    if (staging / "CNAME").is_file() and (staging / "CNAME").read_bytes() != EXPECTED_CNAME:
        problems.append("CNAME bytes differ from the expected domain")
    return problems


def mask_problems(staging: Path, titled_values: list[str], official_names=frozenset()) -> list[str]:
    """Gate 3: 0 hits for the private list (exact and case-insensitive) in every file; the titled-person rule and
    `doc` null on masked rows in every award file. Problems name the file only, never the value."""
    from thusa import publish_data as pdx
    problems = []
    folded = [v.casefold() for v in titled_values]
    for f in staging_files(staging):
        data = (staging / f).read_bytes()
        text = data.decode("utf-8", "ignore")
        low = text.casefold()
        if any(v.encode("utf-8") in data for v in titled_values) or any(v in low for v in folded):
            problems.append(f"private list value found in {f}")
        if re.fullmatch(re.escape(DATA_PREFIX) + r"awards-[^/]+\.json", f):
            try:
                pdx.assert_no_titled_supplier({f.rsplit("/", 1)[1][len("awards-"):-len(".json")]: json.loads(text)},
                                              official_names)
            except pdx.UnsafeExport as e:
                problems.append(f"titled-person rule: {e}")
            except (ValueError, KeyError, IndexError, TypeError):
                problems.append(f"titled-person rule cannot run on {f}")
    return problems


def popia_problems(staging: Path, banned_names=frozenset()) -> list[str]:
    """Gate 4, automated part of the release check on the whole staging tree: every JSON file passes the export's
    public-safety check (forbidden keys, SA ID numbers, ID hashes, restricted-register person names); no text file has
    an SA ID number, an e-mail address other than a role mailbox at the site's parent domain, or (pages only) a phone
    number. Problems name the file and the kind of item only."""
    from thusa import publish_data as pdx
    problems = []
    parent = SITE_DOMAIN.split(".", 1)[1]
    for f in staging_files(staging):
        if f.endswith(".png"):
            continue
        text = (staging / f).read_text(encoding="utf-8", errors="replace")
        if f.endswith(".json"):
            try:
                pdx.assert_public_safe(json.loads(text), set(banned_names), f)
            except pdx.UnsafeExport as e:
                problems.append(f"{f}: {str(e).split(' at ')[0]}")
            except ValueError:
                problems.append(f"{f}: not valid JSON")
        elif pdx.looks_like_sa_id(text):
            problems.append(f"{f}: SA-ID-like number")
        for addr in EMAIL_RE.findall(text):
            local, _, dom = addr.lower().partition("@")
            if local not in ROLE_MAILBOXES or dom not in (SITE_DOMAIN, parent):
                problems.append(f"{f}: e-mail address that is not a role mailbox of the site")
                break
        if not f.startswith(DATA_PREFIX) and PHONE_RE.search(text):
            problems.append(f"{f}: phone number")
    return problems


# ------------------------------------------------------------------------------------------------ gate 8
def gate8(work: Path, fetched: str, recorded: str) -> str:
    """Return the accepted tip, or raise Blocked('unexpected remote commit')."""
    if fetched == recorded:
        return fetched
    try:
        parents = _out(_git("rev-list", "--parents", "-n", "1", fetched, cwd=work)).split()[1:]
    except subprocess.SubprocessError:
        raise Blocked("unexpected remote commit") from None
    if parents != [recorded]:
        raise Blocked("unexpected remote commit")
    diff = _out(_git("diff-tree", "-r", "--no-renames", "--no-commit-id", "--raw", recorded, fetched, cwd=work))
    lines = [l for l in diff.splitlines() if l.strip()]
    if len(lines) != 1:
        raise Blocked("unexpected remote commit")
    meta, _, path = lines[0].partition("\t")
    fields = meta.split()
    # ":000000 100644 0000... <blob> A"  -> only an add of a regular file named CNAME at the root
    if path != "CNAME" or len(fields) != 5 or fields[4] != "A" or fields[1] != "100644":
        raise Blocked("unexpected remote commit")
    blob = _git("cat-file", "blob", fields[3], cwd=work).stdout
    if blob not in ACCEPTED_CNAME:
        raise Blocked("unexpected remote commit")
    return fetched


# ------------------------------------------------------------------------------------------------ publish
@dataclass
class Result:
    code: int
    lines: list[str]


def write_tree(work: Path, staging: Path) -> str:
    index = work / "site-publish.index"
    if index.exists():
        index.unlink()
    env = {"GIT_INDEX_FILE": str(index)}
    _git(f"--work-tree={staging}", "add", "-A", "--force", ".", cwd=work, env=env)
    tree = _out(_git("write-tree", cwd=work, env=env))
    index.unlink()
    return tree


def publish(root: Path, *, remote: str, tip_file, titled_file, bundle_dir=None, official_names=frozenset(),
            banned_names=frozenset(), guard_remote: bool = True, check_data_remote: bool = True,
            workdir: Path | None = None, message: str | None = None) -> Result:
    lines: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="site-publish-", dir=workdir))
    try:
        try:
            if guard_remote:
                check_site_remote(remote)
            head = check_data_checkout(root, run_ls_remote=check_data_remote)
            titled = read_titled_values(titled_file)
            recorded = read_recorded_tip(tip_file)
            staging = tmp / "staging"
            files = build_staging(root, head, staging)
            lines.append(f"site_publish: staging tree from data commit {head[:12]}: {len(files)} files")
            for gate, problems in (("mask scan", mask_problems(staging, titled, official_names)),
                                   ("POPIA", popia_problems(staging, banned_names)),
                                   ("allowlist", allowlist_problems(staging))):
                if problems:
                    lines += [f"site_publish:   {p}" for p in problems[:5]]
                    raise Blocked(gate)
            lines.append("site_publish: mask scan, POPIA check and allowlist test passed")
            work = tmp / "work.git"
            _git("init", "-q", "--bare", str(work))
            ls = _git("ls-remote", remote, "refs/heads/main", cwd=work, check=False)
            if ls.returncode != 0:
                raise Blocked("fetch failed")
            fields = _out(ls).split()
            if not fields:
                raise Blocked("unexpected remote commit")          # no main: this helper never makes a root commit
            if _git("fetch", "-q", "--no-tags", remote, "+refs/heads/main:refs/remotes/site/main", cwd=work,
                    check=False).returncode != 0:
                raise Blocked("fetch failed")
            fetched = _out(_git("rev-parse", "refs/remotes/site/main", cwd=work))
            if fetched != fields[0]:
                raise Blocked("unexpected remote commit")
            accepted = gate8(work, fetched, recorded)
            lines.append(f"site_publish: remote tip {accepted[:12]} accepted (gate 8)")
            tree = write_tree(work, staging)
            if tree == _out(_git("rev-parse", f"{accepted}^{{tree}}", cwd=work)):
                lines.append("site_publish: no change; nothing pushed")
                return Result(EXIT_OK, lines)
            msg = message or f"site: publish public-data/v1 from data commit {head[:12]}"
            commit = _out(_git("commit-tree", tree, "-p", accepted, "-m", msg, cwd=work, env=IDENTITY))
            if _out(_git("rev-parse", f"{commit}^{{tree}}", cwd=work)) != tree:
                raise Blocked("tree hash mismatch")
        except Blocked as e:
            return Result(EXIT_BLOCKED, [f"ACTION: site publish blocked ({e})"] + lines)
        except (subprocess.SubprocessError, OSError) as e:
            return Result(EXIT_BLOCKED, [f"ACTION: site publish blocked (git error: {type(e).__name__})"] + lines)
        push = _git("push", "-q", remote, f"{commit}:refs/heads/main", cwd=work, check=False)   # no force
        if push.returncode != 0:
            return Result(EXIT_FAILED, ["ACTION: site publish failed (push refused or failed; nothing changed by this run)"] + lines)
        try:
            record_tip(tip_file, commit)
        except OSError:
            return Result(EXIT_FAILED, [f"ACTION: site publish failed (pushed {commit}, but the tip was not recorded)"] + lines)
        if bundle_dir:
            try:
                _git("update-ref", "refs/heads/main", commit, cwd=work)
                _git("bundle", "create", "-q", str(Path(bundle_dir) / f"site-{commit[:12]}.bundle"), "main", cwd=work)
            except (subprocess.SubprocessError, OSError):
                lines.append("site_publish: WARN private bundle not written (the tip is recorded)")
        lines.append(f"site_publish: pushed {commit}")
        return Result(EXIT_OK, lines)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _warehouse_names() -> tuple[frozenset, frozenset]:
    """Official municipality names and restricted-register person names from the warehouse (read-only)."""
    import duckdb

    from thusa import publish_data as pdx
    from thusa.settings import get_paths
    p = get_paths()
    con = duckdb.connect(str(p.warehouse), read_only=True)
    try:
        official = pdx.official_municipality_names(con)
        banned = frozenset(r[0].lower() for r in con.execute(
            "SELECT name FROM curated.restriction WHERE is_person AND name IS NOT NULL").fetchall())
    finally:
        con.close()
    return official, banned


PRIVATE_CONFIG = Path.home() / ".config" / "thusa" / "site-publish.json"
CONFIG_KEYS = {"PF_TITLED_VALUES_FILE": "titled_values_file", "PF_SITE_TIP_FILE": "tip_file",
               "PF_SITE_BUNDLE_DIR": "bundle_dir"}


def private_settings(environ=os.environ, config: Path | None = None) -> dict[str, str | None]:
    """The private inputs: each environment variable, else the same key in the private config file, else None."""
    cfg: dict = {}
    path = config or PRIVATE_CONFIG
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        cfg = loaded if isinstance(loaded, dict) else {}
    except (OSError, ValueError):
        cfg = {}
    out = {}
    for env_name, key in CONFIG_KEYS.items():
        v = environ.get(env_name) or cfg.get(key)
        out[env_name] = str(v) if v else None
    return out


def main(argv: list[str] | None = None, out=print) -> int:
    if argv:
        out("ACTION: site publish blocked (this command takes no arguments)")
        return EXIT_BLOCKED
    root = Path(__file__).resolve().parents[1]
    try:
        official, banned = _warehouse_names()
    except Exception as e:  # noqa: BLE001 - any failure here means the scans cannot run
        out(f"ACTION: site publish blocked (warehouse names cannot be read: {type(e).__name__})")
        return EXIT_BLOCKED
    cfg = private_settings()
    r = publish(root, remote=SITE_REMOTE_URL, tip_file=cfg["PF_SITE_TIP_FILE"], titled_file=cfg["PF_TITLED_VALUES_FILE"],
                bundle_dir=cfg["PF_SITE_BUNDLE_DIR"], official_names=official, banned_names=banned)
    for line in r.lines:
        out(line)
    return r.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
