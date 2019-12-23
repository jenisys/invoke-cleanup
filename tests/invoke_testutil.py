# -*- coding: UTF-8 -*-
"""
Extended test support for testing with invoke.

.. seealso:: http://docs.pyinvoke.org/en/1.3/concepts/testing.html
"""

from __future__ import absolute_import, print_function
import subprocess
from invoke import MockContext


# ---------------------------------------------------------------------------
# TEST SUPPORT
# ---------------------------------------------------------------------------
class EchoMockContext(MockContext):
    """MockContext that echos the "command" in ``ctx.run(command)``."""
    ECHO_PREFIX = "INVOKED: "
    ECHO_MODE = True

    def __init__(self, config=None, **kwargs):
        echo = kwargs.pop("echo", self.ECHO_MODE)
        echo_prefix = kwargs.pop("echo_prefix", self.ECHO_PREFIX)
        super(EchoMockContext, self).__init__(config=config, **kwargs)
        self.config.run.echo = echo
        self.echo = echo
        self.echo_prefix = echo_prefix

    def run(self, command, *args, **kwargs):
        echo = kwargs.pop("echo", False)
        if self.config.run.echo or echo:
            cmd_args = " ".join(args)
            print("{prefix}{command} {args}".format(prefix=self.echo_prefix,
                                             command=command,
                                             args=cmd_args).strip())
        # -- VIRTUAL-CHAIN OF DEFPENDENCY: Delegate to base-class.
        return super(EchoMockContext, self).run(command, *args, **kwargs)


def run(command):
    print("SUBPROCESS.call: %s" % command)
    subprocess.check_call(command, shell=True)


def run_with_output(command):
    print("SUBPROCESS.call: %s" % command)
    return subprocess.check_output(command, shell=True)


def invoke(command):
    run("invoke {0}".format(command))


