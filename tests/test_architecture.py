import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureTests(unittest.TestCase):
    def test_entry_point_is_small(self):
        source = (ROOT / "TaskPilot.py").read_text(encoding="utf-8")
        self.assertLessEqual(len(source.splitlines()), 40)
        self.assertIn("from taskpilot.app import TaskPilot", source)

    def test_expected_files_exist(self):
        expected = [
            "docs/README.md",
            "docs/ROADMAP.md",
            "docs/CHANGELOG.md",
            "requirements/runtime.txt",
            "requirements/dev.txt",
            "taskpilot/app.py",
            "taskpilot/core/config.py",
            "taskpilot/core/hotkeys.py",
            "taskpilot/core/resources.py",
            "taskpilot/core/target_window.py",
            "taskpilot/modules/clicker.py",
            "taskpilot/modules/keypresser.py",
            "taskpilot/modules/mover.py",
            "taskpilot/modules/ruta.py",
            "taskpilot/modules/rastreador.py",
            "taskpilot/services/input_backend.py",
            "taskpilot/services/tray.py",
            "taskpilot/services/vision.py",
            "taskpilot/services/windows.py",
            "taskpilot/ui/dialogs/settings.py",
            "taskpilot/ui/dialogs/window_selector.py",
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
            (ROOT / "taskpilot/app.py").read_text(encoding="utf-8")
        )
        app_class = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "TaskPilot"
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
            ROOT / "taskpilot/app.py",
            ROOT / "taskpilot/core/hotkeys.py",
            ROOT / "taskpilot/core/target_window.py",
            ROOT / "taskpilot/modules/clicker.py",
            ROOT / "taskpilot/modules/keypresser.py",
            ROOT / "taskpilot/modules/mover.py",
            ROOT / "taskpilot/modules/ruta.py",
            ROOT / "taskpilot/modules/rastreador.py",
            ROOT / "taskpilot/services/input_backend.py",
            ROOT / "taskpilot/services/tray.py",
            ROOT / "taskpilot/ui/dialogs/settings.py",
            ROOT / "taskpilot/ui/dialogs/window_selector.py",
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
        class_files = list((ROOT / "taskpilot").rglob("*.py"))
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
        for path in (ROOT / "taskpilot").rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            if "fusionador" in text or "fusion_" in text:
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
