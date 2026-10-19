import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureTests(unittest.TestCase):
    def test_entry_point_is_small(self):
        source = (ROOT / "AutoInputR.py").read_text(encoding="utf-8")
        self.assertLessEqual(len(source.splitlines()), 40)
        self.assertIn("from autoinputr.app import AutoInputR", source)

    def test_expected_files_exist(self):
        expected = [
            "docs/README.md",
            "docs/ROADMAP.md",
            "docs/CHANGELOG.md",
            "requirements/runtime.txt",
            "requirements/dev.txt",
            "autoinputr/app.py",
            "autoinputr/core/config.py",
            "autoinputr/core/hotkeys.py",
            "autoinputr/core/resources.py",
            "autoinputr/core/target_window.py",
            "autoinputr/modules/clicker.py",
            "autoinputr/modules/keypresser.py",
            "autoinputr/modules/mover.py",
            "autoinputr/modules/ruta.py",
            "autoinputr/modules/rastreador.py",
            "autoinputr/services/input_backend.py",
            "autoinputr/services/tray.py",
            "autoinputr/services/vision.py",
            "autoinputr/services/windows.py",
            "autoinputr/ui/dialogs/settings.py",
            "autoinputr/ui/dialogs/window_selector.py",
        ]
        for relative in expected:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_legacy_root_project_files_are_not_present(self):
        legacy_root_files = [
            "README.md",
            "ROADMAP.md",
            "CHANGELOG.md",
            "requirements.txt",
            "requirements-dev.txt",
        ]
        present = [name for name in legacy_root_files if (ROOT / name).exists()]
        self.assertEqual(present, [])

    def test_app_uses_expected_mixins(self):
        tree = ast.parse(
            (ROOT / "autoinputr/app.py").read_text(encoding="utf-8")
        )
        app_class = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "AutoInputR"
        )
        bases = [ast.unparse(base) for base in app_class.bases]
        for expected in [
            "RutaMixin",
            "RastreadorMixin",
            "KeyPresserMixin",
            "ClickerMixin",
            "MoverMixin",
            "HotkeysMixin",
            "WindowSelectorMixin",
            "SettingsMixin",
            "TrayMixin",
            "TargetWindowMixin",
            "InputBackendMixin",
            "ctk.CTk",
        ]:
            self.assertIn(expected, bases)


    def test_method_inventory_has_no_duplicates(self):
        class_files = [
            ROOT / "autoinputr/app.py",
            ROOT / "autoinputr/core/hotkeys.py",
            ROOT / "autoinputr/core/target_window.py",
            ROOT / "autoinputr/modules/clicker.py",
            ROOT / "autoinputr/modules/keypresser.py",
            ROOT / "autoinputr/modules/mover.py",
            ROOT / "autoinputr/modules/ruta.py",
            ROOT / "autoinputr/modules/rastreador.py",
            ROOT / "autoinputr/services/input_backend.py",
            ROOT / "autoinputr/services/tray.py",
            ROOT / "autoinputr/ui/dialogs/settings.py",
            ROOT / "autoinputr/ui/dialogs/window_selector.py",
        ]

        owners = {}
        for path in class_files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
                for method in (
                    node for node in cls.body if isinstance(node, ast.FunctionDef)
                ):
                    self.assertNotIn(
                        method.name,
                        owners,
                        msg=f"Metodo duplicado: {method.name}",
                    )
                    owners[method.name] = f"{path.name}:{cls.name}"

        self.assertEqual(len(owners), 192)

    def test_app_self_method_calls_are_resolvable(self):
        class_files = list((ROOT / "autoinputr").rglob("*.py"))
        methods = set()
        calls = set()

        for path in class_files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
                for method in (
                    node for node in cls.body if isinstance(node, ast.FunctionDef)
                ):
                    methods.add(method.name)
                    for node in ast.walk(method):
                        if (
                            isinstance(node, ast.Call)
                            and isinstance(node.func, ast.Attribute)
                            and isinstance(node.func.value, ast.Name)
                            and node.func.value.id == "self"
                        ):
                            calls.add(node.func.attr)

        tkinter_inherited = {
            "after",
            "attributes",
            "deiconify",
            "destroy",
            "focus_force",
            "geometry",
            "iconbitmap",
            "iconify",
            "iconphoto",
            "lift",
            "lower",
            "protocol",
            "resizable",
            "state",
            "title",
            "winfo_screenheight",
            "winfo_screenwidth",
            "withdraw",
        }

        unresolved = sorted(calls - methods - tkinter_inherited)
        self.assertEqual(unresolved, [])

    def test_fusionador_is_not_present(self):
        hits = []
        for path in (ROOT / "autoinputr").rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            if "fusionador" in text or "fusion_" in text:
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
