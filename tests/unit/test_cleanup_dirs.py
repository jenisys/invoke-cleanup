# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.exexecute_cleanup_tasks()`.
"""

from __future__ import absolute_import, print_function
from invoke_cleanup import cleanup_dirs
from invoke.util import cd
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestCleanupDirs(object):
    def test_skips_rmtree_that_contains_sys_executable(self, tmp_path, monkeypatch, capsys):
        """SKIP-SUICIDE in context of cleanup_dirs in virtual environment."""
        setup_workdir(tmp_path, [
            "foo/one.xxx/python_x.y/bin/python",
        ])
        python_basedir = tmp_path/"foo/one.xxx/python_x.y"
        mock_sys_executable = python_basedir/"bin/python"
        mock_sys_executable = str(mock_sys_executable.absolute())
        problematic_dir = "foo/one.xxx"

        with cd(str(tmp_path)):
            monkeypatch.setattr("sys.executable", mock_sys_executable)
            cleanup_dirs(["**/*.xxx"], dry_run=True)

        # pylint: disable=line-too-long
        captured = capsys.readouterr()
        print(captured.out)
        # expected = "SKIP-SUICIDE: 'foo/one.xxx' contains current python executable"
        expected1 = "SKIP-SUICIDE: '%s'" % problematic_dir
        expected2 = "SKIP-SUICIDE: '%s' contains current python executable" % problematic_dir
        assert expected1 in captured.out
        assert expected2 in captured.out

    def test_skips_rmtree_below_sys_executable_basedir(self, tmp_path, monkeypatch, capsys):
        """SKIP-SUICIDE in context of cleanup_dirs in virtual environment."""
        setup_workdir(tmp_path, [
            "opt/python_x.y/bin/python",
            "opt/python_x.y/lib/foo/one.xxx/.dir"
        ])
        python_basedir = tmp_path/"opt/python_x.y"
        mock_sys_executable = python_basedir/"bin/python"
        mock_sys_executable = str(mock_sys_executable.absolute())
        problematic_dir = python_basedir/"lib/foo/one.xxx"
        problematic_dir = problematic_dir.relative_to(tmp_path)

        with cd(str(tmp_path)):
            monkeypatch.setattr("sys.executable", mock_sys_executable)
            cleanup_dirs(["**/*.xxx"], dry_run=True)

            captured = capsys.readouterr()
            print(captured.out)
            expected = "SKIP-SUICIDE: 'opt/python_x.y/lib/foo/one.xxx'"
            assert expected in captured.out
