# Live refresh skill: master copy, history and routine prompt

The master copy of the live `publicfunds-refresh` skill is in this folder (CHG-2026-065; owner decision, 17 Nov 2026, as reported to the author (PublicFunds)). The live skill on the bot computer is deployed from it. The bot does not load any file from this folder.

| File | What it is |
|---|---|
| `publicfunds-refresh.MASTER.md` | **Master.** The text of the live skill. It is the CHG-2026-061 draft made final: step 4 runs on the nightly run only; it publishes with `--push` every time, only if step 1 returned 0, and then runs `scripts/nightly_check_live.py` whatever the publish exit code. A run on request does not publish unless the owner asks for a publish. The publish wording is all in step 4, after the publish command. |
| `routine-nightly.PROPOSED.md` | The nightly routine prompt that goes with the master. The prompt runs the skill and does not publish by itself. Deploy it together with the master. |
| `publicfunds-refresh.LIVE-2026-11-17.md` | History and rollback text. A byte-for-byte copy of the live skill of 17 Nov 2026, before CHG-2026-065 (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`). Do not edit it. |
| `publicfunds-refresh.PROPOSED-CHG-2026-061.md` | History. The CHG-2026-061 draft (merged in PR #13). The master replaced it. Do not edit it. |

## Deploy (the orchestrator does this)

The live path is `/home/box/agent-data/workflows/publicfunds-refresh/SKILL.md`. A deploy happens only after two independent reviewer PASSes on the exact head of the change and the owner's GO naming that head, and after the change is merged to `main`.

1. Copy the master from a clean checkout of `main` to the live path, byte for byte: `cp docs/bot/live-skill/publicfunds-refresh.MASTER.md <live path>`.
2. Check: `sha256sum` of both files gives the same value, and `cmp` gives no output.
3. In the same step, replace the nightly routine prompt with the text between the marker lines in `routine-nightly.PROPOSED.md`. Keep the old prompt text outside git as its rollback text.
4. Record the deploy (date and time in SAST, the sha256, who deployed) in the next change record.

Do not edit the live skill directly. A change to the live skill is a change to the master, with its own change record, reviews and owner GO, then a deploy.

## Drift check

`cmp docs/bot/live-skill/publicfunds-refresh.MASTER.md /home/box/agent-data/workflows/publicfunds-refresh/SKILL.md` gives no output when the live skill is the master. Before the first deploy, the live skill is equal to `publicfunds-refresh.LIVE-2026-11-17.md`. `tests/test_live_skill_snapshot.py` runs this check when the live path exists (it is skipped when it does not): the live skill must equal the master or the 17 Nov 2026 snapshot. Any other text is drift and fails the test.

## Rollback

Copy `publicfunds-refresh.LIVE-2026-11-17.md` byte for byte to the live path, and write back the old routine prompt text, in the same step. A repo rollback is `git revert -m 1 <merge commit>`.

## The template skill

`docs/bot/skills/publicfunds-refresh/SKILL.md` is a generic copy for new installs (CI-070). It is not the master and CHG-2026-065 does not change it. It differs from the live skill (it has the publish as step 4 and the health check as step 5, and no step 0).
