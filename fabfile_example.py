import copy
import os

from fabric.api import *

from myfab import django, python

PRODUCTION = '192.168.1.2'

RUNING_USER = 'nobody'
GIT_URL = 'https://github.com/cooleasyhan/apitest.git'
GIT_BRANCH = 'dev'
GIT_BASE_ROOT = '/u01'
DJANGO_SETTINGS_MODULE = 'djapi_manager.settings_prod'
IS_INSTALL_MYSQL = True
IS_UPLOAD_PROD_SETTINGS = True
GUNICORN_BIND = '0.0.0.0:8000'


_tmp = copy.copy(locals())
config = {}
for k, v in _tmp.items():
    if k == k.upper():
        config[k] = v


@hosts(PRODUCTION)
def install_python3():
    python.install3_6()


@hosts(PRODUCTION)
def ci():
    django.ci(config)


@hosts(PRODUCTION)
def restart():
    django.restart(config)
