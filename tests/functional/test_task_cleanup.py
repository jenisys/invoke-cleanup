# -*- coding: UTF-8 -*-
"""
Functional tests for :mod:`invoke_cleanup.cleanup` task.
"""

from __future__ import absolute_import, print_function
import os
from contextlib import contextmanager
from invoke import Config
from invoke.util import cd
import pytest
import coverage


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir
from tests.invoke_testutil import run_with_output, ensure_text

DEFAULT_CONFIG = Config(defaults={
    "run": {
        "echo": True,
        "pty": False,
        "dry": True,
    },
})


def mock_read_from_stdin(*args):
    return ""



# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
TASKS_FILE_TEXT_USING_CLEANUP_MODULE_ONLY = u"""
from __future__ import absolute_import, print_function
from invoke import task, Collection
import invoke_cleanup as cleanup

namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())
"""

TASKS_FILE_TEMPLATE = """
from invoke import task, Collection
import invoke_cleanup as cleanup

{tasks_frame1}

namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())
{tasks_frame2}
"""


# def make_tasks_text(dest, frame1=None, frame2=None):
#     contents = TASKS_FILE_TEMPLATE.format(
#         tasks_frame1=frame1 or "", tasks_frame2=frame2 or "")
#     return contents


COVERAGE_ENABLED = bool(os.environ.get("COVERAGE_PROCESS_START"))

@contextmanager
def use_subprocess_coverage(workdir=None):
    coverage_collector = None
    if COVERAGE_ENABLED:
        from path import Path
        curdir = Path.getcwd()
        workdir = Path(str(workdir or ".")).abspath()
        coverage_collector = coverage.process_startup()
        print("COVERAGE.use_subprocess_coverage.ENABLED")
    yield coverage_collector
    # -- CLEANUP PHASE:
    if coverage_collector:
        coverage_collector.stop()
        # XXX-CHECK-IF-NEEDED:
        for coverage_file in workdir.walkfiles(".coverage.*"):
            print("COVERAGE.collect: %s" % coverage_file.relpath(workdir))
            coverage_file.move(curdir)
        for coverage_file in workdir.walkfiles(".coverage"):
            print("COVERAGE.collect: %s" % coverage_file.relpath(workdir))
            coverage_file.move(curdir)
        # XXX-CHECK-IF-NEEDED.END
        print("COVERAGE.use_subprocess_coverage.DISABLED")


# ---------------------------------------------------------------------------
# TEST MARKERS
# ---------------------------------------------------------------------------
xfail = pytest.mark.xfail()
not_implemented = pytest.mark.skip(reason="Not implemented yet")
not_necessary = pytest.mark.skip(reason="Not necessary")


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestCleanupTask(object):
    """Test :func:`invoke_cleanup.clean()` task."""

    def test_cleanup_files_without_configfile(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "DEFAULT_FILE.bak",
            "more/DEFAULT_FILE.log",
        ])
        my_file1 = tmp_path / "DEFAULT_FILE.bak"
        my_file2 = tmp_path / "more/DEFAULT_FILE.log"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        tasks_file = tmp_path / "tasks.py"
        tasks_file.write_text(TASKS_FILE_TEXT_USING_CLEANUP_MODULE_ONLY)
        config_file = tmp_path / "invoke.yaml"
        assert not config_file.exists()

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_file1.exists()
        assert not my_file2.exists()
        expected1 = "REMOVE: DEFAULT_FILE.bak"
        expected2 = "REMOVE: more/DEFAULT_FILE.log"
        assert expected1 in output
        assert expected2 in output

    @not_necessary
    def test_cleanup_dirs_without_configfile(self, tmp_path):
        """HINT: cleanup.directories has no default patterns."""

    def test_with_configfile_and_cleanup_files_overrides_default(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "DEFAULT_FILE.bak",
            "one.xxx",
            "more/two.zzz",
        ])
        my_file0 = tmp_path / "DEFAULT_FILE.bak"
        my_file1 = tmp_path / "one.xxx"
        my_file2 = tmp_path / "more/two.zzz"
        assert my_file0.exists() and my_file0.is_file()
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        tasks_file = tmp_path/"tasks.py"
        tasks_file.write_text(TASKS_FILE_TEXT_USING_CLEANUP_MODULE_ONLY)
        config_file = tmp_path/"invoke.yaml"
        config_file.write_text(u"""
cleanup:
    files:
      - "**/*.xxx"
      - "**/*.zzz"
""")

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        assert my_file0.exists(), "OOPS: DEFAULT:cleanup.files pattern was not OVERWRITTEN"
        assert not my_file1.exists()
        assert not my_file2.exists()
        expected1 = "REMOVE: one.xxx"
        expected2 = "REMOVE: more/two.zzz"
        assert expected1 in output
        assert expected2 in output

    def test_with_configfile_and_cleanup_directories_overrides_default(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            # -- HINT: DEFAULT cleanup.directories = [] EMPTY-LIST
            "one.xxx/.dir",
            "more/two.zzz/.dir",
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.zzz"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        tasks_dir = tmp_path/"tasks.py"
        tasks_dir.write_text(TASKS_FILE_TEXT_USING_CLEANUP_MODULE_ONLY)
        config_dir = tmp_path/"invoke.yaml"
        config_dir.write_text(u"""
cleanup:
    directories:
      - "**/*.xxx"
      - "**/*.zzz"
""")

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_dir1.exists()
        assert not my_dir2.exists()
        expected1 = "RMTREE: one.xxx"
        expected2 = "RMTREE: more/two.zzz"
        assert expected1 in output
        assert expected2 in output

    def test_with_configfile_and_cleanup_extra_files_extends_default(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "DEFAULT_FILE.bak",
            "one.xxx",
            "more/two.zzz",
        ])
        my_file0 = tmp_path / "DEFAULT_FILE.bak"
        my_file1 = tmp_path / "one.xxx"
        my_file2 = tmp_path / "more/two.zzz"
        assert my_file0.exists() and my_file0.is_file()
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        tasks_file = tmp_path/"tasks.py"
        tasks_file.write_text(TASKS_FILE_TEXT_USING_CLEANUP_MODULE_ONLY)
        config_file = tmp_path/"invoke.yaml"
        config_file.write_text(u"""
cleanup:
    extra_files:
      - "**/*.xxx"
      - "**/*.zzz"
""")

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_file0.exists(), "OOPS: DEFAULT:cleanup.files was NOT_REMOVED"
        assert not my_file1.exists()
        assert not my_file2.exists()
        expected0 = "REMOVE: DEFAULT_FILE.bak"
        expected1 = "REMOVE: one.xxx"
        expected2 = "REMOVE: more/two.zzz"
        assert expected0 in output
        assert expected1 in output
        assert expected2 in output

    def test_with_configfile_and_cleanup_extra_directories_extends_default(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.dir",
            "more/two.zzz/.dir",
        ])
        my_dir1 = tmp_path/"one.xxx"
        my_dir2 = tmp_path/"more/two.zzz"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        tasks_dir = tmp_path/"tasks.py"
        tasks_dir.write_text(TASKS_FILE_TEXT_USING_CLEANUP_MODULE_ONLY)
        config_dir = tmp_path/"invoke.yaml"
        config_dir.write_text(u"""
cleanup:
    extra_directories:
      - "**/*.xxx"
      - "**/*.zzz"
""")

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_dir1.exists()
        assert not my_dir2.exists()
        expected1 = "RMTREE: one.xxx"
        expected2 = "RMTREE: more/two.zzz"
        assert expected1 in output
        assert expected2 in output


class TestCleanupWithOtherTask(object):
    """Test :func:`invoke_cleanup.clean()` task."""

    def test_invoke_calls_other_cleanup_task(self, tmp_path):
        tasks_file = tmp_path/"tasks.py"
        tasks_file.write_text(u"""
from __future__ import absolute_import, print_function
from invoke import task, Collection
import invoke_cleanup as cleanup

@task
def foo_clean(ctx):
    print("CALLED: foo_clean")

namespace = Collection(foo_clean)
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())

from invoke_cleanup import cleanup_tasks
cleanup_tasks.add_task(foo_clean, name="foo_clean")
cleanup_tasks.configure(namespace.configuration())
""")

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        expected1 = "CLEANUP TASK: foo-clean"
        expected2 = "CALLED: foo_clean"
        assert expected1 in output
        assert expected2 in output

    def test_invoke_calls_other_task_that_uses_cleanup_files(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx",
        ])
        my_file1 = tmp_path / "one.xxx"
        my_file2 = tmp_path / "more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        tasks_file = tmp_path / "tasks.py"
        tasks_file.write_text(u"""
from __future__ import absolute_import, print_function
from invoke import task, Collection
import invoke_cleanup as cleanup
from invoke_cleanup import cleanup_files

@task
def foo_clean(ctx):
    print("CALLED: foo_clean")
    cleanup_files(["**/*.xxx"])

namespace = Collection(foo_clean)
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())

from invoke_cleanup import cleanup_tasks
cleanup_tasks.add_task(foo_clean, name="foo_clean")
cleanup_tasks.configure(namespace.configuration())
""")

        # -- EXECUTE AND VERIFY:
        with use_subprocess_coverage(tmp_path):
            with cd(str(tmp_path)):
                output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_file1.exists()
        assert not my_file2.exists()
        expected1 = "REMOVE: one.xxx"
        expected2 = "REMOVE: more/two.xxx"
        assert expected1 in output
        assert expected2 in output

    def test_invoke_calls_other_task_that_uses_cleanup_dirs(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.dir",
            "more/two.xxx/.dir",
        ])
        my_dir1 = tmp_path / "one.xxx"
        my_dir2 = tmp_path / "more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        tasks_file = tmp_path / "tasks.py"
        tasks_file.write_text(u"""
from __future__ import absolute_import, print_function
from invoke import task, Collection
import invoke_cleanup as cleanup
from invoke_cleanup import cleanup_dirs

@task
def foo_clean(ctx):
    print("CALLED: foo_clean")
    cleanup_dirs(["**/*.xxx"])

namespace = Collection(foo_clean)
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())

from invoke_cleanup import cleanup_tasks
cleanup_tasks.add_task(foo_clean, name="foo_clean")
cleanup_tasks.configure(namespace.configuration())
""")

        # -- EXECUTE AND VERIFY:
        with cd(str(tmp_path)):
            output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_dir1.exists()
        assert not my_dir2.exists()
        expected1 = "RMTREE: one.xxx"
        expected2 = "RMTREE: more/two.xxx"
        assert expected1 in output
        assert expected2 in output

    @xfail
    def test_invoke_removes_other_cleanup_files(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx",
            "more/two.xxx",
        ])
        my_file1 = tmp_path/"one.xxx"
        my_file2 = tmp_path/"more/two.xxx"
        assert my_file1.exists() and my_file1.is_file()
        assert my_file2.exists() and my_file2.is_file()

        tasks_file = tmp_path/"tasks.py"
        tasks_file.write_text(u"""
from __future__ import absolute_import, print_function
from invoke import task, Collection
import invoke_cleanup as cleanup

namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())

from invoke_cleanup import config_add_cleanup_files
config_add_cleanup_files(["**/*.xxx", "one.xxx"])
""")

        # -- EXECUTE AND VERIFY:
        with cd(str(tmp_path)):
            output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_file1.exists()
        assert not my_file2.exists()
        expected1 = "REMOVE: one.xxx"
        expected2 = "REMOVE: more/two.xxx"
        assert expected1 in output
        assert expected2 in output

    @xfail
    def test_invoke_removes_other_cleanup_dirs(self, tmp_path):
        # -- SETUP:
        setup_workdir(tmp_path, [
            "one.xxx/.dir",
            "more/two.xxx/.dir",
        ])
        my_dir1 = tmp_path / "one.xxx"
        my_dir2 = tmp_path / "more/two.xxx"
        assert my_dir1.exists() and my_dir1.is_dir()
        assert my_dir2.exists() and my_dir2.is_dir()

        tasks_file = tmp_path / "tasks.py"
        tasks_file.write_text(u"""
from __future__ import absolute_import, print_function
from invoke import task, Collection
import invoke_cleanup as cleanup

namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())

from invoke_cleanup import config_add_cleanup_dirs
config_add_cleanup_dirs(["**/*.xxx", "one.xxx"])
""")

        # -- EXECUTE AND VERIFY:
        with cd(str(tmp_path)):
            output = ensure_text(run_with_output("invoke cleanup"))

        assert not my_dir1.exists()
        assert not my_dir2.exists()
        expected1 = "RMTREE: one.xxx"
        expected2 = "RMTREE: more/two.xxx"
        assert expected1 in output
        assert expected2 in output
