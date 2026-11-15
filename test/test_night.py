import json
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = Path(os.environ.get("GAMES_REPO", ROOT.parent / "Building58_games"))


class Replay(unittest.TestCase):
    def test_replay_rules(self):
        subprocess.run(["node", "--test", str(ROOT / "test" / "replay.test.mjs")], check=True, capture_output=True)


@unittest.skipUnless((GAMES / "find-the-ring" / "desk.js").exists(), "set GAMES_REPO to a games checkout with find-the-ring")
class NightExport(unittest.TestCase):
    def test_club_server(self):
        subprocess.run(["node", "--test", str(ROOT / "test" / "play.test.mjs")], check=True, capture_output=True,
                       env={**os.environ, "GAMES_REPO": str(GAMES)})

    def test_holds_only_public_records(self):
        out = ROOT / "out" / "night-test-0.json"
        subprocess.run(["node", str(ROOT / "find-the-ring" / "night.mjs"), "test-0"], check=True, capture_output=True,
                       env={**os.environ, "GAMES_REPO": str(GAMES)})
        night = json.loads(out.read_text())
        self.assertGreater(len(night["records"]), 0)
        self.assertEqual(len(night["regulars"]), 12)
        keys = set()

        def walk(x):
            if isinstance(x, dict):
                keys.update(x)
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(night)
        # The truth: who is in the ring, the method, and the ring's own mark on a record.
        self.assertFalse(keys & {"ring", "method", "members", "truth"})


if __name__ == "__main__":
    unittest.main()
