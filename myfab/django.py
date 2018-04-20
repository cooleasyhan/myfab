import copy
import os
import time

from fabric.api import *
from fabric.contrib.files import exists, upload_template
from fabtools import require, supervisor
from fabtools.system import cpus

from . import envfile, git, mysql, python, utils

try:
    from io import StringIO
except:
    from StringIO import StringIO


def working_copy(remote_url, working_path, branch="master", user='nobody'):
    git.working_copy(remote_url, working_path, branch)

    path = remote_url.split('/')[-1]
    if path.endswith('.git'):
        path = path[:-4]

    with cd(os.path.join(working_path, path)):
        if user == 'nobody':
            utils.mkdir('/.local', user=user)
            utils.mkdir('/.virtualenvs', user=user)

        sudo('pipenv install', user=user)
        sudo('pipenv run pip install gunicorn ', user=user)
        sudo('pipenv run pip install whitenoise ', user=user)


def default_gunicorn_sh(context, timeout=600, file_name='gunicorn.sh'):
    num_workers = cpus()
    file_name = os.path.join(context['ROOT_PATH'], file_name)
    text = '''
#!/usr/bin/env bash

#!/bin/bash

NAME="{APP_NAME}" # Name of the application
USER={RUNING_USER} # the user to run as
GROUP={RUNING_USER} # the group to run as
NUM_WORKERS={num_workers} # how many worker processes should Gunicorn spawn
TIMEOUT={timeout}
DJANGO_WSGI_MODULE={DJANGO_WSGI_MODULE} # WSGI module name

echo "Starting $NAME as `whoami`"

exec pipenv run gunicorn $DJANGO_WSGI_MODULE:application \\
--name $NAME \\
--workers $NUM_WORKERS \\
--timeout $TIMEOUT \\
--user=$USER --group=$GROUP \\
--bind={GUNICORN_BIND} \\
--log-level=debug \\
--log-file=-

    '''
    text = text.format(num_workers=num_workers, timeout=timeout,  **context)
    return put(
        local_path=StringIO(text),
        remote_path=file_name,
        use_sudo=True,
        mode=644,
        temp_dir='/tmp'
    )


def add_supervisor(working_path, app_name, user):

    sudo("chown -R '%s:%s' %s " % (user, user, working_path))

    utils.mkdir('/data/logs', user=user)
    sudo('chmod +rwx %s' % os.path.join(working_path, 'gunicorn.sh'), user=user)
    require.supervisor.process(name=app_name, command='sh gunicorn.sh',
                               directory=working_path,
                               environment='LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8',
                               stdout_logfile_maxbytes='1024MB',
                               stdout_logfile_backups=10,
                               user=user,
                               stdout_logfile='/data/logs/gunicorn_supervisor.log'
                               )


def prepare(working_path, user='nobody'):
    with cd(working_path):
        sudo('pipenv run python manage.py  migrate ', user=user)

        sudo('pipenv run python manage.py  collectstatic --noinput ', user=user)

        sudo('pipenv run python manage.py check ', user=user)

        sudo('pipenv run python manage.py test', user=user)


def createsuperuser(username='admin', user='nobody'):
    sudo('pipenv run python manage.py createsuperuser --username %s ' %
         admin_user, user=user)


def _get_app_name(git_url):
    app_name = git_url.split(
        '/')[-1]
    if app_name.endswith('.git'):
        return app_name[:-4]

    return app_name


def ci(config):
    '''
    RUNING_USER = 'nobody'
    GIT_URL = 'https://github.com/cooleasyhan/apitest.git'
    GIT_BRANCH = 'dev'
    GIT_BASE_ROOT = '/u01'
    DJANGO_SETTINGS_MODULE = 'djapi_manager.context_prod'
    IS_INSTALL_MYSQL = True
    IS_UPLOAD_PROD_SETTINGS = True
    GUNICORN_BIND = '0.0.0.0:8000'
    '''

    context = copy.copy(config)

    context['APP_NAME'] = _get_app_name(config['GIT_URL'])

    context['ROOT_PATH'] = os.path.join(
        context['GIT_BASE_ROOT'], context['APP_NAME'])

    context['PROD_SETTINGS_FILE'] = os.path.join(
        os.path.curdir,  *context['DJANGO_SETTINGS_MODULE'].split('.')) + '.py'
    context['PROD_TARGET_FILE'] = os.path.join(
        context['ROOT_PATH'], *context['DJANGO_SETTINGS_MODULE'].split('.')) + '.py'

    context['DJANGO_WSGI_MODULE'] = context['DJANGO_SETTINGS_MODULE'].split('.')[
        0] + '.wsgi'

    for key, value in context.items():
        print(key.rjust(25), '===>', str(value).rjust(50))

    # Install mysql client
    if context['IS_INSTALL_MYSQL']:
        mysql.mysql_client()

    # Git pull, install pipenv , and install same python production libs
    working_copy(context['GIT_URL'], context['GIT_BASE_ROOT'],
                 branch=context['GIT_BRANCH'], user=context['RUNING_USER'])

    # update .env
    envfile.replace(context['ROOT_PATH'], 'DJANGO_SETTINGS_MODULE',
                    context['DJANGO_SETTINGS_MODULE'], user=context['RUNING_USER'])

    # update prod setting files
    if context['IS_UPLOAD_PROD_SETTINGS']:
        upload_template(context['PROD_SETTINGS_FILE'],
                        context['PROD_TARGET_FILE'], use_sudo=True)

    # prepare django
    prepare(
        working_path=context['ROOT_PATH'], user=context['RUNING_USER'])

    if not exists(os.path.join(context['ROOT_PATH'], 'gunicorn.sh')):
        default_gunicorn_sh(context)

    # do supervisor
    add_supervisor(working_path=context['ROOT_PATH'],
                   app_name=context['APP_NAME'], user=context['RUNING_USER'])

    

def restart(config):
    app_name = _get_app_name(config['GIT_URL'])
    supervisor.restart_process(app_name)
    time.sleep(1)
    print(app_name, 'status:', supervisor.process_status(app_name))
