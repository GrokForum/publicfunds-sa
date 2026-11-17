"""CHG-2026-061: the repo holds the live refresh skill text and the proposed step as a marked draft.

The draft must be the live snapshot plus only the marked CHG-2026-061 step (and the renumbering it causes), so the
head shows exactly what the later step changes. Neither file is a template skill (see tests/test_bot_skills.py).
"""
import re
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "docs" / "bot" / "live-skill"
LIVE = D / "publicfunds-refresh.LIVE-2026-11-17.md"
DRAFT = D / "publicfunds-refresh.PROPOSED-CHG-2026-061.md"


def test_files_exist_and_are_not_template_skills():
    assert LIVE.is_file() and DRAFT.is_file()
    assert not list(D.glob("*/SKILL.md")) and not (D / "SKILL.md").exists()


def test_draft_is_marked_and_calls_the_wrapper():
    t = DRAFT.read_text(encoding="utf-8")
    assert "DRAFT (CHG-2026-061). NOT APPLIED." in t
    assert "**[DRAFT, CHG-2026-061: proposed new step; not in the live skill]**" in t
    assert "scripts/nightly_check_live.py --publish-exit" in t and "Do not push by hand." in t


def test_draft_is_the_live_text_plus_only_the_marked_step():
    t = DRAFT.read_text(encoding="utf-8")
    t = re.sub(r"<!-- DRAFT \(CHG-2026-061\).*?-->\n", "", t, flags=re.S)
    t = re.sub(r"^4\. \*\*\[DRAFT, CHG-2026-061.*?(?=^5\. Check )", "", t, flags=re.S | re.M)
    t = t.replace("5. Check `curl", "4. Check `curl").replace("6. Never confirm", "5. Never confirm")
    t = t.replace("skip steps 1 to 6", "skip steps 1 to 5")
    assert t == LIVE.read_text(encoding="utf-8")
