from fabtools import require
from fabric.api import sudo, cd, settings,  run, hide
import os

PIP_OPTION = '-i http://pypi.douban.com/simple/ --trusted-host=pypi.douban.com/simple '

def mkdir(path, user=None, use_sudo=True):
    if use_sudo:
        fun = sudo
    else:
        fun = run
    fun('mkdir -p %s ' %path )
    if user:
        fun('chown %s:%s %s' %(user, user, path))


    

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

    if not _is_install('pipenv', pip_cmd='pip3'):
        sudo('pip3 install %s pipenv ' % PIP_OPTION)
    # require.python.package('pipenv', python_cmd='python36', use_sudo=True)


def ci(remote_url, working_path, branch="master", user='nobody'):
    sudo('mkdir -p %s' % working_path)
    sudo('chown %s:%s %s' % (user, user, working_path))
    with cd(working_path):
        require.git.working_copy(
            remote_url, branch=branch, update=True, use_sudo=True, user=user)


def django_ci(remote_url, working_path, branch="master", user='nobody'):
    ci(remote_url, working_path, branch)
    
    path = remote_url.split('/')[-1]
    if path.endswith('.git'):
        path = path[:-4]

    with cd(os.path.join(working_path, path)):
        if user=='nobody':
            mkdir('/.local', user=user)
            mkdir('/.virtualenvs', user=user)

        sudo('pipenv install', user=user)
        sudo('pipenv run pip install gunicorn ', user=user)
        sudo('pipenv run pip install whitenoise ', user=user)


def _user_is_exists(user_name):

    with settings(
            hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        rst = sudo('pipenv run python manage.py   changepassword %s ' %
                   user_name)
        return rst.succeeded


def django_run(working_path, user='nobody', admin_user='admin'):
    with cd(working_path):
        sudo('pipenv run python manage.py  migrate ', user=user)
        if not _user_is_exists(admin_user):
            sudo('pipenv run python manage.py createsuperuser --username %s ' % admin_user, user=user)

        sudo('pipenv run python manage.py  collectstatic ', user=user)
        sudo("chown -R '%s:%s' ." % (user, user))

        sudo('mkdir -p /data/logs && chown %s:%s /data/logs' % (user, user))

        require.supervisor.process(name='apitest', command='sh gunicorn.sh',
            directory=working_path,
            environment='LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8',
            stdout_logfile_maxbytes='1024MB',
            stdout_logfile_backups=10,
            user=user,
            stdout_logfile='/data/logs/gunicorn_supervisor.log'
        )
