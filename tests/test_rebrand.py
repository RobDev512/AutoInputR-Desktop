import tempfile
import unittest
from pathlib import Path

from taskpilot.core import resources


ROOT = Path(__file__).resolve().parents[1]


class RebrandTests(unittest.TestCase):
    def test_taskpilot_identity(self):
        self.assertEqual(resources.APP_NAME, "TaskPilot")
        self.assertTrue(resources.APP_VERSION.startswith("1.4.0"))
        self.assertTrue((ROOT / "TaskPilot.py").is_file())
        self.assertTrue((ROOT / "taskpilot" / "app.py").is_file())
        self.assertFalse((ROOT / "AutoInputR.py").exists())
        self.assertFalse((ROOT / "autoinputr").exists())

    def test_branding_assets_exist(self):
        for name in [
            "TaskPilotLogo.png",
            "TaskPilotLogoHorizontal.png",
            "TaskPilotIcon.png",
            "TaskPilotLogoTransparent.png",
            "TaskPilotMono.png",
            "TaskPilotIcon.ico",
        ]:
            with self.subTest(name=name):
                self.assertTrue((ROOT / "assets" / "branding" / name).is_file())

        for old_name in ["LogoAIR.png", "Logo2AIR.png", "Logo2AIR.ico"]:
            with self.subTest(old_name=old_name):
                self.assertFalse((ROOT / "assets" / "branding" / old_name).exists())

    def test_autoinputr_install_data_can_be_copied(self):
        names = [
            "CONFIG_FILE",
            "TRACKER_TEMPLATE_FILE",
            "LEGACY_PRODUCT_CONFIG_FILE",
            "LEGACY_PRODUCT_ROOT_CONFIG_FILE",
            "LEGACY_PRODUCT_TRACKER_TEMPLATE_FILE",
            "LEGACY_PRODUCT_ROOT_TRACKER_TEMPLATE_FILE",
        ]
        original = {name: getattr(resources, name) for name in names}

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            old_data = root / "AutoInputR" / "data"
            new_data = root / "TaskPilot" / "data"
            old_data.mkdir(parents=True)

            old_config = old_data / "config.json"
            old_tracker = old_data / "tracker_template.png"
            old_config.write_text('{"from": "AutoInputR"}', encoding="utf-8")
            old_tracker.write_bytes(b"legacy-template")

            try:
                resources.CONFIG_FILE = new_data / "config.json"
                resources.TRACKER_TEMPLATE_FILE = new_data / "tracker_template.png"
                resources.LEGACY_PRODUCT_CONFIG_FILE = old_config
                resources.LEGACY_PRODUCT_ROOT_CONFIG_FILE = root / "AutoInputR" / "config.json"
                resources.LEGACY_PRODUCT_TRACKER_TEMPLATE_FILE = old_tracker
                resources.LEGACY_PRODUCT_ROOT_TRACKER_TEMPLATE_FILE = root / "AutoInputR" / "tracker_template.png"

                resources.migrate_legacy_product_files()

                self.assertEqual(
                    resources.CONFIG_FILE.read_text(encoding="utf-8"),
                    '{"from": "AutoInputR"}',
                )
                self.assertEqual(
                    resources.TRACKER_TEMPLATE_FILE.read_bytes(),
                    b"legacy-template",
                )
                self.assertTrue(old_config.exists())
                self.assertTrue(old_tracker.exists())
            finally:
                for name, value in original.items():
                    setattr(resources, name, value)


if __name__ == "__main__":
    unittest.main()
