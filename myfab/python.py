from fabtools import require
from fabric.api import sudo, cd, settings,  run, hide
import os

PIP_OPTION = '-i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com/simple '



def _is_install(package, pip_cmd='pip'):

    with settings(
            hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = run('%(pip_cmd)s freeze' % locals())
    packages = [line.split('==')[0].lower() for line in res.splitlines()]
    return (package.lower() in packages)


def install3_6():

    require.rpm.package('python36-devel.x86_64')
    require.rpm.package('python36-tools.x86_64')
    require.rpm.package('python36-libs.x86_64')

    """
    Fix Bug, is_pip_installed
    res = run('%(python_cmd)s -m %(pip_cmd)s --version 2>/dev/null' % locals())
    """
    require.python.pip(python_cmd='python36')

    # if not _is_install('pipenv', pip_cmd='pip3'):
    #     sudo('pip3 install %s pipenv ' % PIP_OPTION)
    require.python.package('pipenv', python_cmd='python36', use_sudo=True)
