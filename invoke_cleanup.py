# -*- coding: UTF-8 -*-
"""
Provides cleanup tasks for invoke build scripts (as generic invoke tasklet).
Simplifies writing common, composable and extendable cleanup tasks.

PYTHON PACKAGE DEPENDENCIES:

* path (python >= 3.5) or path.py >= 11.5.0 (as path-object abstraction)
* pathlib (for ant-like wildcard patterns; since: python > 3.5)
* pycmd (required-by: clean_python())


cleanup task: Add Additional Directories and Files to be removed
-------------------------------------------------------------------------------

Create an invoke configuration file (YAML of JSON) with the additional
configuration data:

.. code-block:: yaml

    # -- FILE: invoke.yaml
    # USE: cleanup.directories, cleanup.files to override current configuration.
    cleanup:
        # directories: Default directory patterns (can be overwritten).
        # files:       Default file patterns      (can be ovewritten).
        extra_directories:
            - **/tmp/
        extra_files:
            - **/*.log
            - **/*.bak


Registration of Cleanup Tasks
------------------------------

Other task modules often have an own cleanup task to recover the clean state.
The :meth:`cleanup` task, that is provided here, supports the registration
of additional cleanup tasks. Therefore, when the :meth:`cleanup` task is executed,
all registered cleanup tasks will be executed.

EXAMPLE::

    # -- FILE: tasks/docs.py
    from __future__ import absolute_import
    from invoke import task, Collection
    from invoke_cleanup import cleanup_tasks, cleanup_dirs

    @task
    def clean(ctx):
        "Cleanup generated documentation artifacts."
        dry_run = ctx.config.run.dry
        cleanup_dirs(["build/docs"], dry_run=dry_run)

    namespace = Collection(clean)
    ...

    # -- REGISTER CLEANUP TASK:
    cleanup_tasks.add_task(clean, "clean_docs")
    cleanup_tasks.configure(namespace.configuration())
"""

from __future__ import absolute_import, print_function
import os
import sys
from invoke import task, Collection
from invoke.executor import Executor
from invoke.exceptions import Exit, Failure, UnexpectedExit
from path import Path

# -- PYTHON BACKWARD COMPATIBILITY:
python_version = sys.version_info[:2]
python35 = (3, 5)   # HINT: python3.8 does not raise OSErrors.
if python_version < python35:   # noqa
    import pathlib2 as pathlib
else:
    import pathlib              # noqa


# -----------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------
VERSION = "0.3.5"


# -----------------------------------------------------------------------------
# CLEANUP UTILITIES:
# -----------------------------------------------------------------------------
def execute_cleanup_tasks(ctx, cleanup_tasks):
    """Execute several cleanup tasks as part of the cleanup.

    :param ctx:             Context object for the tasks.
    :param cleanup_tasks:   Collection of cleanup tasks (as Collection).
    """
    # pylint: disable=redefined-outer-name
    executor = Executor(cleanup_tasks, ctx.config)
    failure_count = 0
    for cleanup_task in cleanup_tasks.tasks:
        try:
            print("CLEANUP TASK: %s" % cleanup_task)
            executor.execute(cleanup_task)
        except (Exit, Failure, UnexpectedExit) as e:
            print(e)
            print("FAILURE in CLEANUP TASK: %s (GRACEFULLY-IGNORED)" % cleanup_task)
            failure_count += 1

    if failure_count:
        print("CLEANUP TASKS: %d failure(s) occured" % failure_count)


def cleanup_dirs(patterns, workdir=".", dry_run=False):
    """Remove directories (and their contents) recursively.
    Skips removal if directories does not exist.

    :param patterns:    Directory name patterns, like "**/tmp*" (as list).
    :param workdir:     Current work directory (default=".")
    :param dry_run:     Dry-run mode indicator (as bool).
    """
    current_dir = Path(workdir)
    python_basedir = Path(Path(sys.executable).dirname()).joinpath("..").abspath()
    warn2_counter = 0
    for dir_pattern in patterns:
        for directory in path_glob(dir_pattern, current_dir):
            directory2 = directory.abspath()
            if sys.executable.startswith(directory2):
                # -- PROTECT VIRTUAL ENVIRONMENT (currently in use):
                # pylint: disable=line-too-long
                print("SKIP-SUICIDE: '%s' contains current python executable" % directory)
                continue
            elif directory2.startswith(python_basedir):
                # -- PROTECT VIRTUAL ENVIRONMENT (currently in use):
                # HINT: Limit noise in DIAGNOSTIC OUTPUT to X messages.
                if warn2_counter <= 4:  # noqa
                    print("SKIP-SUICIDE: '%s'" % directory)
                warn2_counter += 1
                continue

            if not directory.isdir():
                print("RMTREE: %s (SKIPPED: Not a directory)" % directory)
                continue

            if dry_run:
                print("RMTREE: %s (dry-run)" % directory)
            else:
                try:
                    # -- MAYBE: directory.rmtree(ignore_errors=True)
                    print("RMTREE: %s" % directory)
                    directory.rmtree_p()
                except OSError as e:
                    print("RMTREE-FAILED: %s (for: %s)" % (e, directory))


def cleanup_files(patterns, workdir=".", dry_run=False):
    """Remove files or files selected by file patterns.
    Skips removal if file does not exist.

    :param patterns:    File patterns, like "**/*.pyc" (as list).
    :param workdir:     Current work directory (default=".")
    :param dry_run:     Dry-run mode indicator (as bool).
    """
    current_dir = Path(workdir)
    python_basedir = Path(Path(sys.executable).dirname()).joinpath("..").abspath()
    error_message = None
    error_count = 0
    for file_pattern in patterns:
        for file_ in path_glob(file_pattern, current_dir):
            if file_.abspath().startswith(python_basedir):
                # -- PROTECT VIRTUAL ENVIRONMENT (currently in use):
                continue
            if not file_.isfile():
                print("REMOVE: %s (SKIPPED: Not a file)" % file_)
                continue

            if dry_run:
                print("REMOVE: %s (dry-run)" % file_)
            else:
                print("REMOVE: %s" % file_)
                try:
                    file_.remove_p()
                except os.error as e:
                    message = "%s: %s" % (e.__class__.__name__, e)
                    print(message + " basedir: "+ python_basedir)
                    error_count += 1
                    if not error_message:
                        error_message = message
    if False and error_message: # noqa
        class CleanupError(RuntimeError):
            pass
        raise CleanupError(error_message)


def path_glob(pattern, current_dir=None):
    """Use pathlib for ant-like patterns, like: "**/*.py"

    :param pattern:      File/directory pattern to use (as string).
    :param current_dir:  Current working directory (as Path, pathlib.Path, str)
    :return Resolved Path (as path.Path).
    """
    if not current_dir: # noqa
        current_dir = pathlib.Path.cwd()
    elif not isinstance(current_dir, pathlib.Path):
        # -- CASE: string, path.Path (string-like)
        current_dir = pathlib.Path(str(current_dir))

    # -- HINT: OSError is no longer raised in pathlib2 or python35.pathlib
    # try:
    for p in current_dir.glob(pattern):
        yield Path(str(p))
    # except OSError as e:
    #     # -- CORNER-CASE 1: x.glob(pattern) may fail with:
    #     # OSError: [Errno 13] Permission denied: <filename>
    #     # HINT: Directory lacks excutable permissions for traversal.
    #     # -- CORNER-CASE 2: symlinked endless loop
    #     # OSError: [Errno 62] Too many levels of symbolic links: <filename>
    #     print("{0}: {1}".format(e.__class__.__name__, e))


# -----------------------------------------------------------------------------
# GENERIC CLEANUP TASKS:
# -----------------------------------------------------------------------------
@task
def clean(ctx):
    """Cleanup temporary dirs/files to regain a clean state."""
    dry_run = ctx.config.run.dry
    directories = list(ctx.config.cleanup.directories or [])
    directories.extend(ctx.config.cleanup.extra_directories or [])
    files = list(ctx.config.cleanup.files or [])
    files.extend(ctx.config.cleanup.extra_files or [])

    # -- PERFORM CLEANUP:
    execute_cleanup_tasks(ctx, cleanup_tasks)
    cleanup_dirs(directories, dry_run=dry_run)
    cleanup_files(files, dry_run=dry_run)

    # -- CONFIGURABLE EXTENSION-POINT:
    # use_cleanup_python = ctx.config.cleanup.use_cleanup_python or False
    # if use_cleanup_python:
    #     clean_python(ctx)


@task(name="all", aliases=("distclean",))
def clean_all(ctx):
    """Clean up everything, even the precious stuff.
    NOTE: clean task is executed last.
    """
    dry_run = ctx.config.run.dry
    directories = list(ctx.config.cleanup_all.directories or [])
    directories.extend(ctx.config.cleanup_all.extra_directories or [])
    files = list(ctx.config.cleanup_all.files or [])
    files.extend(ctx.config.cleanup_all.extra_files or [])

    # -- PERFORM CLEANUP:
    # HINT: Remove now directories, files first before cleanup-tasks.
    cleanup_dirs(directories, dry_run=dry_run)
    cleanup_files(files, dry_run=dry_run)
    execute_cleanup_tasks(ctx, cleanup_all_tasks)
    clean(ctx)

    # -- CONFIGURABLE EXTENSION-POINT:
    # use_cleanup_python1 = ctx.config.cleanup.use_cleanup_python or False
    # use_cleanup_python2 = ctx.config.cleanup_all.use_cleanup_python or False
    # if use_cleanup_python2 and not use_cleanup_python1:
    #     clean_python(ctx)


@task(aliases=["python"])
def clean_python(ctx):
    """Cleanup python related files/dirs: *.pyc, *.pyo, ..."""
    dry_run = ctx.config.run.dry or False
    # MAYBE NOT: "**/__pycache__"
    cleanup_dirs(["build", "dist", "*.egg-info", "**/__pycache__"],
                 dry_run=dry_run)
    if not dry_run:
        ctx.run("py.cleanup")
    cleanup_files(["**/*.pyc", "**/*.pyo", "**/*$py.class"], dry_run=dry_run)


@task(help={
    "path": "Path to cleanup.",
    "interactive": "Enable interactive mode.",
    "force": "Enable force mode.",
    "options": "Additional git-clean options",
})
def git_clean(ctx, path=None, interactive=False, force=False,
              dry_run=False, options=None):
    """Perform git-clean command to cleanup the worktree of a git repository.

    BEWARE: This may remove any precious files that are not checked in.
    WARNING: DANGEROUS COMMAND.
    """
    args = []
    force = force or ctx.config.git_clean.force
    path = path or ctx.config.git_clean.path or "."
    interactive = interactive or ctx.config.git_clean.interactive
    dry_run = dry_run or ctx.config.run.dry or ctx.config.git_clean.dry_run

    if interactive:
        args.append("--interactive")
    if force:
        args.append("--force")
    if dry_run:
        args.append("--dry-run")
    args.append(options or "")
    args = " ".join(args).strip()

    ctx.run("git clean {options} {path}".format(options=args, path=path))


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
CLEANUP_EMPTY_CONFIG = {
    "directories": [],
    "files": [],
    "extra_directories": [],
    "extra_files": [],
    "use_cleanup_python": False,
}
def make_cleanup_config(**kwargs):
    config_data = CLEANUP_EMPTY_CONFIG.copy()
    config_data.update(kwargs)
    return config_data


namespace = Collection(clean_all, clean_python)
namespace.add_task(clean, default=True)
namespace.add_task(git_clean)
namespace.configure({
    "cleanup": make_cleanup_config(
        files=["**/*.bak", "**/*.log", "**/*.tmp", "**/.DS_Store"],
    ),
    "cleanup_all": make_cleanup_config(
        directories=[".venv*", ".tox", "downloads", "tmp"],
    ),
    "git_clean": {
        "interactive": True,
        "force": False,
        "path": ".",
        "dry_run": False,
    },
})


# -- EXTENSION-POINT: CLEANUP TASKS (called by: clean, clean_all task)
# NOTE: Can be used by other tasklets to register cleanup tasks.
cleanup_tasks = Collection("cleanup_tasks")
cleanup_all_tasks = Collection("cleanup_all_tasks")

# -- EXTEND NORMAL CLEANUP-TASKS:
# DISABLED: cleanup_tasks.add_task(clean_python)

# -----------------------------------------------------------------------------
# EXTENSION-POINT: CONFIGURATION HELPERS: Can be used from other task modules
# -----------------------------------------------------------------------------
def config_add_cleanup_dirs(directories):
    # pylint: disable=protected-access
    the_cleanup_directories = namespace._configuration["cleanup"]["directories"]
    the_cleanup_directories.extend(directories)

def config_add_cleanup_files(files):
    # pylint: disable=protected-access
    the_cleanup_files = namespace._configuration["cleanup"]["files"]
    the_cleanup_files.extend(files)
    # namespace.configure({"cleanup": {"files": files}})
    # print("DIAG cleanup.config.cleanup: %r" % namespace.configuration())

def config_add_cleanup_all_dirs(directories):
    # pylint: disable=protected-access
    the_cleanup_directories = namespace._configuration["cleanup_all"]["directories"]
    the_cleanup_directories.extend(directories)

def config_add_cleanup_all_files(files):
    # pylint: disable=protected-access
    the_cleanup_files = namespace._configuration["cleanup_all"]["files"]
    the_cleanup_files.extend(files)
