"""CHG-2026-051 guard: no word-for-word owner chat quotes in tracked text.

Public text names an owner decision by role and date only, for example
"Owner GO for head 363ae159, 1 Nov 2026 19:41 SAST". The exact words live in a
private record outside git.

Two checks:
1. Marker: no string in double, single, curly or backtick quotes that starts
   with GO / Go (the form of a
   quoted merge GO).
2. Known quotes: no string inside any of those delimiters whose normalised text hashes to a
   known owner quote. Only hashes are stored here, never the words.
"""
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PREFIXES = ("public-data/", "data/")
SKIP_FILES = {"tests/test_no_owner_quotes.py"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".html", ".py", ".json", ".toml", ".sh", ".js", ".css", ""}

# Opening delimiters: double, single, curly double/single, backtick.
GO_MARKER = re.compile(r"(?:[\"\u201c\u2018`]|(?<![\w'])')(?:GO|Go)\b")
QUOTED_PATTERNS = (
    re.compile(r'"([^"\n]{1,400})"'),
    re.compile(r'\u201c([^\u201c\u201d\n]{1,400})\u201d'),
    re.compile(r'\u2018([^\u2018\u2019\n]{1,400})\u2019'),
    re.compile(r"(?<![\w'])'([^'\n]{1,400})'(?!\w)"),
    re.compile(r'`([^`\n]{1,400})`'),
)

KNOWN_QUOTE_SHA256 = {
    "acd88b932526dd0f2cb66e76fd95234c884aca2c0d5f1bae5fbb023002ceaeee",
    "09cf2e9cb6e01eb69a2f873e9ca01bbf90d605f8bc7f4bbf0331edd5bb688240",
    "3e57719b9a99bda116af7a168fb63afaebc4824a8875a8e14fd2fbc327fbaab4",
    "ab0d1307766ce08eadfdc7655cd528e2036bd93310e33aecf7aaa78fa5cb9429",
    "4cd0e21a9a0795a14ec9aa5f0e7d1abff0492565770e43eafdf1e3e8afed1f33",
    "db619045652051133f9a2a1ffda9db19cc410b760c2fb7231c351fcae958c9bf",
    "48e095e7021fbd2b41bb318b167fe437c6af9ba55e0faa0ed44f2f6910e5d3c9",
    "0bb61f469bc16e4ef97d8c4ed32d111000e147aece24df7272d80c6172c9e689",
    "488e1b788555c321c7d1be84a1dd3bb65401e172eb0421d532f92b6cbc538aec",
    "bc2ce29c139ec6c209072e8c3c553c665f4ed42d4247398154d29cc1cc2bba17",
    "389a0b8cc32312da91507f10f2e6e9365922fb78d43ae964f9049d602d97b156",
    "165009f015b98fb54abae3b84bc7371bd4ce2a8bbc6ed46e9d69f3eb4073acdb",
    "8832d6d1ad4e4d2960507778b410f7d5aa43ac6afaf853ab5a71413b2842c2f1",
    "98bf104287fc35b9bcd82e7f954c64433fab58bd93a90a2761d4d4cd72a84c8d",
    "5cc033f0a018c8d56d347b0431d6fb70245ed2667d8128b7d59d4c97d75aeb08",
    "6fd0dda5ee6db9f25d0fa749c32a7a457ad099689ef138b69a399520ff936bcf",
    "39921ffc0284822d35d80868b4f9c01ba0ed2b224a3411cf3890752ac35ef815",
    "29669ba872c5b8553359a5e0dedff6344108d03752a88aacc1316927aadf6533",
    "603789e88dc4bf6344c00eda4fb881e1dfd5f3fc87cbed40eec5483989331f7c",
    "6e7ecf10083ec035057bdce834a72bbe2bffae8df9383ed10eb06c78dd70944b",
    "d2564c6e963077ac8ce7fb0f13b9ca4a5be8698e55a9ee8fb930516545985707",
    "04b7b0abcc7ea126e6d5b2c90bb27d429c05f75ce952542ea87bd1a76b3b8689",
    "ced91e50af253befaa0718277638c879dd277b3e66bea7fb0f2b914ec584a020",
    "86f7d17cf8be6ba01d078c5d578040d4f7c068546cf504780b267ea52e77964d",
    "208b3530e628b2509d5984b7b031fe881e53f3193675ba3dc18246e5a738bdb2",
    "9d6a632fdd200ac551a7e1e9f42e2a8e35c04c281bee0a8b81ecf7fa52e26068",
    "7b9a82a0c666bfe5ca83dc4b794e6cdd70f7293bce4eecd20a4f91bcf71f96eb",
    "fa11089a9bb2a52dd153c2071365eada28da8d345acac6249dc10440276019d4",
    "8592490d8015e3b043548d1373b0468c2fc6566474e8b68d5af7ffd51680c32e",
    "2b3b6a1a59a8940a754c165c61ab7b764023dfd83339b3ddef6fd0671bd2dc09",
}


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def _tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for rel in out.splitlines():
        if rel.startswith(SKIP_PREFIXES) or rel in SKIP_FILES:
            continue
        p = ROOT / rel
        if p.suffix not in TEXT_SUFFIXES or not p.is_file():
            continue
        try:
            yield rel, p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def test_no_quoted_go_marker():
    bad = []
    for rel, text in _tracked():
        for i, line in enumerate(text.splitlines(), 1):
            if GO_MARKER.search(line):
                bad.append(f"{rel}:{i}")
    assert not bad, "quoted GO found; name it by role and date instead: " + ", ".join(bad)


def test_no_known_owner_quote():
    bad = []
    for rel, text in _tracked():
        for i, line in enumerate(text.splitlines(), 1):
            for m in (m for pat in QUOTED_PATTERNS for m in pat.finditer(line)):
                if hashlib.sha256(_norm(m.group(1)).encode()).hexdigest() in KNOWN_QUOTE_SHA256:
                    bad.append(f"{rel}:{i}")
    assert not bad, "known owner quote found; reword by role and date: " + ", ".join(bad)


def test_guard_detects_examples():
    # Synthetic samples only: this file must not hold any owner wording.
    for sample in ('x "GO sample-a" y', "x 'Go sample-b' y", "\u201cGO sample-c\u201d",
                   "\u2018Go sample-d\u2019", "`GO sample-e`"):
        assert GO_MARKER.search(sample), sample
    assert not GO_MARKER.search('assert a["province"] == "GP"')
    assert not GO_MARKER.search("the owner's GO for head abc")
    fake = "synthetic guard sample"
    known = KNOWN_QUOTE_SHA256 | {hashlib.sha256(_norm(fake).encode()).hexdigest()}
    for text in (f'"{fake}"', f"'{fake}'", f"\u201c{fake}\u201d", f"\u2018{fake}\u2019", f"`{fake}`"):
        hits = [m.group(1) for pat in QUOTED_PATTERNS for m in pat.finditer(text)]
        assert any(hashlib.sha256(_norm(h).encode()).hexdigest() in known for h in hits), text
    assert len(KNOWN_QUOTE_SHA256) == 30
