import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SmokeRender(unittest.TestCase):
    def test_renders_a_png(self):
        out = ROOT / "out" / "smoke.png"
        out.unlink(missing_ok=True)
        subprocess.run([sys.executable, str(ROOT / "kit" / "smoke.py")], check=True, capture_output=True)
        self.assertTrue(out.exists())
        self.assertEqual(out.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


class SecretCheck(unittest.TestCase):
    def test_no_secrets_in_tracked_files(self):
        subprocess.run(["node", str(ROOT / ".githooks" / "check-secrets.cjs"), "--all"], check=True, cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
