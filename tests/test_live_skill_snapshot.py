"""CHG-2026-061: the repo holds the live refresh skill text and the proposed step as a marked draft.

The draft must be exactly the live snapshot with these changes and no others, so the head shows exactly what the
later step changes:
- a DRAFT comment after the frontmatter;
- step 0 says "steps 1 to 6" (was "1 to 5");
- step 3 keeps only its first line; its publish bullets move, unchanged, into the new step 4;
- new step 4 (marked DRAFT): the exact text in STEP4_HEAD, the moved bullets, then the exact text in STEP4_TAIL;
- the health check becomes step 5 and "Never confirm or reject" becomes step 6.
Neither file is a template skill (see tests/test_bot_skills.py).

CHG-2026-065: the master copy of the live skill (publicfunds-refresh.MASTER.md) is the draft made final, and the
routine prompt (routine-nightly.PROPOSED.md) goes with it. The dated snapshot stays byte-exact to its own sha256.
"""
import hashlib
from pathlib import Path

import pytest

D = Path(__file__).resolve().parent.parent / "docs" / "bot" / "live-skill"
LIVE = D / "publicfunds-refresh.LIVE-2026-11-17.md"
DRAFT = D / "publicfunds-refresh.PROPOSED-CHG-2026-061.md"
MASTER = D / "publicfunds-refresh.MASTER.md"
ROUTINE = D / "routine-nightly.PROPOSED.md"
LIVE_SHA256 = "aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b"
LIVE_PATH = Path("/home/box/agent-data/workflows/publicfunds-refresh/SKILL.md")
PUBLISH_CMD = "`cd /workspace/publicfunds && scripts/publish-public-data.sh --push > data/publish-run.log 2>&1; echo $?`"

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
    assert LIVE.is_file() and DRAFT.is_file() and MASTER.is_file() and ROUTINE.is_file()
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


# CHG-2026-065: master copy of the live skill, the routine prompt, and the drift check.

# The exact edits that make the CHG-2026-061 draft final. No other change is allowed.
# 9 edits. Edits 1 to 4 hold the 5 edits of the first CHG-2026-065 commit (the two step-4 head lines are now one
# edit, and edit 3 now also moves the wrapper command up). Edits 5 to 9 and the new step-4 lines are the follow-up
# of 17 Nov 2026: step 4 runs on the nightly run only (owner decision, as reported to the author (PublicFunds)),
# the wrapper runs after every publish, whatever the exit code, and the exit 3 and exit 4 wording matches
# scripts/nightly_check_live.py.
INTRO = ("Two kinds of run: the nightly routine does steps 0 to 6, and step 4 is its only publish. A run on request "
         "does steps 0 to 3 and then 5 and 6, and reports; it does not publish unless the owner asks for a publish "
         "(see step 4).\n\n")
STEP4_FINAL_HEAD = (
    "4. **Nightly run only.** Only if step 1 returned **0**: publish, then check the live site (CHG-2026-061, CHG-2026-065). If step 1 returned anything else, do not publish.\n"
    "   On a run on request, skip this step: do not publish unless the owner asks for a publish. If the owner asks, run this step with the same condition: only if step 1 returned **0**.\n"
    "   If step 4 was skipped, add no publish ACTION line; report the step 1 result.\n"
    "   This is the only publish of the night. The nightly routine prompt runs this skill and does not publish by itself.\n")
WRAPPER_CMD = "`python3 scripts/nightly_check_live.py --publish-exit <that exit code> --publish-log data/publish-run.log; echo $?`"
# Edit 4: the publish guard bullet. The first sentence no longer says "the routine publishes", and the ACTION line
# order agrees with the exit 3, exit 4 and other-exit bullets: refused (exit 3) or failed (exit 4, other non-zero)
# first, then needs attention when the guard line is not a bare pass; exit 0 gives needs attention only, or nothing.
GUARD_OLD = 'When the routine publishes with `scripts/publish-public-data.sh --push`, the script prints one line starting `evidence_guard:`. Add a line "Evidence guard:" to the report with that line and up to three note lines under it. Only a bare `evidence_guard: pass` is quiet. If the line is anything else (`pass (N notes)`, `warn (N notes)`, `BLOCKED`, `not an evidence-guard refusal`, `UNKNOWN`) or is **missing**, treat it as not passed (a missing line is UNKNOWN), and begin the report with `ACTION: publish needs attention` and quote the line.'
GUARD_NEW = 'The publish script prints one line starting `evidence_guard:`. Add a line "Evidence guard:" to the report with that line and up to three note lines under it. Only a bare `evidence_guard: pass` is quiet: it adds no ACTION line of its own. If the line is anything else (`pass (N notes)`, `warn (N notes)`, `BLOCKED`, `not an evidence-guard refusal`, `UNKNOWN`) or is **missing**, treat it as not passed (a missing line is UNKNOWN) and quote the line. The first ACTION line of the report depends on the publish exit code. If the publish was refused (exit 3, see the next bullet), the report always begins with `ACTION: publish refused`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. If the publish failed (exit 4 or any other non-zero exit, see the bullets below), the report always begins with `ACTION: publish failed`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. If the publish exited 0 and the guard line is not a bare pass, the report begins with `ACTION: publish needs attention`. A bare pass with publish exit 0 adds no ACTION line.'
MASTER_EDITS = (
    (COMMENT, ""),                                                                                            # 1
    ("4. **[DRAFT, CHG-2026-061: proposed new step; not in the live skill]** Only if step 1 returned **0**: publish, then check the live site.\n"
     "   This step replaces the publish in the nightly routine prompt. The routine prompt must not publish again (one publish per night).\n",
     STEP4_FINAL_HEAD),                                                                                        # 2
    ("   Read data/publish-run.log for the evidence_guard line and the publish result. Do not push by hand.\n",
     "   Always use `--push`. Do not push by hand. Read data/publish-run.log for the evidence_guard line and the publish result.\n"
     "   Then, whatever the publish exit code, run the live check wrapper. It only reads; it never publishes or pushes:\n"
     "   " + WRAPPER_CMD + "\n"),                                                                                # 3
    (GUARD_OLD, GUARD_NEW),                                                                                    # 4
    ("# PublicFunds refresh\n\n", "# PublicFunds refresh\n\n" + INTRO),                                       # 5
    ("Do not retry and do not edit data. Report to the owner at once:",
     "Do not retry and do not edit data. The wrapper prints `check_live: SKIPPED` and exits 3. Begin the report with `ACTION: publish refused`. If the guard line is not a bare pass (for example `BLOCKED`), put `ACTION: publish needs attention` on the next line (refused first, then needs attention). Then give first:"),  # 6
    ("   - If it exits **4**, stop and report (other changes, wrong branch, main moved). Any other non-zero exit: stop and report too.\n",
     "   - If it exits **4** (other changes, wrong branch, main moved), nothing was pushed. The wrapper prints `check_live: SKIPPED` and exits 3. Begin the report with `ACTION: publish failed`. If the guard line is not a bare pass, put `ACTION: publish needs attention` on the next line (failed first, then needs attention). Stop after the wrapper and report. Do not retry.\n"
     "   - Any other non-zero publish exit: the wrapper cannot tell if the publish pushed. It prints `check_live: FAILED CHECK` and exits 2. Begin the report with `ACTION: publish failed`. If the guard line is not a bare pass, put `ACTION: publish needs attention` on the next line (failed first, then needs attention). Stop and report, and check by hand if new data went live. Do not retry.\n"),  # 7
    ("   Then run: " + WRAPPER_CMD + "\n", "   The wrapper's exit code:\n"),                                 # 8
    ("   - 3: skipped, because it is clear that the publish did not push. Report the check_live: SKIPPED line.\n"
     "     The publish rules (exit 3, exit 4, evidence guard) still apply.\n",
     "   - 3: skipped, because it is clear that the publish did not push (publish exit 3 or 4, or nothing new to push).\n"
     "     check_live was not run. Report the check_live: SKIPPED line. The publish rules above still apply.\n"),  # 9
)
ON_REQUEST = "On a run on request, skip this step: do not publish unless the owner asks for a publish. If the owner asks, run this step with the same condition: only if step 1 returned **0**."


def expected_master(draft: str) -> str:
    for old, new in MASTER_EDITS:
        assert draft.count(old) == 1, old
        draft = draft.replace(old, new)
    return draft


def master_structure_ok(text: str) -> bool:
    """Publish only in step 4, with --push, behind the step-1 gate; publish wording only after the publish command."""
    lines = text.splitlines()
    try:
        s4 = next(i for i, l in enumerate(lines) if l.startswith("4. "))
        cmd = next(i for i, l in enumerate(lines) if l.strip() == PUBLISH_CMD)
        s5 = next(i for i, l in enumerate(lines) if l.startswith("5. Check `curl"))
    except StopIteration:
        return False
    before = "\n".join(lines[:s4])
    step4 = "\n".join(lines[s4:s5])
    return (lines[s4].startswith("4. **Nightly run only.** Only if step 1 returned **0**: publish")
            and s4 < cmd < s5
            and text.count("publish-public-data.sh") == 1
            and "--push" in lines[cmd]
            and all(w not in before for w in ("publish-public-data.sh", "evidence_guard", "--push", "nightly_check_live"))
            and all(w not in "\n".join(lines[s4:cmd]) for w in ("evidence_guard", "exits **3**", "nightly_check_live"))
            and "nightly_check_live.py" in step4
            and "DRAFT" not in text
            and lines[0] == "---"
            and any(l == "name: publicfunds-refresh" for l in lines[:3])
            and "6. Never confirm" in text)


def test_live_snapshot_is_byte_exact_to_its_sha256():
    assert hashlib.sha256(LIVE.read_bytes()).hexdigest() == LIVE_SHA256


def test_master_is_the_draft_made_final():
    assert len(MASTER_EDITS) == 9
    assert MASTER.read_text(encoding="utf-8") == expected_master(DRAFT.read_text(encoding="utf-8"))


def test_master_structure():
    assert master_structure_ok(MASTER.read_text(encoding="utf-8"))


def test_master_structure_check_catches_bad_text():
    good = MASTER.read_text(encoding="utf-8")
    assert master_structure_ok(good)
    bads = (
        good.replace("publish-public-data.sh --push >", "publish-public-data.sh >", 1),            # no --push
        good.replace("Only if step 1 returned **0**: publish", "Publish", 1),                        # gate dropped
        good.replace("3. Report briefly", "3. Run `scripts/publish-public-data.sh --push`. Report briefly", 1),  # publish before step 4
        good.replace("3. Report briefly", "3. Read the evidence_guard line. Report briefly", 1),      # publish wording before step 4
        good.replace("6. Never confirm", "6. **[DRAFT]** Never confirm", 1),                          # draft marker left in
    )
    for bad in bads:
        assert bad != good
        assert not master_structure_ok(bad)


def routine_prompt(text: str) -> str:
    begin, end = "<!-- BEGIN ROUTINE PROMPT -->\n", "<!-- END ROUTINE PROMPT -->\n"
    assert text.count(begin) == 1 and text.count(end) == 1
    return text.split(begin, 1)[1].split(end, 1)[0]


def routine_file_ok(text: str) -> bool:
    """The routine-prompt file names the publish script exactly once (in the rule that step 4 is the only publish)."""
    return text.count("publish-public-data.sh") == 1


def test_routine_file_names_the_publish_script_once():
    good = ROUTINE.read_text(encoding="utf-8")
    assert routine_file_ok(good)
    bad = good.replace("- Never confirm or reject flags.\n",
                       "- Never confirm or reject flags.\n- Then run `scripts/publish-public-data.sh --push`.\n", 1)
    assert bad != good and not routine_file_ok(bad)                      # a second publish line fails


def test_routine_prompt_matches_the_master():
    prompt = routine_prompt(ROUTINE.read_text(encoding="utf-8"))
    assert "ACTION: publish refused" in prompt
    assert PROMPT_ACTION_RULE in prompt
    assert "publicfunds-refresh skill" in prompt and "steps 0 to 6" in prompt
    assert "This is the nightly run" in prompt and "the nightly-run path" in prompt
    assert "Step 4 of the skill is the only publish of the night" in prompt
    assert "only if step 1 returned 0" in prompt and "Always use `--push`" in prompt
    assert "Do not run the publish script at any other point" in prompt
    assert "Do not push by hand" in prompt
    # The prompt itself never gives a publish command line to run.
    assert "> data/publish-run.log" not in prompt and "echo $?" not in prompt
    assert "/home/box" not in prompt


def test_action_line_order_on_a_refused_publish():
    """Publish exit 3 with evidence_guard BLOCKED: `ACTION: publish refused` first, then `ACTION: publish needs attention`."""
    t = MASTER.read_text(encoding="utf-8")
    line = next(l for l in t.splitlines() if "If the publish script exits **3**" in l)
    assert line.index("`ACTION: publish refused`") < line.index("`ACTION: publish needs attention`")
    assert "(refused first, then needs attention)" in line
    assert action_order_ok(t)


BARE_PASS_RULE = ("If the publish exited 0 and the guard line is not a bare pass, the report begins with "
                  "`ACTION: publish needs attention`. A bare pass with publish exit 0 adds no ACTION line.")
REFUSED_RULE = ("If the publish was refused (exit 3, see the next bullet), the report always begins with `ACTION: publish refused`; "
                "if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line.")
FAILED_RULE = ("If the publish failed (exit 4 or any other non-zero exit, see the bullets below), the report always begins with "
               "`ACTION: publish failed`; if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line.")
FAILED_BULLET = ("Begin the report with `ACTION: publish failed`. If the guard line is not a bare pass, put "
                 "`ACTION: publish needs attention` on the next line (failed first, then needs attention).")
PROMPT_ACTION_RULE = ("on publish exit 3, `ACTION: publish refused`; on publish exit 4 or any other non-zero exit, "
                      "`ACTION: publish failed`; then, if the guard line is not a bare pass, `ACTION: publish needs attention` "
                      "on the next line. On publish exit 0, the report begins with `ACTION: publish needs attention` only when "
                      "the guard line is not a bare pass. A bare pass with publish exit 0 adds no ACTION line")


def action_order_ok(text: str) -> bool:
    """The guard bullet and the exit 3, exit 4 and other-exit bullets agree on the first ACTION line and the order."""
    lines = text.splitlines()
    guard = next((l for l in lines if "**Publish guard line" in l), "")
    exit3 = next((l for l in lines if "If the publish script exits **3**" in l), "")
    exit4 = next((l for l in lines if "If it exits **4**" in l), "")
    other = next((l for l in lines if "Any other non-zero publish exit" in l), "")
    def before(line, a, b):
        return a in line and b in line and line.index(a) < line.index(b)
    return (REFUSED_RULE in guard and FAILED_RULE in guard and BARE_PASS_RULE in guard
            and "begin the report with `ACTION: publish needs attention`" not in guard
            and "If there was no refusal" not in guard and "with no refusal" not in guard
            and before(exit3, "`ACTION: publish refused`", "`ACTION: publish needs attention`")
            and FAILED_BULLET in exit4 and FAILED_BULLET in other
            and before(exit4, "`ACTION: publish failed`", "`ACTION: publish needs attention`")
            and before(other, "`ACTION: publish failed`", "`ACTION: publish needs attention`"))


def test_action_order_check_catches_a_conflicting_guard_bullet():
    good = MASTER.read_text(encoding="utf-8")
    assert action_order_ok(good)
    bads = (
        # the old draft wording: needs-attention begins the report, also on a refusal
        good.replace("treat it as not passed (a missing line is UNKNOWN) and quote the line.",
                     "treat it as not passed (a missing line is UNKNOWN), and begin the report with `ACTION: publish needs attention` and quote the line.", 1),
        # the refusal sentence dropped from the guard bullet
        good.replace("If the publish was refused (exit 3, see the next bullet), the report always begins with `ACTION: publish refused`; "
                     "if the guard line is not a bare pass, `ACTION: publish needs attention` goes on the next line. ", "", 1),
        # the exit 3 bullet order swapped
        good.replace("Begin the report with `ACTION: publish refused`. If the guard line is not a bare pass (for example `BLOCKED`), put `ACTION: publish needs attention` on the next line",
                     "Begin the report with `ACTION: publish needs attention`. If the guard line is not a bare pass (for example `BLOCKED`), put `ACTION: publish refused` on the next line", 1),
    )
    for bad in bads:
        assert bad != good
        assert not action_order_ok(bad)


def test_live_skill_has_not_drifted():
    """Drift check: the live skill is the master (after deploy) or the 17 Nov 2026 snapshot (before deploy)."""
    if not LIVE_PATH.is_file():
        pytest.skip("live skill path is not on this computer")
    live = LIVE_PATH.read_bytes()
    assert live in (MASTER.read_bytes(), LIVE.read_bytes()), "live skill differs from the master and the snapshot"


def on_request_rule_ok(text: str) -> bool:
    """Step 4 publishes on the nightly run only; a run on request does not publish unless the owner asks."""
    lines = text.splitlines()
    s4 = next((i for i, l in enumerate(lines) if l.startswith("4. ")), None)
    if s4 is None:
        return False
    return (lines[s4].startswith("4. **Nightly run only.**")
            and lines[s4 + 1].strip() == ON_REQUEST
            and "it does not publish unless the owner asks for a publish" in "\n".join(lines[:s4]))


def test_master_publishes_on_the_nightly_run_only():
    assert on_request_rule_ok(MASTER.read_text(encoding="utf-8"))


def test_on_request_rule_check_catches_bad_text():
    good = MASTER.read_text(encoding="utf-8")
    for bad in (good.replace("   " + ON_REQUEST + "\n", "", 1),                                    # on-request line dropped
                good.replace("4. **Nightly run only.** ", "4. ", 1),                               # nightly-only marker dropped
                good.replace("it does not publish unless the owner asks", "it publishes", 1)):    # intro says it publishes
        assert bad != good
        assert not on_request_rule_ok(bad)


def test_wrapper_runs_after_every_publish_and_matches_its_exit_codes():
    """The wrapper runs whatever the publish exit code; the skill's exit 3 and 4 wording matches the script."""
    t = MASTER.read_text(encoding="utf-8")
    assert t.count(WRAPPER_CMD) == 1
    assert "Then, whatever the publish exit code, run the live check wrapper." in t
    assert t.index(PUBLISH_CMD) < t.index(WRAPPER_CMD) < t.index("If the publish script exits **3**")
    assert t.count("The wrapper prints `check_live: SKIPPED` and exits 3.") == 2      # publish exit 3 and exit 4
    assert "It prints `check_live: FAILED CHECK` and exits 2." in t                    # any other non-zero publish exit
    import importlib.util
    spec = importlib.util.spec_from_file_location("ncl", D.parent.parent.parent / "scripts" / "nightly_check_live.py")
    ncl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ncl)
    assert ncl.publish_pushed(3, "")[0] == ncl.NOT_PUSHED and ncl.publish_pushed(4, "")[0] == ncl.NOT_PUSHED
    assert ncl.publish_pushed(5, "")[0] == ncl.UNKNOWN


def test_bare_pass_with_publish_exit_0_adds_no_action_line():
    t = MASTER.read_text(encoding="utf-8")
    guard = next(l for l in t.splitlines() if "**Publish guard line" in l)
    assert BARE_PASS_RULE in guard
    assert "Only a bare `evidence_guard: pass` is quiet: it adds no ACTION line of its own." in guard
    prompt = routine_prompt(ROUTINE.read_text(encoding="utf-8"))
    assert "A bare pass with publish exit 0 adds no ACTION line" in prompt


def test_wording_that_gives_a_bare_pass_an_action_line_fails():
    good = MASTER.read_text(encoding="utf-8")
    for bad in (
        good.replace(BARE_PASS_RULE, "If there was no refusal, the report begins with `ACTION: publish needs attention`.", 1),
        good.replace("If the publish exited 0 and the guard line is not a bare pass, the report begins",
                     "If the publish exited 0, the report begins", 1),
        good.replace("A bare pass with publish exit 0 adds no ACTION line.",
                     "A bare pass with publish exit 0 begins the report with `ACTION: publish needs attention`.", 1),
    ):
        assert bad != good
        assert not action_order_ok(bad)


def test_publish_failed_comes_first_on_exit_4_and_other_non_zero_exits():
    t = MASTER.read_text(encoding="utf-8")
    assert action_order_ok(t)
    lines = t.splitlines()
    for marker in ("If it exits **4**", "Any other non-zero publish exit"):
        line = next(l for l in lines if marker in l)
        assert line.index("`ACTION: publish failed`") < line.index("`ACTION: publish needs attention`")
    prompt = routine_prompt(ROUTINE.read_text(encoding="utf-8"))
    assert PROMPT_ACTION_RULE in prompt
    assert prompt.index("`ACTION: publish failed`") < prompt.index("then, if the guard line is not a bare pass")


def test_wording_without_publish_failed_fails():
    good = MASTER.read_text(encoding="utf-8")
    bads = (
        # the old exit 4 wording: no ACTION line on exit 4 with a bare pass
        good.replace("exits 3. " + FAILED_BULLET + " Stop after the wrapper", "exits 3. Stop after the wrapper", 1),
        # the old other-exit wording
        good.replace("exits 2. " + FAILED_BULLET + " Stop and report", "exits 2. Stop and report", 1),
        # order swapped on exit 4: needs attention before failed
        good.replace("exits 3. " + FAILED_BULLET,
                     "exits 3. Begin the report with `ACTION: publish needs attention`. If the guard line is not a bare pass, put "
                     "`ACTION: publish failed` on the next line (needs attention first, then failed).", 1),
        # the failed sentence dropped from the guard bullet (exit 4 with a bare pass then gets no ACTION line)
        good.replace(FAILED_RULE + " ", "", 1),
        # the guard bullet says needs attention begins the report with no refusal (that would cover exit 4)
        good.replace(BARE_PASS_RULE, "If there was no refusal and the guard line is not a bare pass, the report begins with "
                     "`ACTION: publish needs attention`. A bare pass with no refusal adds no ACTION line.", 1),
    )
    for bad in bads:
        assert bad != good
        assert not action_order_ok(bad)


SKIP_RULE = "If step 4 was skipped, add no publish ACTION line; report the step 1 result."


def skip_rule_ok(master: str, routine: str) -> bool:
    """Step 4 skipped (step 1 did not return 0, or a run on request with no publish ask): no publish ACTION line."""
    lines = master.splitlines()
    s4 = next((i for i, l in enumerate(lines) if l.startswith("4. ")), None)
    if s4 is None:
        return False
    cmd = next((i for i, l in enumerate(lines) if l.strip() == PUBLISH_CMD), None)
    return (cmd is not None and any(l.strip() == SKIP_RULE for l in lines[s4:cmd])
            and SKIP_RULE in routine_prompt(routine))


def test_skipped_step_4_adds_no_publish_action_line():
    assert skip_rule_ok(MASTER.read_text(encoding="utf-8"), ROUTINE.read_text(encoding="utf-8"))


def test_skip_rule_removed_fails():
    master, routine = MASTER.read_text(encoding="utf-8"), ROUTINE.read_text(encoding="utf-8")
    assert not skip_rule_ok(master.replace("   " + SKIP_RULE + "\n", "", 1), routine)      # removed from the master
    assert not skip_rule_ok(master, routine.replace(" " + SKIP_RULE, "", 1))               # removed from the routine prompt
