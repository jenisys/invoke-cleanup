# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.clean_python()` task.
"""

from __future__ import absolute_import, print_function
from invoke_cleanup import clean_python, cleanup_dirs, cleanup_files
from invoke import task, Config, Collection, MockContext, Result
from invoke import Failure, Exit, UnexpectedExit
from tests.invoke_testutil import EchoMockContext
import pytest
from mock import create_autospec


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = Config(defaults={
    "run": {
        "echo": True,
        "pty": False,
        "dry": False,
    },
})

DEFAULT_KWARGS = dict(workdir=".", verbose=False)
EXPECTED_CLEANUP_DIRS = ["build", "dist", "*.egg-info", "**/__pycache__"]
EXPECTED_CLEANUP_FILES = ["**/*.pyc", "**/*.pyo", "**/*$py.class"]


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestCleanPythonTask(object):
    """Test configuration logic of :func:`clean_python()` tasks with Mocks.
    Therefore, no file removal occurs here.
    """

    def test_normal_mode(self, monkeypatch):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        ctx.config.run.dry = False

        mock_cleanup_dirs = create_autospec(cleanup_dirs)
        mock_cleanup_files = create_autospec(cleanup_files)
        # mock_invoke_run = create_autospec(ctx.run)
        monkeypatch.setattr("invoke_cleanup.cleanup_dirs", mock_cleanup_dirs)
        monkeypatch.setattr("invoke_cleanup.cleanup_files", mock_cleanup_files)


        clean_python(ctx)
        mock_cleanup_dirs.assert_called_once_with(EXPECTED_CLEANUP_DIRS, dry_run=False, **DEFAULT_KWARGS)
        mock_cleanup_files.assert_called_once_with(EXPECTED_CLEANUP_FILES, dry_run=False, **DEFAULT_KWARGS)
        # mock_invoke_run.assert_called_once_with("py.cleanup")

    def test_dryrun_mode(self, monkeypatch):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(config=config)
        ctx.config.run.dry = True

        mock_cleanup_dirs = create_autospec(cleanup_dirs)
        mock_cleanup_files = create_autospec(cleanup_files)
        # mock_invoke_run = create_autospec(EchoMockContext.run)
        monkeypatch.setattr("invoke_cleanup.cleanup_dirs", mock_cleanup_dirs)
        monkeypatch.setattr("invoke_cleanup.cleanup_files", mock_cleanup_files)

        clean_python(ctx)
        mock_cleanup_dirs.assert_called_once_with(EXPECTED_CLEANUP_DIRS, dry_run=True, **DEFAULT_KWARGS)
        mock_cleanup_files.assert_called_once_with(EXPECTED_CLEANUP_FILES, dry_run=True, **DEFAULT_KWARGS)
        # assert mock_invoke_run.called == 0, "OOPS: ctx.run() was called"

