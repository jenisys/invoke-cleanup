# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.cleanup_files()`.
"""

from __future__ import absolute_import, print_function
from invoke import Config, Context
from invoke.util import cd
from invoke_cleanup import git_clean
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir
from tests.invoke_testutil import run
from tests.shell_util import has_program


DEFAULT_CONFIG = Config(defaults={
    "run": {
        "echo": True,
        "pty": False,
        "dry": True,
    },
    "git_clean": {
        "interactive": True,
        "force": False,
        "path": ".",
        "dry_run": False,
    },
})

def mock_read_from_stdin(*args):
    return ""


def git_repo_setup(user_name=None, user_email=None, default_branch="main"):
    user_name = user_name or "test_user"
    user_email = user_email or "{name}@example.com".format(name=user_name)

    run("git config --local init.defaultBranch {branch}".format(branch=default_branch))
    run('git config --local user.email "{email}"'.format(email=user_email))
    run('git config --local user.name "{name}"'.format(name=user_name))


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
requires_git = pytest.mark.skipif(not has_program("git"),
                                  reason="git is not available")


@requires_git
class TestGitCleanTask(object):
    """Test :func:`invoke_cleanup.git_clean()` task."""

    @pytest.mark.parametrize("mode", ["dry_run", "normal"])
    def test_removes_uncommitted_files(self, mode, tmp_path, capsys, monkeypatch):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "two.xxx",
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY:
        Path = tmp_path.__class__
        git_clean_dry_run = (mode == "dry_run")
        curdir = Path(".").resolve()
        with cd(str(tmp_path)):
            work_dir = Path(".").resolve()
            not_in_curdir = not tmp_path.samefile(curdir)
            print("WORK_DIR: %s (work_dir is not CURDIR: %s)" % (work_dir, not_in_curdir))
            assert not_in_curdir, "DANGER_ZONE.SANITY_CHECK_BARRIER.saved_you"

            # with capsys.disabled():
            run("git init")
            git_repo_setup()
            git_dir = tmp_path/".git/"
            assert git_dir.is_dir()
            run('git add one.xxx')
            run('git commit -m"INITIAL" one.xxx')
            run("git status")

            config = Config(DEFAULT_CONFIG)
            ctx = Context(config=config)
            ctx.config.run.dry = False
            ctx.config.git_clean.interactive = False
            monkeypatch.setattr("_pytest.capture.DontReadFromInput.read", mock_read_from_stdin)
            git_clean(ctx, force=True, dry_run=git_clean_dry_run)

        assert my_file1.exists(), "OOPS: my_file1 was REMOVED"
        if git_clean_dry_run:
            # -- DRY-RUN MODE:
            captured = capsys.readouterr()
            assert "Would remove two.xxx" in captured.out
            assert my_file2.exists(), "OOPS: my_file2 was REMOVED"
        else:
            assert not my_file2.exists(), "OOPS: my_file2 was NOT_REMOVED"
