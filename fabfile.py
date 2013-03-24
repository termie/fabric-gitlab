import fabtools.require
import fabtools.files
import fabtools.user
from fabric.api import *
from fabric.context_managers import *

env.hosts = ['vagrant@192.168.33.10']


@task
def depends():
    fabtools.require.deb.packages([
        'build-essential',
        'zlib1g-dev',
        'libyaml-dev',
        'libssl-dev',
        'libgdbm-dev',
        'libreadline-dev',
        'libncurses5-dev',
        'libffi-dev',
        'curl',
        'git-core',
        'openssh-server',
        'redis-server',
        'postfix',
        'checkinstall',
        'libxml2-dev',
        'libxslt-dev',
        'libcurl4-openssl-dev',
        'libicu-dev',
        'libtool',
    ])


@task
def ruby(force = False):
    s = run('ruby --version')
    if force or not s.startswith('ruby 1.9.3p327'):
        sudo('rm -rf /tmp/ruby')
        fabtools.require.directory(
            path    = '/tmp/ruby',
        )

        fabtools.require.file(
            url     = 'http://ftp.ruby-lang.org/pub/ruby/1.9/ruby-1.9.3-p327.tar.gz',
            path    = '/tmp/ruby/ruby-1.9.3-p327.tar.gz'
        )

        with cd('/tmp/ruby'):
            run('tar zxvf ruby-1.9.3-p327.tar.gz')
        with cd('/tmp/ruby/ruby-1.9.3-p327'):
            run('./configure')
            run('make')
            sudo('make install')

@task
def bundler():
    sudo('gem install bundler')


@task
def git_user():
    # do this manually, rather than via fabtools
    if not fabtools.user.exists('git'):
        sudo("adduser --disabled-login --gecos 'GitLab' git")
    sudo('git config --global user.name  "GitLab"')
    sudo('git config --global user.email "gitlab@localhost"')

@task
def gitlab_shell():
    fabtools.require.deb.packages([
        'git'
    ])

    if not fabtools.files.is_dir('/home/git/gitlab-shell'):
        with cd('/home/git'):
            sudo("git clone https://github.com/gitlabhq/gitlab-shell.git", user='git')
    fabtools.require.files.file(
        source  = 'files/gitlab-shell/config.yml',
        path    = '/home/git/gitlab-shell/config.yml',
        owner   = 'git',
        group   = 'git',
        mode    = '644',
        use_sudo = True)
    with cd('/home/git/gitlab-shell'):
        sudo('./bin/install', user='git')


@task
def database():
    fabtools.require.deb.packages([
        'postgresql-9.1',
        'libpq-dev'
    ])

    # execute psql statements


    fabtools.require.files.file(
        source  = 'files/postgres/pg_hba.conf',
        path    = '/etc/postgresql/9.1/main/pg_hba.conf',
        owner   = 'postgres',
        group   = 'postgres',
        mode    = '644',
        use_sudo = True)
    fabtools.require.files.file(
        source  = 'files/postgres/postgres.conf',
        path    = '/etc/postgresql/9.1/main/postgres.conf',
        owner   = 'postgres',
        group   = 'postgres',
        mode    = '644',
        use_sudo = True)
    sudo('service postgresql restart')
    fabtools.require.files.file(
        source  = 'files/gitlab/database.yml',
        path    = '/home/git/gitlab/config/database.yml',
        owner   = 'postgres',
        group   = 'postgres',
        mode    = '644',
        use_sudo = True)



@task
def clone_source():
    with cd('/home/git'):
        sudo('git clone https://github.com/gitlabhq/gitlabhq.git gitlab', user='git')
    with cd('/home/git/gitlab'):
        sudo('git checkout 5-0-stable', user='git')


@task
def configure():
    with cd('/home/git/gitlab'):
        fabtools.require.files.file(
            source  = 'files/gitlab/gitlab.yml',
            path    = '/home/git/gitlab/config/gitlab.yml',
            owner   = 'git',
            group   = 'git',
            mode    = '644',
            use_sudo = True)
        sudo('chown -R git log/')
        sudo('chown -R git tmp/')
        sudo('chmod -R u+rwX  log/')
        sudo('chmod -R u+rwX  tmp/')
        sudo('cp config/unicorn.rb.example config/unicorn.rb', user = 'git')
    fabtools.require.directory(
        path     = '/home/git/gitlab-satellites',
        owner    = 'git',
        group    = 'git',
        mode     = '755',
        use_sudo = True
    )
    fabtools.require.directory(
        path     = '/home/git/gitlab/tmp/pids',
        owner    = 'git',
        group    = 'git',
        mode     = '755',
        use_sudo = True
    )


@task
def install_gems():
    with cd('/home/git/gitlab'):
        sudo("gem install -V charlock_holmes --version '0.6.9'")
        sudo('bundle install --deployment --without development test mysql', user='git')

@task
def init_script():
    fabtools.require.file(
        url      = 'https://raw.github.com/gitlabhq/gitlab-recipes/master/init.d/gitlab',
        path     = '/etc/init.d/gitlab',
        owner    = 'root',
        group    = 'root',
        mode     = '755',
        use_sudo = True
    )
    sudo('update-rc.d gitlab defaults 21')


@task
def check_info():
    with cd('/home/git/gitlab'):
        sudo('bundle exec rake gitlab:env:info RAILS_ENV=production', user='git')


@task
def check_status():
    with cd('/home/git/gitlab'):
        sudo('bundle exec rake gitlab:check RAILS_ENV=production', user='git')

@task(default = True)
def gitlab():
    execute(depends)
    execute(ruby)
    execute(bundler)
    execute(gitlab_shell)
    execute(database)
    execute(configure)

