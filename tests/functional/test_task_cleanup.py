# -*- coding: UTF-8 -*-
"""
Functional tests for :mod:`invoke_cleanup.cleanup` task.
"""

from __future__ import absolute_import, print_function
import os
from contextlib import contextmanager
from invoke import Config, Context
from invoke.util import cd
from invoke_cleanup import cleanup_tasks, \
    config_add_cleanup_dirs, config_add_cleanup_files
import pytest
import coverage


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
from tests.workdir_util import setup_workdir
from tests.invoke_testutil import run, run_with_output, invoke

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
TASKS_FILE_TEMPLATE = """
from invoke import task, Collection
import invoke_cleanup as cleanup

{tasks_frame1}

namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.configure(cleanup.namespace.configuration())
{tasks_frame2}
"""


def make_tasks_text(dest, frame1=None, frame2=None):
    contents = TASKS_FILE_TEMPLATE.format(
        tasks_frame1=frame1 or "", tasks_frame2=frame2 or "")
    return contents


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


# # ---------------------------------------------------------------------------
# # TEST SUITE
# # ---------------------------------------------------------------------------
# not_implemented = pytest.mark.skip(reason="Not implemented yet")
#
# @not_implemented
# class TestCleanupTask(object):
#     def test_use_with_tasks_file(self, tmp_path):
#         return NotImplemented
#
#     def test_use_with_tasks_dir(self, tmpdir):
#         return NotImplemented
#
#
# @not_implemented
# class TestOwnCleanupTask(object):
#     def test_add_cleanup_task(self, tmpdir):
#         return NotImplemented
#
# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
xfail = pytest.mark.xfail()
not_implemented = pytest.mark.skip(reason="Not implemented yet")

class TestCleanupTask(object):
    """Test :func:`invoke_cleanup.clean()` task."""

    def test_invoke_calls_own_cleanup_task(self, tmp_path, capsys):
        # -- SETUP:
        # setup_workdir(tmp_path, [
        #     "one.xxx",
        #     "more/two.xxx",
        # ])
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
                output = run_with_output("invoke cleanup")

        import six
        if not isinstance(output, six.text_type):
            output = output.decode(encoding="UTF-8")
        expected1 = "CLEANUP TASK: foo-clean"
        expected2 = "CALLED: foo_clean"
        assert expected1 in output
        assert expected2 in output

    @xfail
    def test_invoke_removes_own_cleanup_files(self, tmp_path):
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
            output = run_with_output("invoke cleanup")

        assert not my_file1.exists()
        assert not my_file2.exists()
        expected1 = "REMOVE: one.xxx"
        expected2 = "REMOVE: more/two.xxx"
        assert expected1 in output
        assert expected2 in output

    @xfail
    def test_invoke_removes_own_cleanup_dirs(self, tmp_path):
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
            output = run_with_output("invoke cleanup")

        assert not my_dir1.exists()
        assert not my_dir2.exists()
        expected1 = "RMTREE: one.xxx"
        expected2 = "RMTREE: more/two.xxx"
        assert expected1 in output
        assert expected2 in output
