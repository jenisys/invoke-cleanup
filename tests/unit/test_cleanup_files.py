# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.exexecute_cleanup_tasks()`.
"""

from __future__ import absolute_import, print_function
from invoke_cleanup import cleanup_files
from invoke.util import cd
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestCleanupFiles(object):
    def test_skips_remove_below_sys_executable_basedir(self, tmp_path, monkeypatch, capsys):
        """SKIP-SUICIDE in context of cleanup_dirs in virtual environment."""
        setup_workdir(tmp_path, [
            "opt/python_x.y/bin/python",
            "opt/python_x.y/foo/one.xxx",
            "foo2/two.xxx"
        ])
        python_basedir = tmp_path/"opt/python_x.y"
        mock_sys_executable = python_basedir/"bin/python"
        mock_sys_executable = str(mock_sys_executable.absolute())
        problematic_file = python_basedir/"foo/one.xxx"
        problematic_file = problematic_file.relative_to(tmp_path)

        with cd(str(tmp_path)):
            monkeypatch.setattr("sys.executable", mock_sys_executable)
            cleanup_files(["**/*.xxx"], dry_run=True)

            captured = capsys.readouterr()
            print(captured.out)
            expected = "REMOVE: %s" % problematic_file
            assert expected not in captured.out

    def test_remove_raises_oserror(self, tmp_path, monkeypatch, capsys):
        def mock_remove(p):
            raise OSError("MOCK_REMOVE: %s" % p)

        setup_workdir(tmp_path, [
            "foo/one.xxx",
            "more/two.xxx",
        ])
        problematic_file1 = tmp_path/"foo/one.xxx"
        problematic_file1 = problematic_file1.relative_to(tmp_path)
        problematic_file2 = tmp_path/"more/two.xxx"
        problematic_file2 = problematic_file2.relative_to(tmp_path)

        with cd(str(tmp_path)):
            monkeypatch.setattr("path.Path.remove_p", mock_remove)
            cleanup_files(["**/*.xxx"])

            captured = capsys.readouterr()
            print(captured.out)
            expected1 = "REMOVE: %s" % problematic_file1
            expected2 = "OSError: MOCK_REMOVE: %s" % problematic_file1
            assert expected1 in captured.out
            assert expected2 in captured.out
            expected2 = "OSError: MOCK_REMOVE: %s" % problematic_file2
            assert expected2 in captured.out
