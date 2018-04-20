import fabtools
from .require import supervisor
from . import python
def mock():
    fabtools.require.supervisor.process  = supervisor.process
    fabtools.python.is_pip_installed = python.is_pip_installed
    fabtools.python.is_installed = python.is_installed