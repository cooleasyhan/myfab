from fabric.api import sudo, run
def mkdir(path, user=None, use_sudo=True):
    if use_sudo:
        fun = sudo
    else:
        fun = run
    fun('mkdir -p %s ' %path )
    if user:
        fun('chown %s:%s %s' %(user, user, path))


    