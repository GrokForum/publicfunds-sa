#!/usr/bin/env python3
"""Site-repository publish (CHG-2026-070, CHG-2026-069 step S11). See thusa/site_repo.py for the gates.

Run it in step 4 of the nightly, only after `scripts/publish-public-data.sh --push` exited 0:

    cd /workspace/publicfunds && uv run python scripts/publish_site_repo.py > data/site-publish.log 2>&1; echo $?

Exit 0 = pushed, or no change; 3 = blocked (a guard or gate failed; nothing pushed); 4 = failed (push or tip record).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from thusa.site_repo import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
