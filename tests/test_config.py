import tempfile
import unittest
from pathlib import Path

from autoinputr.core.config import load_config_file, save_config_file
from autoinputr.core import resources


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

    def test_default_local_data_paths_use_data_directory(self):
        self.assertEqual(resources.CONFIG_FILE.parent.name, "data")
        self.assertEqual(resources.TRACKER_TEMPLATE_FILE.parent.name, "data")

    def test_legacy_local_files_can_be_migrated(self):
        original_values = (
            resources.LEGACY_CONFIG_FILE,
            resources.CONFIG_FILE,
            resources.LEGACY_TRACKER_TEMPLATE_FILE,
            resources.TRACKER_TEMPLATE_FILE,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data = root / "data"
            legacy_config = root / "config.json"
            new_config = data / "config.json"
            legacy_tracker = root / "tracker_template.png"
            new_tracker = data / "tracker_template.png"

            legacy_config.write_text('{"migrated": true}', encoding="utf-8")
            legacy_tracker.write_bytes(b"template")

            try:
                resources.LEGACY_CONFIG_FILE = legacy_config
                resources.CONFIG_FILE = new_config
                resources.LEGACY_TRACKER_TEMPLATE_FILE = legacy_tracker
                resources.TRACKER_TEMPLATE_FILE = new_tracker

                resources.migrate_legacy_local_files()

                self.assertFalse(legacy_config.exists())
                self.assertFalse(legacy_tracker.exists())
                self.assertEqual(new_config.read_text(encoding="utf-8"), '{"migrated": true}')
                self.assertEqual(new_tracker.read_bytes(), b"template")
            finally:
                (
                    resources.LEGACY_CONFIG_FILE,
                    resources.CONFIG_FILE,
                    resources.LEGACY_TRACKER_TEMPLATE_FILE,
                    resources.TRACKER_TEMPLATE_FILE,
                ) = original_values

    def test_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.json"
            self.assertEqual(load_config_file(config_file=missing), {})


if __name__ == "__main__":
    unittest.main()
