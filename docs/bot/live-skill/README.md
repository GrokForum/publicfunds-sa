# Live refresh skill: snapshot and CHG-2026-061 draft

This folder holds two files for review of CHG-2026-061. Neither file is a template skill, and the bot does not load them from here.

| File | What it is |
|---|---|
| `publicfunds-refresh.LIVE-2026-11-17.md` | A byte-for-byte copy of the live `publicfunds-refresh` skill on the bot computer, taken 17 Nov 2026 (sha256 `aee6514d55b3751271c84a56a537e156f67a98742d09bf5619171b9fb7c0f29b`). |
| `publicfunds-refresh.PROPOSED-CHG-2026-061.md` | **Draft, not applied.** The same text with the proposed CHG-2026-061 step added as step 4 (marked `[DRAFT, CHG-2026-061 ...]`). Step 4 runs only if step 1 returned 0, and it replaces the publish in the routine prompt (one publish per night). Step 3's publish bullets move, unchanged, into step 4. The later steps are renumbered (health check 5, never confirm or reject 6; step 0 says "steps 1 to 6"). |

`tests/test_live_skill_snapshot.py` builds the expected draft from the snapshot with the exact step-4 text, the moved bullets and the renumbering, and checks that the draft file is equal to it. Extra text fails the test.

## How the copies relate

- The template skill `docs/bot/skills/publicfunds-refresh/SKILL.md` is a generic copy for new installs. It differs from the live skill: the template has the publish as step 4 and the health check as step 5. The live skill has a step 0 (update the checkout) and no numbered publish step; its step 3 says "when the routine publishes", so the publish command is in the nightly routine prompt.
- CHG-2026-061 does not change the template skill, the live skill or the nightly routine prompt.

## Follow-up (owner decisions; not part of CHG-2026-061)

1. Apply the draft step to the live skill and the nightly routine prompt together, so that the publish runs once per night. This needs the owner's own GO for that step.
2. Decide which copy is the source of truth for the refresh skill (the live skill or the template copy), and how the other copy is brought in line.
3. Decide if the routine always uses `--push` and never pushes by hand (see CHG-2026-061, "Push detection").
