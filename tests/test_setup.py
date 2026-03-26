import importlib.util
import sys
import unittest
from pathlib import Path


def load_setup_module():
    module_path = Path(__file__).resolve().parents[1] / "bin" / "setup.py"
    spec = importlib.util.spec_from_file_location("dotfiles_setup", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BrewBundlePlanTests(unittest.TestCase):
    def test_brew_bundle_plan_disables_auto_update_and_upgrade_by_default(self):
        setup = load_setup_module()

        cmd, env, stream = setup._brew_bundle_plan()

        self.assertEqual(cmd[0:2], ["brew", "bundle"])
        self.assertIn("--verbose", cmd)
        self.assertIn("--no-upgrade", cmd)
        self.assertEqual(env["HOMEBREW_NO_AUTO_UPDATE"], "1")
        self.assertTrue(stream)


class BrewLockHintTests(unittest.TestCase):
    def test_brew_lock_hint_detects_concurrent_download_lock(self):
        setup = load_setup_module()

        hint = setup._brew_bundle_lock_hint(
            "Error: A `brew fetch atuin` process has already locked "
            "/Users/test/Library/Caches/Homebrew/downloads/example.incomplete."
        )

        self.assertIsNotNone(hint)
        self.assertIn("Homebrew", hint)
        self.assertIn("pgrep -af brew", hint)


class MiseInstallPlanTests(unittest.TestCase):
    def test_mise_install_plan_uses_yes_and_live_output(self):
        setup = load_setup_module()

        cmd, env, stream = setup._mise_install_plan()

        self.assertEqual(cmd[0:2], ["mise", "install"])
        self.assertIn("-y", cmd)
        self.assertEqual(env["MISE_JOBS"], "1")
        self.assertTrue(stream)


class LegacyToolVersionsTests(unittest.TestCase):
    def test_parse_legacy_tool_versions_sanitizes_asdf_only_tokens(self):
        setup = load_setup_module()

        entries, notes = setup._parse_legacy_tool_versions(
            [
                "python 3.12.3 --home",
                "ruby 3.3.1",
                "nodejs 24.6.0",
                "pnpm 10.6.5 --home",
                "java adoptopenjdk-23.0.2+7 --home",
            ]
        )

        self.assertEqual(entries["python"], "3.12.3")
        self.assertEqual(entries["ruby"], "3.3.1")
        self.assertEqual(entries["node"], "24.6.0")
        self.assertEqual(entries["pnpm"], "10.6.5")
        self.assertEqual(entries["java"], "temurin-23.0.2+7")
        self.assertTrue(any("adoptopenjdk" in note for note in notes))


if __name__ == "__main__":
    unittest.main()
