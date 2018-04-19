from fabtools.files import uncommented_lines, upload_template
from fabric.api import cd, sudo
from collections import OrderedDict
from fabric.contrib.files import append

def replace(path,  key, value, user='nobody', file_name='.env'):
    with cd(path):
        sudo("touch %s" % file_name, user=user)
        sudo("sed -ibackup '/^%s=/d' %s" %( key, file_name))
        append(file_name, '%s=%s' % (key, value), use_sudo=True)







