# -*- coding: UTF-8 -*-
"""
Functional tests for :mod:`invoke_cleanup.cleanup` task.
"""

from __future__ import absolute_import, print_function
from invoke_cleanup import (
    clean, clean_all,
    cleanup_dirs, cleanup_files,
    cleanup_tasks, cleanup_all_tasks
)
from invoke import MockContext, Result
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
TASKS_FILE_TEMPLATE = """
from invoke import task, Collection
import invoke_cleanup as cleanup

{part_1}

namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
{part_2}
"""


def make_task_file(dest, part_1=None, part_2=None):
    contents = TASKS_FILE_TEMPLATE.format(part_1=part_1, part_2=part_2)
    # XXX-MORE
    return NotImplemented


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
not_implemented = pytest.mark.skip(reason="Not implemented yet")

@not_implemented
class TestCleanupTask(object):
    def test_use_with_tasks_file(self, tmp_path):
        return NotImplemented

    def test_use_with_tasks_dir(self, tmpdir):
        return NotImplemented


@not_implemented
class TestOwnCleanupTask(object):
    def test_add_cleanup_task(self, tmpdir):
        return NotImplemented
