cli
===
CLI for VisualOps


[required package]
=====================================================
## Ubuntu
apt-get install libyaml-dev libpython2.7-dev

## CentOS
yum install libyaml libyaml-devel python-devel


[third python lib]
=====================================================

##required
* cliff
* cliff-tablib
* pyyaml

##optinal
* virtualenv
* pudb


##1.install virtualenv (virtual python environment)
$ pip install virtualenv

##2.create virtual python environment
$ virtualenv .venv

##3.enter virtual python environment
$ . .venv/bin/activate


##4.The flowlling lib should be installed under virtualenv

###4.1 command line interface formulation framework
(.venv)$ pip install cliff

###4.2 formatting extensions for cliff(support html,json,yaml)
(.venv)$ pip install cliff-tablib



[install]
=====================================================
(.venv)$ pip install cliff
(.venv)$ python setup.py install


[usage]
=====================================================

##1.enter virtual python environment
$ . .venv/bin/activate

##2.enter interactive mode
(.venv)$ visualops
(visualops) help

##3.show help
(.venv)$ visualops -h

##4.none-interactive mode (already support)
(.venv)$ visualops -h
(.venv)$ visualops help stack list

(.venv)$ visualops login

(.venv)$ visualops stack list
(.venv)$ visualops stack list -f csv
(.venv)$ visualops stack list --filter docker --region ap-northeast-1
(.venv)$ visualops stack info stack-xxxxxxxx
(.venv)$ visualops stack pull stack-xxxxxxxx
(.venv)$ visualops stack run stack-xxxxxxxx -l

(.venv)$ visualops app list
(.venv)$ visualops app list --region us-east-1 --filter docker  -l
(.venv)$ visualops app stop app-xxxxxxxx -l
(.venv)$ visualops app start app-xxxxxxxx -l
(.venv)$ visualops app reboot app-xxxxxxxx -l
(.venv)$ visualops app terminate app-xxxxxxxx -l

(.venv)$ visualops logout



[debug]
=====================================================

##add the following line to first breakpoint
<pre>
import pudb
pudb.set_trace()
</pre>


[support auto-complete]
=====================================================

##1.generate `bash_complete script`
(.venv)$ visualops complete > /etc/bash_completion.d/visualops

##use auto-complete
press `tab` twice when input command



[install docker]
=====================================================
## ubuntu 14.04 x86_64 (http://beta-docs.docker.io/installation/ubuntulinux/)
$ sudo apt-get -y install docker.io
$ sudo ln -sf /usr/bin/docker.io /usr/local/bin/docker
$ sudo sed -i '$acomplete -F _docker docker' /etc/bash_completion.d/docker.io
$ sudo update-rc.d docker.io defaults
$ docker -v
Docker version 1.0.1, build 990021a

### upgrade to docker 1.2
$ curl -sSL https://get.docker.io/ubuntu/ | sudo sh
$ docker -v
Docker version 1.2.0, build fa7b24f

-----------------------------------------------------

## centos 6.5 x86_64 (http://beta-docs.docker.io/installation/centos/)
$ yum install http://ftp.riken.jp/Linux/fedora/epel/6/i386/epel-release-6-8.noarch.rpm
$ yum install docker-io
$ docker -v
Docker version 1.1.2, build d84a070/1.1.2

### upgrade to docker 1.2
$ cd /usr/bin
$ cp docker docker-1.1.2
$ wget https://get.docker.io/builds/Linux/x86_64/docker-latest -O docker
$ chmod +x docker
$ docker -v
Docker version 1.2.0, build fa7b24f
