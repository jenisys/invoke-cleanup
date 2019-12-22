# -*- coding: UTF-8 -*-
"""
Unit tests for :func:`invoke_cleanup.exexecute_cleanup_tasks()`.
"""

from __future__ import absolute_import, print_function
from invoke_cleanup import execute_cleanup_tasks
from invoke import task, Collection, MockContext
import pytest


# ---------------------------------------------------------------------------
# TEST SUITE
# ---------------------------------------------------------------------------
class TestExecuteCleanupTask(object):
    def test_with_task(self, capsys):
        @task
        def my_cleanup(ctx):
            print("CALLED: my_cleanup task")

        cleanup_tasks = Collection("cleanup_tasks")
        cleanup_tasks.add_task(my_cleanup)
        ctx = MockContext()

        execute_cleanup_tasks(ctx, cleanup_tasks)
        captured = capsys.readouterr()
        expected = "CALLED: my_cleanup task"
        assert "CLEANUP TASK: my-cleanup" in captured.out
        assert expected in captured.out

    def test_with_two_tasks(self, capsys):
        @task
        def my_cleanup1(ctx):
            print("CALLED: my_cleanup1 task")
        @task
        def my_cleanup2(ctx):
            print("CALLED: my_cleanup2 task")

        cleanup_tasks = Collection("cleanup_tasks")
        cleanup_tasks.add_task(my_cleanup1)
        cleanup_tasks.add_task(my_cleanup2)
        ctx = MockContext()

        execute_cleanup_tasks(ctx, cleanup_tasks)
        captured = capsys.readouterr()
        expected1 = "CALLED: my_cleanup1 task"
        expected2 = "CALLED: my_cleanup2 task"
        assert "CLEANUP TASK: my-cleanup1" in captured.out
        assert expected1 in captured.out
        assert "CLEANUP TASK: my-cleanup2" in captured.out
        assert expected1 in captured.out

    def test_with_failing_task_raises_exception(self, capsys):
        @task
        def my_cleanup(ctx):
            print("CALLED: my_cleanup task (entered)")
            raise RuntimeError("OOPS: my_cleanup fails")
            print("CALLED: my_cleanup task (exited)")

        cleanup_tasks = Collection("cleanup_tasks")
        cleanup_tasks.add_task(my_cleanup, name="my_cleanup")
        ctx = MockContext()

        with pytest.raises(RuntimeError, match="OOPS: my_cleanup fails"):
            execute_cleanup_tasks(ctx, cleanup_tasks)

        captured = capsys.readouterr()
        expected = "CLEANUP TASK: my-cleanup"
        assert expected in captured.out
        assert "CALLED: my_cleanup task (entered)" in captured.out
        assert "CALLED: my_cleanup task (exited)" not in captured.out
