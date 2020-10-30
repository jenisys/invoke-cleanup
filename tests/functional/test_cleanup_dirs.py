# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.cleanup_files()`.
"""

from __future__ import absolute_import, print_function
import stat
from invoke_cleanup import cleanup_dirs
from invoke.util import cd
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir
from tests.path_util import \
    path_is_readable, path_is_writable, path_is_executable, \
    make_path_readonly, path_is_readonly


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
# NOT NEEDED: not_implemented = pytest.mark.skip(reason="Not implemented yet")
class TestCleanupDirs(object):
    """Test :func:`invoke_cleanup.cleanup_files()` function."""

    def test_without_workdir_param_uses_current_directory(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "two.xxx/.ignored",
            "more/ignored.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"two.xxx"
        my_dir3 = tmp_path/"more/ignored.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()
        assert my_dir3.exists() and my_dir3.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        with cd(str(cwd)):  # -- STRING-CONVERSION (needed for: python2.7)
            cleanup_dirs(["*.xxx"])
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert not my_dir2.exists(), "OOPS: my_dir2 was NOT_REMOVED"
        assert my_dir3.exists(), "OOPS: my_dir3 was REMOVED"

    def test_with_one_pattern_in_current_workdir(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "two.xxx/.ignored",
            "more/ignored.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"two.xxx"
        my_dir3 = tmp_path/"more/ignored.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()
        assert my_dir3.exists() and my_dir3.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["*.xxx"], cwd)
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert not my_dir2.exists(), "OOPS: my_dir2 was NOT_REMOVED"
        assert my_dir3.exists(), "OOPS: my_dir3 was REMOVED"

    def test_with_one_pattern_in_current_workdir_subtree(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd)
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert not my_dir2.exists(), "OOPS: my_dir2 was NOT_REMOVED"

    def test_with_one_pattern_in_other_workdir_subtree(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "other/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"other/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], workdir=cwd/"other")
        assert my_dir1.exists(), "OOPS: my_dir1 was REMOVED"
        assert not my_dir2.exists(), "OOPS: my_dir2 was NOT_REMOVED"

    def test_with_two_patterns(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.zzz/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.zzz"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx/", "**/*.zzz/"], cwd)
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert not my_dir2.exists(), "OOPS: my_dir2 was NOT_REMOVED"

    def test_dry_run__should_removes_no_dirs(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd, dry_run=True)
        assert my_dir1.exists(), "OOPS: my_dir1 was REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"

    def test_with_readonly_dir__is_not_removed(self, tmp_path, capsys):
        # -- SETUP:
        # readonly_mode = 0o500   # d.r-x.---.--- (disabled: write-mode)
        readonly_mode = (stat.S_IRUSR | stat.S_IXUSR)
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "readonly.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx/"
        my_dir2 = tmp_path/"readonly.xxx/"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        readonly_dir = my_dir2
        readonly_dir_initial_mode = stat.S_IMODE(readonly_dir.stat().st_mode)
        readonly_dir.chmod(readonly_mode)
        readonly_dir_mode = stat.S_IMODE(readonly_dir.stat().st_mode)
        print("DIAG: readonly_dir.mode= 0o%o" % readonly_dir_mode)
        assert not path_is_writable(readonly_dir)
        assert path_is_readonly(readonly_dir)

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"
        expected = "RMTREE: {0}".format(my_dir2)
        assert expected in captured.out

        # -- CLEANUP:
        readonly_dir.chmod(readonly_dir_initial_mode)

    def test_with_no_permissions_dir__is_not_removed(self, tmp_path, capsys):
        # -- SETUP:
        no_permission_mode = 0o000   # d---.---.--- (NO_PERMISSIONS)
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "no_permission.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx/"
        my_dir2 = tmp_path/"no_permission.xxx/"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        no_permission_dir = my_dir2
        no_permission_initial_mode = stat.S_IMODE(no_permission_dir.stat().st_mode)
        no_permission_dir.chmod(no_permission_mode)
        no_permission_mode = stat.S_IMODE(no_permission_dir.stat().st_mode)
        print("DIAG: no_permission_dir.mode= 0o%o" % no_permission_mode)
        assert not path_is_readable(no_permission_dir)
        assert not path_is_writable(no_permission_dir)
        assert not path_is_executable(no_permission_dir)

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"
        expected = "RMTREE: {0}".format(my_dir2)
        assert expected in captured.out

        # -- CLEANUP:
        no_permission_dir.chmod(no_permission_initial_mode)

    def test_within_readonly_dir__is_not_removed(self, tmp_path, capsys):
        # -- SETUP:
        readonly_mode = 0o555   # dr-xr-xr-x (disabled: write-mode)
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "readonly.dir/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx/"
        readonly_dir = tmp_path/"readonly.dir/"
        my_dir2 = readonly_dir/"two.xxx/"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        readonly_dir_initial_mode = stat.S_IMODE(readonly_dir.stat().st_mode)
        readonly_dir.chmod(readonly_mode)
        readonly_dir_mode = stat.S_IMODE(readonly_dir.stat().st_mode)
        print("DIAG: readonly_dir.mode= 0o%o" % readonly_dir_mode)
        assert path_is_readonly(readonly_dir)

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"
        expected = "RMTREE: {0}".format(my_dir2)
        assert expected in captured.out

        # -- CLEANUP:
        readonly_dir.chmod(readonly_dir_initial_mode)

    def test_within_no_permissions_dir__is_not_removed(self, tmp_path, capsys):
        # -- SETUP:
        no_permission_mode = 0o000   # d---.---.--- (NO_PERMISSIONS)
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "no_permission/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx/"
        no_permission_dir = tmp_path/"no_permission/"
        my_dir2 = no_permission_dir/"two.xxx/"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        no_permission_initial_mode = stat.S_IMODE(no_permission_dir.stat().st_mode)
        no_permission_dir.chmod(no_permission_mode)
        no_permission_mode = stat.S_IMODE(no_permission_dir.stat().st_mode)
        print("DIAG: no_permission_dir.mode= 0o%o" % no_permission_mode)
        assert not path_is_readable(no_permission_dir)
        assert not path_is_writable(no_permission_dir)
        assert not path_is_executable(no_permission_dir)

        # -- EXECUTE AND CLEANUP:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        no_permission_dir.chmod(no_permission_initial_mode)

        # -- VERIFY:
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"
        expected = "RMTREE: {0}".format(my_dir2)
        assert expected not in captured.out, "OOPS: Traversal into NO_PERMISSION.dir"


    def test_without_any_matching_dirs(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.OTHER"], cwd)
        assert my_dir1.exists(), "OOPS: my_dir1 was REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"

    def test_with_exact_name(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.xxx/.ignored"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["more/two.xxx"], cwd)
        assert my_dir1.exists(), "OOPS: my_dir1 was REMOVED"
        assert not my_dir2.exists(), "OOPS: my_dir2 was NOT REMOVED"

    def test_with_matching_file__should_skip_remove(self, tmp_path, capsys):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.xxx"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert my_file2.exists(), "OOPS: my_file2 was REMOVED"

        # -- ONLY IN NON-VERBOSE MODE:
        expected1 = "RMTREE: {0}".format(my_file2)
        expected2 = "REMOVE: {0}".format(my_file2)
        assert expected1 not in captured.out
        assert expected2 not in captured.out

    def test_with_matching_file__should_skip_remove_and_showit_in_verbose_mode(self, tmp_path, capsys):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.ignored",
            "more/two.xxx"
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_dirs(["**/*.xxx"], cwd, verbose=True)
        captured = capsys.readouterr()
        assert not my_dir1.exists(), "OOPS: my_dir1 was NOT_REMOVED"
        assert my_file2.exists(), "OOPS: my_file2 was REMOVED"

        # -- ONLY IN VERBOSE MODE:
        expected = "RMTREE: {0} (SKIPPED: Not a directory)".format(my_file2)
        assert expected in captured.out
