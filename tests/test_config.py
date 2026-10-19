import tempfile
import unittest
from pathlib import Path

from autoinputr.core.config import load_config_file, save_config_file


class ConfigTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            config_file = directory / "config.json"
            expected = {
                "enabled": True,
                "number": 123,
                "text": "AutoInputR",
            }
            self.assertTrue(
                save_config_file(
                    expected,
                    config_dir=directory,
                    config_file=config_file,
                )
            )
            self.assertEqual(
                load_config_file(config_file=config_file),
                expected,
            )

    def test_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.json"
            self.assertEqual(load_config_file(config_file=missing), {})


if __name__ == "__main__":
    unittest.main()
