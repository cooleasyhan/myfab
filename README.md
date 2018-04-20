# myfab

支持django部署
```python
# DEMO fabric file for DJANGO
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

```


```shell
# fab ci
[192.168.1.2] Executing task 'ci'
               PRODUCTION ===>                                       192.168.1.2
              RUNING_USER ===>                                             nobody
                  GIT_URL ===>         https://github.com/cooleasyhan/apitest.git
               GIT_BRANCH ===>                                                dev
            GIT_BASE_ROOT ===>                                               /u01
   DJANGO_SETTINGS_MODULE ===>                        djapi_manager.settings_prod
         IS_INSTALL_MYSQL ===>                                               True
  IS_UPLOAD_PROD_SETTINGS ===>                                               True
            GUNICORN_BIND ===>                                       0.0.0.0:8000
                 APP_NAME ===>                                            apitest
                ROOT_PATH ===>                                       /u01/apitest
       PROD_SETTINGS_FILE ===>                   ./djapi_manager/settings_prod.py
         PROD_TARGET_FILE ===>        /u01/apitest/djapi_manager/settings_prod.py
       DJANGO_WSGI_MODULE ===>                                 djapi_manager.wsgi
[192.168.1.2] Login password for 'yihan':
[192.168.1.2] sudo: mkdir -p /u01
.
.
.
```