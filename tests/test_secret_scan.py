from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scan_tracked_secrets.py"
SPEC = importlib.util.spec_from_file_location("scan_tracked_secrets", SCRIPT)
scanner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(scanner)


class TrackedSecretScanTests(unittest.TestCase):
    def test_repository_has_no_tracked_secrets(self) -> None:
        self.assertEqual(scanner.scan(), [])

    def test_detects_secret_without_printing_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.example"
            path.write_text("SECRET_KEY=actual-sensitive-value-123456\n", encoding="utf-8")
            with patch.object(scanner, "tracked_files", return_value=[path]), patch.object(scanner, "ROOT", Path(directory)):
                findings = scanner.scan()
        self.assertEqual(findings, [("config.example", "non-placeholder SECRET_KEY")])
        self.assertNotIn("actual-sensitive-value", repr(findings))


if __name__ == "__main__":
    unittest.main()
