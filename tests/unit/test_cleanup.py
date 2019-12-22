# -*- coding: UTF-8 -*-
"""
Unit tests for :mod:`invoke_cleanup` module.

.. seealso:: http://docs.pyinvoke.org/en/1.2/concepts/testing.html
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
# TEST SUITE
# ---------------------------------------------------------------------------
not_implemented = pytest.mark.skip(reason="Not implemented yet")

class TestCleanupTask(object):
    @not_implemented
    def test_1(self):
        pass

@not_implemented
class TestCleanupAllTask(object):
    pass

@not_implemented
class TestCleanupFunction(object):
    pass
