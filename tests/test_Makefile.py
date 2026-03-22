"""Tests for the skills Makefile targets."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


class MakefileTestCase(unittest.TestCase):
    def setUp(self):
        self.work_dir = Path(tempfile.mkdtemp())
        shutil.copy(REPO_ROOT / "Makefile", self.work_dir)
        shutil.copy(REPO_ROOT / "SKILL.template.md", self.work_dir)

    def tearDown(self):
        shutil.rmtree(self.work_dir)

    def run_make(self, *args, env=None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["make", "-s", *args],
            cwd=self.work_dir,
            capture_output=True,
            text=True,
            env=env,
        )

    def output(self, result: subprocess.CompletedProcess) -> str:
        return result.stdout + result.stderr

    def make_stubs(self, *cmds: str) -> dict:
        """Create no-op shell stubs for the given commands and return an env with them on PATH."""
        bin_dir = self.work_dir / "bin"
        bin_dir.mkdir(exist_ok=True)
        for cmd in cmds:
            stub = bin_dir / cmd
            stub.write_text('#!/bin/sh\necho "$0 $@"\n')
            stub.chmod(0o755)
        return {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}


class TestCreatePullRequest(MakefileTestCase):
    def test_fails_when_name_is_missing(self):
        result = self.run_make("create-pull-request")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR", self.output(result))

    def test_creates_branch_and_pr(self):
        env = self.make_stubs("git", "gh")
        result = self.run_make("create-pull-request", "name=my-skill", env=env)
        self.assertEqual(result.returncode, 0)
        out = self.output(result)
        self.assertIn("checkout -b mario/my-skill", out)
        self.assertIn("push -u origin mario/my-skill", out)
        self.assertIn("pr create", out)
        self.assertIn("my-skill", out)


class TestGenerate(MakefileTestCase):
    def test_generates_skill_file(self):
        result = self.run_make("generate", "name=hello")
        skill_file = self.work_dir / ".agents/skills/hello/SKILL.md"
        self.assertEqual(result.returncode, 0)
        self.assertTrue(skill_file.exists())
        self.assertIn("hello", skill_file.read_text())

    def test_fails_when_name_is_missing(self):
        result = self.run_make("generate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR", self.output(result))


class TestValidateFile(MakefileTestCase):
    def test_fails_when_file_arg_omitted(self):
        result = self.run_make("validate-file")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR", self.output(result))

    def test_fails_for_nonexistent_file(self):
        result = self.run_make("validate-file", "file=does_not_exist.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", self.output(result))

    def test_passes_for_existing_file(self):
        (self.work_dir / "ok.md").write_text("hello\n")
        result = self.run_make("validate-file", "file=ok.md")
        self.assertEqual(result.returncode, 0)


class TestValidateLines(MakefileTestCase):
    def test_passes_for_file_with_100_lines(self):
        (self.work_dir / "short.md").write_text("x\n" * 100)
        result = self.run_make("validate-lines", "file=short.md")
        self.assertEqual(result.returncode, 0)

    def test_fails_for_file_with_501_lines(self):
        (self.work_dir / "long.md").write_text("x\n" * 501)
        result = self.run_make("validate-lines", "file=long.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("max 500", self.output(result))


class TestValidateTokens(MakefileTestCase):
    def test_passes_for_small_file(self):
        (self.work_dir / "small.md").write_text("a" * 100)
        result = self.run_make("validate-tokens", "file=small.md")
        self.assertEqual(result.returncode, 0)

    def test_fails_for_file_exceeding_5000_tokens(self):
        (self.work_dir / "large.md").write_text("a" * 20004)
        result = self.run_make("validate-tokens", "file=large.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("max 5000", self.output(result))


class TestValidateDescription(MakefileTestCase):
    def test_passes_for_short_description(self):
        (self.work_dir / "ok.md").write_text("description: short description\n")
        result = self.run_make("validate-description", "file=ok.md")
        self.assertEqual(result.returncode, 0)

    def test_fails_for_description_over_1024_chars(self):
        (self.work_dir / "longdesc.md").write_text(f"description: {'a' * 1024}\n")
        result = self.run_make("validate-description", "file=longdesc.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("too long", self.output(result))

    def test_passes_when_description_field_is_absent(self):
        (self.work_dir / "nodesc.md").write_text("no description field here\n")
        result = self.run_make("validate-description", "file=nodesc.md")
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
