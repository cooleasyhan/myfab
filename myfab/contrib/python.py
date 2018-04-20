"""
Python environments and packages
================================

This module provides tools for using Python `virtual environments`_
and installing Python packages using the `pip`_ installer.

.. _virtual environments: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org/

"""

import os
import posixpath
import re
from contextlib import contextmanager
from distutils.version import StrictVersion as V
from pipes import quote

import six
from fabric.api import cd, hide, prefix, run, settings, sudo
from fabric.utils import puts
from fabtools.files import is_file
from fabtools.utils import abspath, download, run_as_root

GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'


def is_installed(package, python_cmd='python', pip_cmd='pip'):
    """
    Check if a Python package is installed (using pip).
    Package names are case insensitive.
    Example::
        from fabtools.python import virtualenv
        import fabtools
        with virtualenv('/path/to/venv'):
            fabtools.python.install('Flask')
            assert fabtools.python.is_installed('flask')
    .. _pip: http://www.pip-installer.org/
    """
    with settings(
            hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = run('%(python_cmd)s -m %(pip_cmd)s freeze' % locals())
    packages = [line.split('==')[0].lower() for line in res.splitlines()]
    return (package.lower() in packages)

def is_pip_installed(version=None, python_cmd='python', pip_cmd='pip'):
    """
    Check if `pip`_ is installed.

    .. _pip: http://www.pip-installer.org/
    """
    with settings(
            hide('running', 'warnings', 'stderr', 'stdout'), warn_only=True):
        res = run('%(python_cmd)s -m %(pip_cmd)s --version 2>/dev/null' % locals())
        if res.failed:
            return False
        if version is None:
            return res.succeeded
        else:
            m = re.search(r'pip (?P<version>.*) from', res)
            if m is None:
                return False
            installed = m.group('version')
            if V(installed) < V(version):
                puts("pip %s found (version >= %s required)" % (
                    installed, version))
                return False
            else:
                return True
