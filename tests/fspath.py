"""
"""

from __future__ import absolute_import, print_function
import six
if six.PY2:
    from pathlib2 import Path
else:
    from pathlib import Path


def fspath_normalize_output(text):
    # -- POSIX-PATH NORMALIZATION: For Windows paths
    assert isinstance(text, six.string_types)
    normalized_text = text.replace("\\", "/")
    return normalized_text

def fspath_normalize(path):
    if isinstance(path, six.string_types):
        return fspath_normalize_output(path)
    elif not isinstance(path, Path):
        raise TypeError("%r (expected: string, Path)" % path)

    # -- POSIX-PATH NORMALIZATION: For Windows paths
    return str(path).replace("\\", "/")
