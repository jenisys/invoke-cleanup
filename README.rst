invoke-tasklet-cleanup
=============================================================================

.. _`invoke-tasklet-cleanup`: https://github.com/jenisys/invoke-tasklet-cleanup
.. _invoke: https://pyinvoke.org


`invoke-tasklet-cleanup`_ provides common cleanup tasks (and simple dry-run support)
for the `invoke`_ build system.

`invoke`_ provides a modular build system.
This means that each module (or namespace) should also provide its ``clean`` or
``cleanup`` task. But in addition, you often want a common ``cleanup`` task
that calls somehow the cleanup task in each module. This functionality is provided
by the `invoke-tasklet-cleanup`_.

`invoke-tasklet-cleanup`_ provides two tasks and a number of helper functions
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



EXAMPLE: Use common cleanup tasks
------------------------------------------------------------------------------

The following code snippets show how `invoke-tasklet-cleanup`_ tasks
should be used in your own invoke tasks:

.. code-block:: python

    # -- FILE: tasks/__init__.py or tasks.py
    from invoke import Collection, task

    # -- USE TASKLET-LIBRARY:
    import invoke_tasklet_cleanup as cleanup

    ...     # More tasks here.

    # -----------------------------------------------------------------------------
    # TASK CONFIGURATION:
    # -----------------------------------------------------------------------------
    namespace = Collection()
    namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
    ...


EXAMPLE: Override and extend the invoke configuration settings.

.. code-block:: yaml

    # -- FILE: invoke.yaml
    # USE: cleanup.directories, cleanup.files to override current configuration.
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


EXAMPLE: Add own, specific cleanup task to common cleanup tasks.
------------------------------------------------------------------------------

The following snippet shows how you can register own cleanup tasks
that should be executed when the common cleanup tasks are executed.

.. code-block:: python

    # -- FILE: tasks/docs.py
    from __future__ import absolute_import
    from invoke import task, Collection
    from invoke_tasklet_cleanup import cleanup_tasks, cleanup_dirs

    @task
    def clean(ctx, dry_run=False):
        """Cleanup generated documentation artifacts."""
        cleanup_dirs(["build/docs"])

    namespace = Collection(clean)
    ...

    # -- REGISTER CLEANUP TASK:
    # ENSURE: "clean_docs" is executed when common "cleanup" task is performed.
    cleanup_tasks.add_task(clean, "clean_docs")
    cleanup_tasks.configure(namespace.configuration())


.. hint::

    You can use:

    * ``invoke docs.clean`` to cleanup only created docs artifacts.
    * ``invoke cleanup`` to perform its cleanup and call other tasks,
      like ``docs.clean``task, too.
