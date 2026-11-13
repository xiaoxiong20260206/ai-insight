import subprocess
import tempfile
import unittest
from pathlib import Path


SCANNER = Path(__file__).with_name("verify_staged_secrets.py")


class StagedSecretScanTests(unittest.TestCase):
    def scan_file(self, filename, content):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            subprocess.run(["git", "init", "-q", directory], check=True)
            (target / filename).write_text(content)
            subprocess.run(["git", "-C", directory, "add", "-f", filename], check=True)
            return subprocess.run(
                ["python3", str(SCANNER)], cwd=directory, capture_output=True, text=True,
            )

    def test_environment_files_are_blocked(self):
        for filename in [".env", ".env.production", ".env.local"]:
            with self.subTest(filename=filename):
                self.assertEqual(self.scan_file(filename, "SETTING=safe").returncode, 1)

    def test_safe_environment_examples_are_allowed(self):
        for filename in [".env.example", ".env.sample"]:
            with self.subTest(filename=filename):
                self.assertEqual(self.scan_file(filename, "SETTING=<value>").returncode, 0)

    def test_examples_with_credentials_remain_blocked(self):
        content = "value=" + "openApp" + "a" * 24
        result = self.scan_file(".env.example", content)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(content, result.stdout)


if __name__ == "__main__":
    unittest.main()
