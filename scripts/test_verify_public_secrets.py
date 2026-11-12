import tempfile
import unittest
from pathlib import Path

from verify_public_secrets import find_violations


class PublicSecretScanTests(unittest.TestCase):
    def test_root_git_metadata_is_not_published_content(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".git").mkdir()
            (target / ".git" / "config").touch()
            self.assertEqual(find_violations(target), [])

    def test_secret_in_every_file_type_is_blocked(self):
        for filename in ["client.py", ".env", "config", "data.bin"]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                (target / filename).write_bytes(b"openApp" + b"a" * 24)
                self.assertTrue(find_violations(target))

    def test_nested_git_metadata_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "snapshot" / ".git_disabled").mkdir(parents=True)
            self.assertTrue(find_violations(target))

    def test_documented_placeholder_is_not_a_credential(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "example.py").write_text('api_key="YOUR_DEEPSEEK_API_KEY"')
            self.assertEqual(find_violations(target), [])

    def test_archive_and_oversized_file_are_blocked(self):
        for filename, size in [("backup.zip", 0), ("large.txt", 10 * 1024 * 1024 + 1)]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                target = Path(directory)
                with (target / filename).open("wb") as output:
                    output.truncate(size)
                self.assertTrue(find_violations(target))

    def test_symbolic_link_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "outside").symlink_to(target.parent, target_is_directory=True)
            self.assertTrue(find_violations(target))


if __name__ == "__main__":
    unittest.main()
