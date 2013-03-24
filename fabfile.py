import fabtools.require
import fabtools.files
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
def ruby():
    s = run('ruby --version')
    if not s.startswith('ruby 1.9.3p327'):
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
    sudo("adduser --disabled-login --gecos 'GitLab' git")


@task
def gitlab_shell():
    fabtools.require.deb.packages([
        'git'
    ])

    if not fabtools.files.is_dir('/home/git/gitlab-shell'):
        with cd('/home/git'):
            sudo("git clone https://github.com/gitlabhq/gitlab-shell.git", user='git')
    fabtools.require.files.file(
        source  = './config.yml',
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
    fabtools.require.files.file(
        source  = 'pg_hba.conf',
        path    = '/etc/postgresql/9.1/main/pg_hba.conf',
        owner   = 'root',
        group   = 'root',
        mode    = '644',
        use_sudo = True)
    sudo('service postgresql restart')

    fabtools.require.files.file(
        source  = 'database.yml',
        path    = '/home/git/gitlab/config/database.yml')


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
            source  = './gitlab.yml',
            path    = '/home/git/gitlab/config/gitlab.yml',
            owner   = 'git',
            group   = 'git',
            mode    = '644',
            use_sudo = True)

## Copy the example GitLab config
#sudo -u git -H cp config/gitlab.yml.example config/gitlab.yml

## Make sure to change "localhost" to the fully-qualified domain name of your
## host serving GitLab where necessary
#sudo -u git -H vim config/gitlab.yml

## Make sure GitLab can write to the log/ and tmp/ directories
#sudo chown -R git log/
#sudo chown -R git tmp/
#sudo chmod -R u+rwX  log/
#sudo chmod -R u+rwX  tmp/

## Create directory for satellites
#sudo -u git -H mkdir /home/git/gitlab-satellites

## Create directory for pids and make sure GitLab can write to it
#sudo -u git -H mkdir tmp/pids/
#sudo chmod -R u+rwX  tmp/pids/

## Copy the example Unicorn config
#sudo -u git -H cp config/unicorn.rb.example config/unicorn.rb

@task(default = True)
def gitlab():
    execute(depends)
    execute(ruby)
    execute(bundler)
    execute(gitlab_shell)
    execute(database)
