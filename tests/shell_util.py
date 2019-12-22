# -*- coding: UTF-8 -*-
try:
    from shutil import which    # -- SINCE: Python 3.3
except ImportError:
    from backports.shutil_which import which


def has_program(program_name):
    located = which(program_name)
    return bool(located)


def require_program(program_name):
    located_path = which(program_name)
    if located_path:
        print("FOUND %s: %s" % (program_name, located_path))
    else:
        assert False, "NOT_FOUND: %s" % program_name
