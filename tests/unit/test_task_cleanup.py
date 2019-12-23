# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.clean()` task.
"""

from __future__ import absolute_import, print_function
from invoke import Config, Collection, Result
from invoke import Failure, Exit, UnexpectedExit
from invoke_cleanup import clean, cleanup_tasks
from invoke_cleanup import execute_cleanup_tasks, \
    cleanup_dirs, cleanup_files, make_cleanup_config
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
    "cleanup": make_cleanup_config(
        dirs=["**/xxx"],
        files=["*.bak", "*.log", "*.tmp"],
    ),
})


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
not_implemented = pytest.mark.skip(reason="Not implemented yet")
class TestCleanTask(object):
    """Test configuration logic of :func:`clean()` tasks with Mocks.
    Therefore, no file removal occurs here.
    """

    @pytest.mark.parametrize("mode", ["normal", "dry_run"])
    def test_with_mode(self, mode, monkeypatch):
        dry_run = (mode == "dry_run")
        ctx = EchoMockContext(run=Result(), config=Config(DEFAULT_CONFIG))
        ctx.config.run.dry = dry_run
        ctx.config.cleanup.directories = ["build"]
        ctx.config.cleanup.extra_directories = ["dist"]
        ctx.config.cleanup.files = ["**/*.bak"]
        ctx.config.cleanup.extra_files = ["**/*.log"]

        mock_cleanup_dirs = create_autospec(cleanup_dirs)
        mock_cleanup_files = create_autospec(cleanup_files)
        mock_execute_cleanup_tasks = create_autospec(execute_cleanup_tasks)
        monkeypatch.setattr("invoke_cleanup.cleanup_dirs", mock_cleanup_dirs)
        monkeypatch.setattr("invoke_cleanup.cleanup_files", mock_cleanup_files)
        monkeypatch.setattr("invoke_cleanup.execute_cleanup_tasks",
                            mock_execute_cleanup_tasks)

        mock_other_cleanup_task = create_autospec(clean)
        mock_other_cleanup_task.name = "other_cleanup1"
        the_cleanup_tasks = Collection(mock_other_cleanup_task)
        monkeypatch.setattr("invoke_cleanup.cleanup_tasks", the_cleanup_tasks)

        # -- EXECUTE and VERIFY:
        # pylint: disable=line-too-long
        clean(ctx)
        expected_cleanup_dirs = ["build", "dist"]
        expected_cleanup_files = ["**/*.bak", "**/*.log"]
        mock_execute_cleanup_tasks.assert_called_once_with(ctx, the_cleanup_tasks)
        mock_cleanup_dirs.assert_called_once_with(expected_cleanup_dirs, dry_run=dry_run)
        mock_cleanup_files.assert_called_once_with(expected_cleanup_files, dry_run=dry_run)
        # mock_other_cleanup_task.assert_called_once_with(ctx)

    def test_calls_cleanup_tasks(self, monkeypatch):
        mock_other_cleanup_task1 = create_autospec(clean)
        mock_other_cleanup_task2 = create_autospec(clean)
        mock_other_cleanup_task1.name = "other_cleanup1"
        mock_other_cleanup_task2.name = "other_cleanup2"
        the_cleanup_tasks = Collection()
        the_cleanup_tasks.add_task(mock_other_cleanup_task1, default=False)
        the_cleanup_tasks.add_task(mock_other_cleanup_task2, default=False)
        monkeypatch.setattr("invoke_cleanup.cleanup_tasks", the_cleanup_tasks)

        # -- EXECUTE and VERIFY:
        # pylint: disable=line-too-long
        ctx = EchoMockContext(run=Result(), config=Config(DEFAULT_CONFIG))
        clean(ctx)
        mock_other_cleanup_task1.assert_called_once_with(ctx)
        mock_other_cleanup_task2.assert_called_once_with(ctx)


class TestCleanTaskExtensionPoint(object):

    def test_can_add_own_cleanup_tasks(self, monkeypatch):
        mock_other_cleanup_task = create_autospec(clean)
        mock_other_cleanup_task.name = "other_cleanup"
        the_cleanup_tasks = Collection()
        monkeypatch.setattr("invoke_cleanup.cleanup_tasks", the_cleanup_tasks)

        # -- EXTENSION-POINT:
        from invoke_cleanup import cleanup_tasks
        cleanup_tasks.add_task(mock_other_cleanup_task)

        # -- EXECUTE and VERIFY:
        # pylint: disable=line-too-long
        ctx = EchoMockContext(run=Result(), config=Config(DEFAULT_CONFIG))
        clean(ctx)
        mock_other_cleanup_task.assert_called_once_with(ctx)

    def test_can_add_own_cleanup_dirs(self, monkeypatch):
        ctx = EchoMockContext(run=Result(), config=Config(DEFAULT_CONFIG))
        ctx.config.cleanup.directories = ["build"]
        ctx.config.cleanup.extra_directories = [ "extra_build"]
        mock_cleanup_dirs = create_autospec(cleanup_dirs)
        monkeypatch.setattr("invoke_cleanup.cleanup_dirs", mock_cleanup_dirs)
        monkeypatch.setattr("invoke_cleanup.namespace._configuration", ctx.config)

        # -- EXTENSION-POINT:
        from invoke_cleanup import config_add_cleanup_dirs
        config_add_cleanup_dirs(["other"])

        # -- EXECUTE and VERIFY:
        # pylint: disable=line-too-long
        clean(ctx)
        expected_cleanup_dirs = ["build", "other", "extra_build"]
        mock_cleanup_dirs.assert_called_once_with(expected_cleanup_dirs, dry_run=False)

    def test_can_add_own_cleanup_files(self, monkeypatch):
        ctx = EchoMockContext(run=Result(), config=Config(DEFAULT_CONFIG))
        ctx.config.cleanup.files = ["*.file"]
        ctx.config.cleanup.extra_files = [ "*.extra_file"]
        mock_cleanup_files = create_autospec(cleanup_files)
        monkeypatch.setattr("invoke_cleanup.cleanup_files", mock_cleanup_files)
        monkeypatch.setattr("invoke_cleanup.namespace._configuration", ctx.config)

        # -- EXTENSION-POINT:
        from invoke_cleanup import config_add_cleanup_files
        config_add_cleanup_files(["other_file"])

        # -- EXECUTE and VERIFY:
        # pylint: disable=line-too-long
        clean(ctx)
        expected_cleanup_files = ["*.file", "other_file", "*.extra_file"]
        mock_cleanup_files.assert_called_once_with(expected_cleanup_files, dry_run=False)
