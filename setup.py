# -*- coding: UTF-8 -*
"""
Setup script for invoke-cleanup.

USAGE:
    python setup.py install

REQUIRES:
* setuptools >= 36.2.0

SEE ALSO:
* https://setuptools.readthedocs.io/en/latest/history.html
"""


# -- IMPORTS:
import sys
import os.path
from setuptools import find_packages, setup


# -----------------------------------------------------------------------------
# CONFIGURATION:
# -----------------------------------------------------------------------------
HERE = os.path.dirname(__file__)
FIRST_LINE = 8
python_version = float("%s.%s" % sys.version_info[:2])
README = os.path.join(HERE, "README.rst")
description = "".join(open(README).readlines()[FIRST_LINE:])

# -----------------------------------------------------------------------------
# UTILITY:
# -----------------------------------------------------------------------------
def find_packages_by_root_package(where):
    """
    Better than excluding everything that is not needed,
    collect only what is needed.
    """
    root_package = os.path.basename(where)
    packages = [ "%s.%s" % (root_package, sub_package)
                 for sub_package in find_packages(where)]
    packages.insert(0, root_package)
    return packages


# -----------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------
setup(
    name="invoke-cleanup",
    version="0.3.5",
    description="Performs cleanup tasks for the ``invoke`` build system",
    long_description=description,
    author="Jens Engel",
    author_email="jenisys@users.noreply.github.com",
    url="http://github.com/jenisys/invoke-cleanup",
    provides = ["invoke_cleanup"],
    # packages = find_packages_by_root_package("invoke_cleanup"),
    modules = [
        "invoke_cleanup",
        # DISABLED: "invoke_dry_run",   # ADD-ON.
    ],
    # -- REQUIREMENTS:
    # SUPPORT: python2.7, python3.3 (or higher)
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*",
    install_requires=[
        "invoke >= 1.3.0",
        "six >= 1.12.0",
        "pycmd",
        # -- HINT: path.py => path (python-install-package was renamed for python3)
        "path.py >= 11.5.0; python_version <  '3.5'",
        "path >= 13.1.0;    python_version >= '3.5'",
        "pathlib2; python_version < '3.4'",
    ],
    tests_require=[
        "pytest <  5.0; python_version < '3.0'",
        "pytest >= 5.0; python_version >= '3.0'",
        "pytest-html >= 1.19.0",
        "mock >= 2.0",
        "coverage >= 4.2",
        "backports.shutil_which; python_version <= '3.3'",
        # PREPARED: "behave >= 1.2.6",
        # PREPARED: "PyHamcrest >= 1.9",
    ],
    extras_require={
        # PREPARED: 'docs': ["sphinx >= 1.8", "sphinx_bootstrap_theme >= 0.6"],
        'develop': [
            "coverage",
            "pytest <  5.0; python_version < '3.0'",
            "pytest >= 4.0; python_version >= '3.0'",
            "pytest-html >= 1.19.0",
            "tox",
            "modernize >= 0.5",
            "pylint",
            # PREPARED: "behave >= 1.2.6",
            # PREPARED: "PyHamcrest >= 1.9",
        ],
    },
    # MAYBE-DISABLE: use_2to3
    use_2to3= bool(python_version >= 3.0),
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Invoke",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: C++",  # FOR: Intended Audience
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
    ],
    zip_safe = True,
)


