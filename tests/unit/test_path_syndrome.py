"""
Unit tests for :mod:`cmake_build.tasklet.cleanup` module.
"""

from invoke_cleanup import path_glob
import os.path
import sys
import pytest

python_version = sys.version_info[:2]
python35 = (3, 5)   # HINT: python3.8 does not raise OSErrors.

# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
@pytest.mark.filterwarnings(r"ignore:.*(rm_rf) unknown function.*:Warning")
@pytest.mark.filterwarnings(r"ignore:.*(rm_rf) error removing.*:Warning")
class TestSyndrome(object):
    """Test path syndromes that sometimes occur in weird situations."""

    # @pytest.mark.skipif(python_version >= python35, reason="OSError suppressed")
    def test_path_glob__with_not_accessible_directory(self, tmp_path, capsys):
        # -- SETUP: Filesystem
        bad_directory = tmp_path / "not_accessible"
        bad_directory.mkdir()
        good_file1 = tmp_path / "hello_1.txt"
        good_file2 = bad_directory / "hello_2.txt"
        good_file1.write_text(u"hello_1")
        good_file2.write_text(u"hello_2")

        # -- SETUP: PROBLEM-POINT
        mode_not_accessible = 0o000   # mask: d---------
        bad_directory.chmod(mode_not_accessible)

        # -- ACT and VERIFY:
        selected = list(path_glob("**/*.txt", current_dir=tmp_path))
        captured = capsys.readouterr()
        selected2 = [os.path.relpath(p, str(tmp_path)) for p in selected]
        assert selected2 == ["hello_1.txt"]
        if python_version < python35:
            assert "OSError: [Errno 13] Permission denied:" in captured.out
        # -- EXPECT: No OSError exception is raised (only printed).

        # -- CLEANUP: Silence pytest cleanup errors
        bad_directory.chmod(0o777) # CLEANUP: Make accesible again
        good_file1.unlink()
        good_file2.unlink()
        bad_directory.rmdir()
        os.removedirs(str(tmp_path))

    @pytest.mark.skipif(python_version >= python35, reason="OSError suppressed")
    def test_path_glob__with_symlinked_endless_loop(self, tmp_path, capsys):
        """Causes OSError: Recursion limit reached."""
        directory_1 = tmp_path / "d1"
        directory_2 = tmp_path / "d2"
        directory_1.mkdir()
        directory_2.mkdir()

        # -- SYNDROME: Endless symlink loop
        #   d1/point_to_d2.txt -> ../d2/point_to_d1.txt
        #   d2/point_to_d1.txt -> ../d1/point_to_d2.txt
        file_1 = directory_1/"point_to_d2.txt"
        file_2 = directory_2/"point_to_d1.txt"
        file_1.symlink_to("../d2/point_to_d1.txt")
        file_2.symlink_to("../d1/point_to_d2.txt")

        # -- ACT and VERIFY:
        selected = list(path_glob("**/*.txt", current_dir=tmp_path))
        captured = capsys.readouterr()
        selected2 = [os.path.relpath(p, str(tmp_path)) for p in selected]
        # assert selected2 == ["d1/hello_1.txt"]
        # assert "OSError: [Errno 62] Too many levels of symbolic links:" in captured.out
        assert "OSError: " in captured.out
        assert "Too many levels of symbolic links:" in captured.out
        # -- EXPECT: No OSError exception is raised (only printed).

        # -- CLEANUP: Silence pytest cleanup errors => Remove BAD_SYMLINK-Files.
        file_1.unlink()
        file_2.unlink()
