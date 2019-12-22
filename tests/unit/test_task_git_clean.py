# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.git_clean()` task.
"""

from __future__ import absolute_import, print_function
from invoke_cleanup import git_clean
from invoke import task, Config, Collection, MockContext, Result
from invoke import Failure, Exit, UnexpectedExit
from tests.invoke_testutil import EchoMockContext
import pytest


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = Config(defaults={
    "run": {
        "echo": True,
        "pty": False,
        "dry": False,
    },
    "git_clean": {
        "interactive": True,
        "force": False,
        "path": ".",
        "dry_run": False,
    },
})


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestGitCleanTask(object):
    """Test configuration logic of :func:`git_clean()` tasks with Mock objects.
    Therefore, no file removal occurs here.
    """

    def test_without_options_uses_interactive_mode(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        ctx.config.run.dry = False

        git_clean(ctx)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean --interactive ."
        assert expected in captured.out

    def test_without_options_if_config_disables_interactive_mode(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        ctx.config.git_clean.interactive = False

        git_clean(ctx)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean  ."
        assert expected in captured.out

    def test_with_option_force_on_cmdline(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        # ctx.config.git_clean.interactive = False

        git_clean(ctx, force=True)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean --interactive --force ."
        assert expected in captured.out

    def test_with_option_force_in_configfile(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        # ctx.config.git_clean.interactive = False
        ctx.config.git_clean.force = True

        git_clean(ctx)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean --interactive --force ."
        assert expected in captured.out

    def test_with_invoke_option_dry_on_cmdline(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        ctx.config.run.dry = True  # CMDLINE-EMULATION

        git_clean(ctx)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean --interactive --dry-run ."
        assert expected in captured.out

    def test_with_option_dryrun_on_cmdline(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)

        git_clean(ctx, dry_run=True)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean --interactive --dry-run ."
        assert expected in captured.out

    def test_with_option_dryrun_in_configfile(self, capsys):
        config = Config(DEFAULT_CONFIG)
        ctx = EchoMockContext(run=Result(), config=config)
        # ctx.config.git_clean.interactive = False
        ctx.config.git_clean.dry_run = True

        git_clean(ctx)
        captured = capsys.readouterr()
        expected = "INVOKED: git clean --interactive --dry-run ."
        assert expected in captured.out
