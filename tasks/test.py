# -*- coding: UTF-8 -*-
"""
Invoke test tasks.
"""

from __future__ import print_function
import os.path
import sys
from invoke import task, Collection

# -- TASK-LIBRARY:
from invoke_cleanup import cleanup_tasks, cleanup_dirs, cleanup_files


# ---------------------------------------------------------------------------
# TASKS
# ---------------------------------------------------------------------------
@task(name="all", help={
    "args": "Command line args for test run.",
})
def test_all(ctx, args="", options=""):
    """Run all tests (default)."""
    pytest_args = select_by_prefix(args, ctx.pytest.scopes)
    behave_args = select_by_prefix(args, ctx.behave_test.scopes)
    pytest_should_run = not args or (args and pytest_args)
    behave_should_run = not args or (args and behave_args)
    if pytest_should_run:
        pytest(ctx, pytest_args, options=options)
    # if behave_should_run:
    #     behave(ctx, behave_args, options=options)


@task
def clean(ctx):
    """Cleanup (temporary) test artifacts."""
    dry_run = ctx.config.run.dry
    directories = ctx.test.clean.directories or []
    files = ctx.test.clean.files or []
    cleanup_dirs(directories, dry_run=dry_run)
    cleanup_files(files, dry_run=dry_run)


@task(name="unit")
def unittest(ctx, args="", options=""):
    """Run unit tests."""
    pytest(ctx, args, options)


@task
def pytest(ctx, args="", options=""):
    """Run unit tests."""
    args = args or ctx.pytest.args
    options = options or ctx.pytest.options
    ctx.run("pytest {options} {args}".format(options=options, args=args))


# @task(help={
#     "args": "Command line args for behave",
#     "format": "Formatter to use (progress, pretty, ...)",
# })
# # pylint: disable=redefined-builtin
# def behave(ctx, args="", format="", options=""):
#     """Run behave tests."""
#     format = format or ctx.behave_test.format
#     options = options or ctx.behave_test.options
#     args = args or ctx.behave_test.args
#     if os.path.exists("bin/behave"):
#         behave_cmd = "{python} bin/behave".format(python=sys.executable)
#     else:
#         behave_cmd = "{python} -m behave".format(python=sys.executable)
#
#     for group_args in grouped_by_prefix(args, ctx.behave_test.scopes):
#         ctx.run("{behave} -f {format} {options} {args}".format(
#             behave=behave_cmd, format=format, options=options, args=group_args))


@task(iterable=["args", "report"],
    help={
        "args":   "Tests to run (empty: all)",
        "report": "Coverage report format(s) to use (report, html, xml; many)",
})
def coverage(ctx, args="", report="report", append=False):
    """Determine test coverage (run pytest, behave)"""
    append = append or ctx.coverage.append
    coverage_options = []
    if append:
        coverage_options.append("--append")

    pytest_args = select_by_prefix(args, ctx.pytest.scopes)
    pytest_should_run = not args or (args and pytest_args)
    # behave_args = select_by_prefix(args, ctx.behave_test.scopes)
    # behave_should_run = not args or (args and behave_args)
    # if not args:
    #    behave_args = ctx.behave_test.args # DISABLED: or "features"
    if isinstance(pytest_args, list):
        pytest_args = " ".join(pytest_args)
    # if isinstance(behave_args, list):
    #     behave_args = " ".join(behave_args)

    # -- RUN TESTS WITH COVERAGE:
    if pytest_should_run:
        os.environ["COVERAGE_PROCESS_START"] = os.path.abspath(".coveragerc")
        ctx.run("coverage run {options} -m pytest {args}".format(
            args=pytest_args, options=" ".join(coverage_options)))
        os.unsetenv("COVERAGE_PROCESS_START")
        # del os.environ["COVERAGE_PROCESS_START"]
    # if behave_should_run:
    #     behave_options = ctx.behave_test.coverage_options or ""
    #     os.environ["COVERAGE_PROCESS_START"] = os.path.abspath(".coveragerc")
    #     behave(ctx, args=behave_args, options=behave_options)
    #     del os.environ["COVERAGE_PROCESS_START"]

    # -- POST-PROCESSING:
    coverage_report(ctx, report=report)
    # ctx.run("coverage combine")
    # for report_format in report_formats:
    #     ctx.run("coverage {report_format}".format(report_format=report_format))


@task(name="report", aliases=["coverage-report"],
      iterable=["report"],
      help={
        "report": "Coverage report format(s) to use (report, html, xml; many)",
})
def coverage_report(ctx, report=None):
    """Generate test-coverage report(s)."""
    reports = report
    report_formats = reports or ctx.coverage.report_formats or []
    # if report not in report_formats:
    #     report_formats.insert(0, report)

    ctx.run("coverage combine")
    for report_format in report_formats:
        ctx.run("coverage {report_format}".format(report_format=report_format))


# ---------------------------------------------------------------------------
# UTILITIES:
# ---------------------------------------------------------------------------
def select_prefix_for(arg, prefixes):
    for prefix in prefixes:
        if arg.startswith(prefix):
            return prefix
    return os.path.dirname(arg)


def select_by_prefix(args, prefixes):
    selected = []
    for arg in args.strip().split():
        assert not arg.startswith("-"), "REQUIRE: arg, not options"
        scope = select_prefix_for(arg, prefixes)
        if scope:
            selected.append(arg)
    return " ".join(selected)


def grouped_by_prefix(args, prefixes):
    """Group behave args by (directory) scope into multiple test-runs."""
    group_args = []
    current_scope = None
    for arg in args.strip().split():
        assert not arg.startswith("-"), "REQUIRE: arg, not options"
        scope = select_prefix_for(arg, prefixes)
        if scope != current_scope:
            if group_args:
                # -- DETECTED GROUP-END:
                yield " ".join(group_args)
                group_args = []
            current_scope = scope
        group_args.append(arg)
    if group_args:
        yield " ".join(group_args)


# ---------------------------------------------------------------------------
# TASK MANAGEMENT / CONFIGURATION
# ---------------------------------------------------------------------------
namespace = Collection(clean, unittest, pytest, coverage, coverage_report)
namespace.add_task(test_all, default=True)
namespace.configure({
    "test": {
        "clean": {
            "directories": [
                ".pytest_cache",    # -- TEST RUNS
                "__WORKDIR__",      # -- BEHAVE test
            ],
            "files": [
                ".coverage", ".coverage.*",
                "report.html",
                "rerun*.txt", "rerun*.featureset", "testrun*.json",
            ],
        },
    },
    "pytest": {
        "scopes":   ["tests"],
        "args":   "",
        "options": "",  # -- NOTE:  Overide in configfile "invoke.yaml"
    },
    # "behave_test": behave.namespace._configuration["behave_test"],
    "behave_test": {
        "scopes":   [],     # DISABLED: "features", "issue.features"],
        "args":     "",     # DISABLED: ""features issue.features",
        "format":   "progress",
        "options":  "",  # -- NOTE:  Overide in configfile "invoke.yaml"
        "coverage_options": "",
    },
    "coverage": {
        "append":   False,
        "report_formats": ["report", "html"],
    },
})

# -- ADD CLEANUP TASK:
cleanup_tasks.add_task(clean, name="clean_test")
cleanup_tasks.configure(namespace.configuration())
