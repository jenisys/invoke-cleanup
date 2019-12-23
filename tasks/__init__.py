# -*- coding: UTF-8 -*-
# pylint: disable=wrong-import-position, wrong-import-order
"""
Invoke build script.
Show all tasks with::

    invoke -l

.. seealso::

    * http://pyinvoke.org
    * https://github.com/pyinvoke/invoke
"""

from __future__ import absolute_import, print_function

# -----------------------------------------------------------------------------
# BOOTSTRAP PYTHON PATH:
# -----------------------------------------------------------------------------
import os.path
import sys

HERE = os.path.dirname(__file__)
TOPDIR = os.path.join(HERE, "..")
TOPDIR = os.path.abspath(TOPDIR)
sys.path.insert(0, TOPDIR)
sys.path.insert(0, HERE)

# -----------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------
from invoke import task, Collection


# -----------------------------------------------------------------------------
# TASK-LIBRARY:
# -----------------------------------------------------------------------------
import invoke_cleanup as cleanup
from . import test
# DISABLED: from . import release


# -----------------------------------------------------------------------------
# TASKS:
# -----------------------------------------------------------------------------
# None here.


# -----------------------------------------------------------------------------
# TASK CONFIGURATION:
# -----------------------------------------------------------------------------
namespace = Collection()
namespace.add_collection(Collection.from_module(cleanup), name="cleanup")
namespace.add_collection(Collection.from_module(test))
namespace.configure({})

# -- INJECT: cleanup configuration into this namespace
namespace.configure(cleanup.namespace.configuration())
cleanup.cleanup_tasks.add_task(cleanup.clean_python)

if sys.platform.startswith("win"):
    # -- OVERRIDE SETTINGS: For platform=win32, ... (Windows)
    from ._compat_shutil import which
    run_settings = dict(echo=True, pty=False, shell=which("cmd"))
    namespace.configure({"run": run_settings})
else:
    namespace.configure({"run": dict(echo=True, pty=True)})
