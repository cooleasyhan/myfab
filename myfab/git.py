from fabric.api import sudo, cd
from fabtools import require
def working_copy(remote_url, working_path, branch="master", user='nobody'):
    sudo('mkdir -p %s' % working_path)
    sudo('chown %s:%s %s' % (user, user, working_path))
    with cd(working_path):
        require.git.working_copy(
            remote_url, branch=branch, update=True, use_sudo=True, user=user)
