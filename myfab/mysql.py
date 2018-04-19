from fabtools import require
def mysql_client(is_mariadb=True):
    if is_mariadb:
        require.rpm.package('mariadb-devel')
    else:
        require.rpm.package('mysql-devel')
