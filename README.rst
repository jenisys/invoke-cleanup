invoke-cleanup
=============================================================================

.. _`invoke-cleanup`: https://github.com/jenisys/invoke-cleanup
.. _invoke: https://pyinvoke.org


`invoke-cleanup`_ provides common cleanup tasks for the `invoke`_ build system.

`invoke`_ provides a modular build system.

* This means that each module (or namespace) can / should also provide its
  ``clean`` or ``cleanup`` task.

* In addition, you often want a common ``cleanup`` task
  that somehow cleans up everything and can call the cleanup task in each module.

Because the *cleanup-everything* functionality is generic and
the cleanup tasks are often project specific,
the generic cleanup functionality provides a mechanism that allows the
specific cleanup tasks to register themselves.


Functionality of `invoke-cleanup`_
------------------------------------------------------------------------------

This following functionality is provided by the `invoke-cleanup`_.

`invoke-cleanup`_ provides two tasks and a number of helper functions
to simplify the implementation of cleanup tasks.

Tasks (when registered as shown below):

* ``cleanup`` to cleanup the basic things (normal cleanup)
* ``cleanup.all`` to cleanup everything even the precious artifacts (spotless cleanup)

Helper functions (for other cleanup tasks as well):

* ``cleanup_dirs(list_of_dirs_or_dir_patterns)``
* ``cleanup_files(list_of_files_or_file_patterns)``

Module attributes:

* ``cleanup_tasks`` to append additional cleanup tasks for common ``cleanup`` task
* ``cleanup_all_tasks`` to append additional cleanup tasks for common ``cleanup.all`` task



EXAMPLE: Use invoke-cleanup for common cleanup tasks
------------------------------------------------------------------------------

The following code snippet show how `invoke-cleanup`_ tasks
can used in your own invoke tasks file or tasks directory:

.. code-block:: python

    # -- FILE: tasks.py or tasks/__init__.py
    from invoke import Collection, task

    # -- USE TASKLET-LIBRARY:
    import invoke_cleanup as cleanup

    ...     # More tasks here.

    # -----------------------------------------------------------------------------
    # TASK CONFIGURATION:
    # -----------------------------------------------------------------------------
    namespace = Collection()
    namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
    ...


EXAMPLE: Override or extend the invoke configuration settings
------------------------------------------------------------------------------

The cleanup settings can be overwritten and extended in the config-file:

.. code-block:: yaml

    # -- FILE: invoke.yaml
    # USE:
    #   * cleanup.directories, cleanup.files to override current configuration.
    #   * cleanup.extra_directories, cleanup.extra_files to extend current config.
    cleanup:
        extra_directories:
            - **/tmp/
        extra_files:
            - **/*.log
            - **/*.bak

    cleanup_all:
        extra_directories:
            - .tox
            - .venv*
        # OR: extra_files:
        #    - **/*.log
        #    - **/*.bak


.. note:: Search patterns ``**/*.<suffix>`` vs ``*.<suffix>``

    `Ant`_ like search patterns ``**/*.<suffix>`` are used
    to search for file or directories in a directory tree
    (provide by the `pathlib`_ module).

    For example, use ``**/*.txt`` to search for all text files (``*.txt``)
    within the current directory and below.
    The normal search pattern ``*.txt`` applies only to the current
    (or one) directory.

.. _Ant: https://ant.apache.org/
.. _pathlib: https://docs.python.org/3/library/pathlib.html#basic-use


EXAMPLE: Add invoke-cleanup to your invoke tasks
------------------------------------------------------------------------------

The following examples shows how you can add `invoke-cleanup`_
to your ``tasks.py`` file or ``tasks/__init__.py`` file (in your tasks directory):

.. code-block:: python

    # -- FILE: tasks.py
    # -- FILE: tasks/__init__.py
    from __future__ import absolute_import, print_function
    from invoke import task, Collection
    import invoke_cleanup as cleanup

    @task
    def hello(ctx, name=None):
        """Hello ..."""
        print("Hello {}".format(name or "Alice"))

    namespace = Collection(hello)
    namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
    namespace.configure({
        # ...
    })
    namespace.configure(cleanup.namespace.configuration())


EXAMPLE: Add own, specific cleanup task to common cleanup tasks.
------------------------------------------------------------------------------

The following snippet shows how you can register own cleanup tasks
that should be executed when the common cleanup tasks are executed.

.. code-block:: python

    # -- FILE: tasks/docs.py
    from __future__ import absolute_import
    from invoke import task, Collection
    from invoke_cleanup import cleanup_tasks, cleanup_dirs

    @task
    def clean(ctx):
        """Cleanup generated documentation artifacts."""
        dry_run = ctx.config.run.dry
        cleanup_dirs(["build/docs"], dry_run=dry_run)

    namespace = Collection(clean)
    ...

    # -- REGISTER CLEANUP TASK:
    # ENSURE: "clean_docs" is executed when "invoke cleanup" task is executed.
    cleanup_tasks.add_task(clean, name="clean_docs")
    cleanup_tasks.configure(namespace.configuration())

    # -- ALTERNATIVE: cleanup_all_tasks:
    # Then cleanup task is called with "invoke cleanup.all"


.. hint::

    You can use:

    * ``invoke docs.clean`` to cleanup only created docs artifacts.
    * ``invoke cleanup`` to perform its cleanup and call other tasks,
      like the ``docs.clean`` task.


EXAMPLE: Use invoke dry-run support
------------------------------------------------------------------------------

:Since: invoke-1.3.0

A common dry-run support was added in one of the latest versions of `invoke`_.
This common dry-run mode is supported by `invoke-cleanup`_.
This allows you to ask **WHAT IF ...** questions and allows to inspect
what occurs when the ``cleanup`` or ``cleanup.all`` task is executed:

.. code-block:: shell

    $ invoke --dry cleanup
    RMTREE: xxx_dir_1 (dry-run)
    RMTREE: xxx_dir_2 (dry-run)
    ...
    REMOVE: xxx_file_1 (dry-run)
    REMOVE: xxx_file_2 (dry-run)
    ...
    CLEANUP TASK: python
    CLEANUP TASK: clean-docs
    ...

    $ invoke --dry cleanup.all
    RMTREE: xxx_dirall_1 (dry-run)
    ...

    # -- HINT: Shows WHAT-IF ...
    #   * No directories or files are removed, only impact is shown.
    #   * No cleanup tasks are executed, only impact is shown.

.. note::

    The **dry-run mode** is especially useful when you add new cleanup tasks
    and you are not quite sure that the cleanup task does not clean up too much.
