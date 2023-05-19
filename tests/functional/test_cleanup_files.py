# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.cleanup_files()`.
"""

from __future__ import absolute_import, print_function
import sys
import stat
from invoke_cleanup import cleanup_files
from invoke.util import cd
from tests.fspath import fspath_normalize, fspath_normalize_output
import pytest


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
python_version = sys.version_info[:2]
python35 = (3, 5)   # HINT: python3.8 does not raise OSErrors.

ON_WINDOWS = sys.platform == "win32"


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir
from tests.path_util import make_path_readonly, \
    path_is_readonly, path_is_readable, path_is_writable


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestCleanupFiles(object):
    """Test :func:`invoke_cleanup.cleanup_files()` function."""

    def test_without_workdir_param_uses_current_directory(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "two.xxx",
            "more/ignored.xxx",
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"two.xxx"
        my_file3 = tmp_path/"more/ignored.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()
        assert my_file3.exists() and my_file3.is_file()

        # -- EXECUTE AND VERIFY:
        with cd(str(tmp_path)):  # -- STRING-CONVERSION (needed for: python2.7)
            cleanup_files(["*.xxx"])
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"
        assert not my_file2.exists(), "OOPS: my_file2 was NOT_REMOVED"
        assert my_file3.exists(), "OOPS: my_file3 was REMOVED"

    def test_with_one_pattern_in_current_workdir(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "two.xxx",
            "more/ignored.xxx",
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"two.xxx"
        my_file3 = tmp_path/"more/ignored.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()
        assert my_file3.exists() and my_file3.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_files(["*.xxx"], cwd)
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"
        assert not my_file2.exists(), "OOPS: my_file2 was NOT_REMOVED"
        assert my_file3.exists(), "OOPS: my_file3 was REMOVED"

    def test_with_one_pattern_in_current_workdir_subtree(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_files(["**/*.xxx"], cwd)
        assert not my_file1.exists()
        assert not my_file2.exists()

    def test_with_one_pattern_in_other_workdir_subtree(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "other/more/two.xxx"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"other/more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_files(["**/*.xxx"], cwd/"other")
        assert my_file1.exists()
        assert not my_file2.exists()

    def test_with_two_patterns(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.zzz"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.zzz"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_files(["**/*.xxx", "**/*.zzz"], cwd)
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"
        assert not my_file2.exists(), "OOPS: my_file2 was NOT_REMOVED"

    def test_dry_run__should_removes_no_files(self, tmp_path):
        # -- SETUP:
        my_file1 = tmp_path/"one.xxx"
        my_file1.write_text(u"one.xxx")
        assert my_file1.exists() and my_file1.is_file()

        # -- EXECUTE AND VERIFY:
        cwd = tmp_path
        cleanup_files(["*.xxx"], cwd, dry_run=True)
        assert my_file1.exists(), "OOPS: my_file1 was removed."

    @pytest.mark.skipif(ON_WINDOWS, reason="assert NOT my_file1.exists() -- is NOT_REMOVED on Windows")
    def test_with_readonly_file_is_removed(self, tmp_path):
        # -- SETUP:
        readonly_mode = 0o400   # mask: -.r--.---.---
        my_file1 = tmp_path/"one.xxx"
        my_file1.write_text(u"one.xxx")
        my_file1.chmod(readonly_mode)
        make_path_readonly(my_file1)
        assert my_file1.exists() and my_file1.is_file()
        assert path_is_readonly(my_file1)
        file1_mode = stat.S_IMODE(my_file1.stat().st_mode)
        print("DIAG: my_file1.mode= 0o%o" % file1_mode)

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        # with pytest.raises(OSError, match=".* Permission denied:.*"):
        cwd = tmp_path
        cleanup_files(["*.xxx"], cwd)
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"

    @pytest.mark.skipif(ON_WINDOWS, reason="assert NOT my_file1.exists() -- is NOT_REMOVED on Windows")
    def test_with_no_permissions_file_is_removed(self, tmp_path):
        # -- SETUP:
        readonly_mode = 0o000   # mask: -.---.---.--- NO_PERMISSIONS
        my_file1 = tmp_path/"one.xxx"
        my_file1.write_text(u"one.xxx")
        my_file1.chmod(readonly_mode)
        make_path_readonly(my_file1)
        assert my_file1.exists() and my_file1.is_file()
        assert path_is_readonly(my_file1)
        file1_mode = stat.S_IMODE(my_file1.stat().st_mode)
        print("DIAG: my_file1.mode= 0o%o" % file1_mode)

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        cwd = tmp_path
        cleanup_files(["*.xxx"], cwd)
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"

    @pytest.mark.skipif(ON_WINDOWS, reason="assert my_file1 -- Is removed on Windows")
    def test_with_file_in_readonly_dir_is_not_removed(self, tmp_path, capsys):
        # -- SETUP:
        readonly_mode = 0o555   # dr-xr-xr-x (disabled: write-mode)
        setup_workdir(tmp_path, [
            "readonly.dir/one.xxx",
        ])
        my_dir = tmp_path/"readonly.dir"
        my_file1 = my_dir/"one.xxx"
        my_dir.chmod(readonly_mode)
        assert my_file1.exists() and my_file1.is_file()
        my_dir_mode = stat.S_IMODE(my_file1.stat().st_mode)
        print("DIAG: my_dir.mode= 0o%o" % my_dir_mode)
        assert path_is_readable(my_dir)
        assert not path_is_writable(my_dir)

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        # with pytest.raises(OSError, match="Permission denied"):
        cwd = tmp_path
        cleanup_files(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        assert my_file1.exists(), "OOPS: my_file1 was removed."
        if python_version < python35:
            # -- REASON: OSError is not raised for newer py3 versions.
            my_file1_normalized = fspath_normalize(str(my_file1))
            captured_output = fspath_normalize_output(captured.out)
            assert "OSError" in captured.out
            assert "Permission denied:" in captured.out
            assert my_file1_normalized in captured_output

    def test_without_any_matching_files(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        # with pytest.raises(OSError, match="Permission denied"):
        cwd = tmp_path
        cleanup_files(["**/*.zzz"], cwd)
        assert my_file1.exists(), "OOPS: my_file1 was REMOVED"
        assert my_file2.exists(), "OOPS: my_file2 was REMOVED"

    def test_with_exact_name(self, tmp_path):
        remove_pattern = "more/two.xxx"

        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        # with pytest.raises(OSError, match="Permission denied"):
        cwd = tmp_path
        cleanup_files([remove_pattern], cwd)
        assert my_file1.exists(), "OOPS: my_file1 was REMOVED"
        assert not my_file2.exists(), "OOPS: my_file2 was NOT_REMOVED"

    def test_with_matching_directory__should_skip_remove(self, tmp_path, capsys):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx/.dir"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        # with pytest.raises(OSError, match="Permission denied"):
        cwd = tmp_path
        cleanup_files(["**/*.xxx"], cwd)
        captured = capsys.readouterr()
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"

        # -- ONLY IN NON-VERBOSE MODE:
        expected1 = fspath_normalize("REMOVE: {0}".format(my_dir2))
        expected2 = fspath_normalize("RMTREE: {0}".format(my_dir2))
        captured_output = fspath_normalize_output(captured.out)
        assert expected1 not in captured_output
        assert expected2 not in captured_output

        # -- ONLY IN VERBOSE MODE:
        # expected = "REMOVE: {0} (SKIPPED: Not a file)".format(my_dir2)
        # assert expected in captured.out

    def test_with_matching_directory__should_skip_remove_and_showit_in_verbose_mode(self, tmp_path, capsys):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx/.dir"
        ])
        my_file1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_dir2.exists() and my_dir2.is_dir()

        # -- EXECUTE AND VERIFY: Best-effort, ignore read-only file(s)
        # with pytest.raises(OSError, match="Permission denied"):
        cwd = tmp_path
        cleanup_files(["**/*.xxx"], cwd, verbose=True)
        captured = capsys.readouterr()
        assert not my_file1.exists(), "OOPS: my_file1 was NOT_REMOVED"
        assert my_dir2.exists(), "OOPS: my_dir2 was REMOVED"

        # -- ONLY IN VERBOSE MODE:
        expected = fspath_normalize("REMOVE: {0} (SKIPPED: Not a file)".format(my_dir2))
        captured_output = fspath_normalize_output(captured.out)
        assert expected in captured_output
