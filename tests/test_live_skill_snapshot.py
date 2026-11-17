"""CHG-2026-061: the repo holds the live refresh skill text and the proposed step as a marked draft.

The draft must be exactly the live snapshot with these changes and no others, so the head shows exactly what the
later step changes:
- a DRAFT comment after the frontmatter;
- step 0 says "steps 1 to 6" (was "1 to 5");
- step 3 keeps only its first line; its publish bullets move, unchanged, into the new step 4;
- new step 4 (marked DRAFT): the exact text in STEP4_HEAD, the moved bullets, then the exact text in STEP4_TAIL;
- the health check becomes step 5 and "Never confirm or reject" becomes step 6.
Neither file is a template skill (see tests/test_bot_skills.py).
"""
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "docs" / "bot" / "live-skill"
LIVE = D / "publicfunds-refresh.LIVE-2026-11-17.md"
DRAFT = D / "publicfunds-refresh.PROPOSED-CHG-2026-061.md"

COMMENT = ("<!-- DRAFT (CHG-2026-061). NOT APPLIED. This is the live skill text of 17 Nov 2026 with the proposed CHG-2026-061 step added.\n"
           "     The live skill and the nightly routine prompt change only after the owner's own GO for that step,\n"
           "     and they change together, so that the publish runs once per night. -->\n")
STEP4_HEAD = """4. **[DRAFT, CHG-2026-061: proposed new step; not in the live skill]** Only if step 1 returned **0**: publish, then check the live site.
   This step replaces the publish in the nightly routine prompt. The routine prompt must not publish again (one publish per night).
   `cd /workspace/publicfunds && scripts/publish-public-data.sh --push > data/publish-run.log 2>&1; echo $?`
   Read data/publish-run.log for the evidence_guard line and the publish result. Do not push by hand.
"""
STEP4_TAIL = """   Then run: `python3 scripts/nightly_check_live.py --publish-exit <that exit code> --publish-log data/publish-run.log; echo $?`
   - Put its RESULT: line, any [BREACH] / [WARN] lines, and its check_live:, healthz: and NEXT: lines in the nightly report.
   - 0: OK, or WARN only. Report any [WARN] lines. The rest of the routine may finish.
   - 1: at least one BREACH. A BREACH is reported as a breach, never as success. The wrapper has already run
     the health check (curl -s http://127.0.0.1:8765/healthz); report its healthz: line. Then stop.
     Do not re-run the publish to fix it. Follow RB-12.
   - 2: a failed check (bad command line, crash, time limit, or it cannot tell if the publish pushed; nothing
     was checked). Report it as a failed check and stop. Do not treat it as OK.
   - 3: skipped, because it is clear that the publish did not push. Report the check_live: SKIPPED line.
     The publish rules (exit 3, exit 4, evidence guard) still apply.
"""


def expected_draft(live: str) -> str:
    lines = live.splitlines(True)
    fm_end = [i for i, l in enumerate(lines) if l == "---\n"][1]
    s3 = next(i for i, l in enumerate(lines) if l.startswith("3. Report briefly"))
    s4 = next(i for i, l in enumerate(lines) if l.startswith("4. Check `curl"))
    s5 = next(i for i, l in enumerate(lines) if l.startswith("5. Never confirm"))
    bullets = lines[s3 + 1:s4]
    assert bullets and all(l.startswith("   - ") for l in bullets)
    head = [l.replace("skip steps 1 to 5", "skip steps 1 to 6") for l in lines[:s3 + 1]]
    out = head[:fm_end + 1] + [COMMENT] + head[fm_end + 1:]
    out += [STEP4_HEAD] + bullets + [STEP4_TAIL]
    out += ["5" + lines[s4][1:]] + ["6" + lines[s5][1:]] + lines[s5 + 1:]
    return "".join(out)


def draft_matches(text: str) -> bool:
    """The one comparison used by the tests: the draft text must equal the constructed expected text exactly."""
    return text == expected_draft(LIVE.read_text(encoding="utf-8"))


def test_files_exist_and_are_not_template_skills():
    assert LIVE.is_file() and DRAFT.is_file()
    assert not list(D.glob("*/SKILL.md")) and not (D / "SKILL.md").exists()


def test_live_snapshot_has_the_expected_shape():
    t = LIVE.read_text(encoding="utf-8")
    assert "skip steps 1 to 5" in t and "4. Check `curl" in t and "5. Never confirm" in t


def test_draft_is_exactly_the_live_text_plus_the_marked_step():
    assert draft_matches(DRAFT.read_text(encoding="utf-8"))


def test_extra_text_in_the_draft_fails():
    good = DRAFT.read_text(encoding="utf-8")
    for bad in (good.replace("Do not push by hand.\n", "Do not push by hand.\n   You may also push other branches.\n", 1),
                good.replace("   - 0: OK", "   - Extra unmarked line.\n   - 0: OK", 1),
                good.replace("5. Check `curl", "Extra line before the health check.\n5. Check `curl", 1)):
        assert bad != good
        assert not draft_matches(bad)
    assert not draft_matches(good.replace("Only if step 1 returned **0**: ", "", 1))      # a dropped condition fails too
