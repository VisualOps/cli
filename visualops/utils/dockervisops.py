'''
Docker module (docker-py wrapper)
@author: Thibault BRONCHAIN
Copyright 2014 MadeiraCloud LTD.

note: Part of these functions have been extracted and/or modified
      from the Salt (SaltStack) Docker module
'''

import time
import json
import os
import docker
import datetime
import re
import socket

import visualops
from visualops.utils import boot2docker
from visualops.utils import utils
from visualops.utils import db

import logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

IPS=["PrivateIp","PublicIp","PrivateIpAddress","PublicIpAddress"]


# Check if docker exists decorator
def has_docker(func):
    def action(*args, **kwargs):
        try:
            get_images(args[0])
        except Exception:
            utils.error("Unable to find Docker client.\nPlease, ensure Docker is correcly setup.")
        return func(*args, **kwargs)
    return action

## Helpers
def _get_config():
    '''
    Get user docker configuration

    Return: dict
    '''
    cfg = os.path.expanduser('~/.dockercfg')
    try:
        fic = open(cfg)
        try:
            config = json.loads(fic.read())
        finally:
            fic.close()
    except Exception:
        config = {'rootPath': '/dev/null'}
    if not 'Configs' in config:
        config['Configs'] = {}
    return config

def _get_client(config, url=None, version=None, timeout=None):
    '''
    Get a connection to a docker API (socket or URL)

    By default it will use the base docker-py defaults which
    at the time of writing are using the local socket and
    the 1.4 API

    Set those keys in your configuration tree somehow:

        - docker.url: URL to the docker service
        - docker.version: API version to use

    Return: docker client
    '''
    if config.get("docker_sock"):
        url=config["docker_sock"]
    client = docker.Client(base_url=url)
    # force 1..5 API for registry login
    if not version:
        if client._version == '1.4':
            client._version = '1.5'
    if getattr(client, '_cfg', None) is None:
        client._cfg = {
            'Configs': {},
            'rootPath': '/dev/null'
        }
    client._cfg.update(_get_config())
    return client

def _set_id(infos):
    '''
    ID compatibility hack

    return: dict
    '''
    if infos:
        cid = None
        if infos.get("Id"): cid = infos["Id"]
        elif infos.get("ID"): cid = infos["ID"]
        elif infos.get("id"): cid = infos["id"]
        if "Id" not in infos:
            infos["Id"] = cid
        infos.pop("id",None)
        infos.pop("ID",None)
    return infos

def _get_image_infos(config,image):
    '''
    Verify that the image exists
    We will try to resolve either by:
        - name
        - image_id
        - tag

    image
        Image Name / Image Id / Image Tag

    Returns dict
    '''
    client = _get_client(config)
    infos = None
    try:
        infos = _set_id(client.inspect_image(image))
    except Exception as e:
        pass
    return infos

# external access
def get_container_infos(config,container):
    return _get_container_infos(config, container)

def _get_container_infos(config, container):
    '''
    Get container infos

    container
        Image Id / grain name

    return: dict
    '''
    client = _get_client(config)
    infos = None
    try:
        infos = _set_id(client.inspect_container(container))
    except Exception:
        pass
    return infos

def is_running(config, container, *args, **kwargs):
    '''
    Is this container running

    container
        Container id

    Return container
    '''
    try:
        infos = _get_container_infos(config, container)
        return (infos if infos.get('State', {}).get('Running') else None)
    except Exception:
        return None

def _sizeof_fmt(num):
    '''
    Return disk format size data
    '''
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if num < 1024.0:
            return '%3.1f %s' % (num, x)
        num /= 1024.0

def _parse_image_multilogs_string(config, ret, repo):
    '''
    Parse image log strings into grokable data
    '''
    image_logs, infos = [], None
    if ret and ret.strip().startswith('{') and ret.strip().endswith('}'):
        pushd = 0
        buf = ''
        for char in ret:
            buf += char
            if char == '{':
                pushd += 1
            if char == '}':
                pushd -= 1
            if pushd == 0:
                try:
                    buf = json.loads(buf)
                except Exception:
                    pass
                image_logs.append(buf)
                buf = ''
        image_logs.reverse()
        # search last layer grabbed
        for l in image_logs:
            if isinstance(l, dict):
                if l.get('status') == 'Download complete' and l.get('id'):
                    infos = _get_image_infos(config, repo)
                    break
    return image_logs, infos

def _pull_assemble_error_status(logs):
    '''
    Given input in this form::

        u'{"status":"Pulling repository foo/ubuntubox"}:
        "image (latest) from foo/  ...
         rogress":"complete","id":"2c80228370c9"}'

    construct something like that (load JSON data is possible)::

        [u'{"status":"Pulling repository foo/ubuntubox"',
         {"status":"Download","progress":"complete","id":"2c80228370c9"}]
    '''
    comment = 'An error occurred pulling your image'
    try:
        for err_log in logs:
            if isinstance(err_log, dict):
                if 'errorDetail' in err_log:
                    if 'code' in err_log['errorDetail']:
                        msg = '\n{0}\n{1}: {2}'.format(
                            err_log['error'],
                            err_log['errorDetail']['code'],
                            err_log['errorDetail']['message']
                        )
                    else:
                        msg = '\n{0}\n{1}'.format(
                            err_log['error'],
                            err_log['errorDetail']['message'],
                        )
                    comment += msg
    except Exception as e:
        comment += "%s"%e
    return comment

def _get_port(port):
    p = port.split("/")
    return int(p[0])

def _test_ports(pb,length):
    hosts = sorted([int(pb[guest].get("HostPort",0)) for guest in pb])
    if not hosts:
        return False
    previous = hosts[0]
    for port in hosts[1:]:
        if (port - previous < length):
            return False
    return True

def _gen_ports(ports,port_bindings,length):
    out_ports = []
    out_port_bindings = []

    if _test_ports(port_bindings,length) is False:
        return (None,None)

    i = 0
    while i < length:
        cur_port = []
        for p in ports:
            port = p.split("/")
            protocol = ("tcp" if len(port) != 2 else port[1])
            port = int(port[0])
            cur_port.append("%s/%s"%(port,protocol))
        out_ports.append(cur_port)
        i += 1

    i = 0
    while i < length:
        cur_pb = {}
        for p in port_bindings:
            port = p.split("/")
            protocol = ("tcp" if len(port) != 2 else port[1])
            port = int(port[0])
            cur_pb["%s/%s"%(port,protocol)] = {
                "HostIp": port_bindings[p].get("HostIp"),
                "HostPort": int(port_bindings[p].get("HostPort",0))+i
            }
        out_port_bindings.append(cur_pb)
        i += 1

    return (out_ports[::-1],out_port_bindings[::-1])
##


## Docker action calls
def create_container(config,
                     image,
                     command=None,
                     hostname=None,
                     user=None,
                     detach=True,
                     entrypoint=None,
                     stdin_open=False,
                     tty=False,
                     mem_limit=0,
                     cpu_shares=None,
                     ports=None,
                     environment=None,
                     dns=None,
                     volumes=None,
                     volumes_from=None,
                     name=None,
                     *args, **kwargs):
    '''
    Create a new container

    image
        image to create the container from
    command
        command to execute while starting
    hostname
        hostname of the container
    user
        user to run docker as
    detach
        daemon mode
    entrypoint
        entrypoint to the container
    stdin_open
        let stdin open
    tty
        attach ttys
    mem_limit:
        memory size limit
    cpu_shares:
        cpu shares authorized
    ports
        ports redirections ({'222': {}})
    environment
        environment variable mapping ({'foo':'BAR'})
    dns
        list of DNS servers
    volumes
        list of volumes mapping::

            (['/mountpoint/in/container:/guest/foo',
              '/same/path/mounted/point'])
    volumes_from
        container to get volumes definition from
    name
        name given to container

    Returns: created container / None
    '''

    err = "Unknown"
    client = _get_client(config)
    try:
        img_infos = _get_image_infos(config, image)
        mountpoints = {}
        binds = {}
        # create empty mountpoints for them to be
        # editable
        # either we have a list of guest or host:guest
        if isinstance(volumes, list):
            for mountpoint in volumes:
                mounted = mountpoint
                if ':' in mountpoint:
                    parts = mountpoint.split(':')
                    mountpoint = parts[1]
                    mounted = parts[0]
                mountpoints[mountpoint] = {}
                binds[mounted] = mountpoint
        info = _set_id(client.create_container(
            image=image,
            command=command,
            hostname=hostname,
            user=user,
            entrypoint=entrypoint,
            detach=detach,
            stdin_open=stdin_open,
            tty=tty,
            mem_limit=mem_limit,
            ports=ports,
            environment=environment,
            dns=dns,
            volumes=mountpoints,
            volumes_from=volumes_from,
            name=name,
            cpu_shares=cpu_shares
        ))
        print "Container '%s' created."%info['Id']
        return info
    except Exception as e:
        err = e
    utils.error("Unable to create your container: %s"%err)
    return None


def stop(config, container, timeout=10, *args, **kwargs):
    '''
    Stop a running container

    :type container: string
    :param container: The container id to stop

    :type timeout: int
    :param timeout: Wait for a timeout to let the container exit gracefully
        before killing it

    :rtype: dict
    :returns: boolean
    '''
    err = "Unknown"
    client = _get_client(config)
    try:
        dcontainer = _get_container_infos(config, container)['Id']
        if is_running(config, dcontainer):
            client.stop(dcontainer, timeout=timeout)
            if not is_running(config, dcontainer):
                print "Container stopped."
                return True
            else:
                i = 0
                while is_running(config, dcontainer):
                    time.sleep(0.1)
                    if i > 100:
                        return kill(config,container)
                    i += 1
                return True
        else:
            return True
    except Exception as e:
        err = e
    utils.warning("Container not existing")
    return True


def kill(config, container, *args, **kwargs):
    '''
    Kill a running container

    :type container: string
    :param container: The container id to kill

    :rtype: dict
    :returns: boolean
    '''
    err = "Unknown"
    client = _get_client(config)
    try:
        dcontainer = _get_container_infos(config, container)['Id']
        if is_running(config, dcontainer):
            client.kill(dcontainer)
            if not is_running(config, dcontainer):
                print "Container killed."
                return True
        else:
            print "Container not running."
            return True
    except Exception as e:
        err = e
    utils.error("Unable to kill the container: %s"%err)
    return False


def remove_container(config, container=None, force=True, v=False, *args, **kwargs):
    '''
    Removes a container from a docker installation

    container
        Container id to remove
    force
        By default, remove a running container, set this
        to notremove it unconditionally
    v
        verbose mode

    Return boolean
    '''
    err = "Unknown"
    client = _get_client(config)
    dcontainer = None
    try:
        try:
            dcontainer = _get_container_infos(config, container)['Id']
        except Exception:
#            print "Container not existing."
            return True
        else:
            if not dcontainer:
                return True
            if is_running(config, dcontainer):
                if not force:
                    utils.error("Container running, won't remove it.")
                    return False
                else:
                    kill(config, dcontainer)
            client.remove_container(dcontainer, v=v)
            try:
                infos = _get_container_infos(config, dcontainer)
                if not infos:
                    return True
            except Exception:
#                print "Container has been successfully removed."
                return True
    except Exception as e:
        err = e
    utils.error("Unable to remove container: %s"%err)
    return False

def restart(config, container, timeout=10, *args, **kwargs):
    '''
    Restart a running container

    :type container: string
    :param container: The container id to restart

    :type timout: int
    :param timeout: Wait for a timeout to let the container exit gracefully
        before killing it

    :rtype: dict
    :returns: boolean
    '''
    err = "Unknown"
    client = _get_client(config)
    try:
        dcontainer = _get_container_infos(config, container)['Id']
        client.restart(dcontainer, timeout=timeout)
        if is_running(config, dcontainer):
            print "Container restarted."
            return True
    except Exception as e:
        err = e
    if stop(config, container, timeout):
        ret = start(config, container)
        if ret: return True
    utils.error("Unable to restart the container: %s"%err)
    return False


def start(config, container, binds=None, ports=None, port_bindings=None,
          lxc_conf=None, publish_all_ports=None, links=None,
          privileged=False,
          *args, **kwargs):
    '''
    Start the specified container

    container
        Container id
    Returns boolean
    '''
    if not binds:
        binds = {}
    if not ports:
        ports = {}
    err = "Unknown"
    client = _get_client(config)
    try:
        dcontainer = _get_container_infos(config, container)['Id']
        if not is_running(config, container):
            bindings = None
            if port_bindings is not None:
                print "Binding container ports ..."
                bindings = {}
                for k, v in port_bindings.iteritems():
                    bindings[k] = (v.get('HostIp', ''), v['HostPort'])
            client.start(dcontainer, binds=binds, port_bindings=bindings,
                         lxc_conf=lxc_conf,
                         publish_all_ports=publish_all_ports, links=links,
                         privileged=privileged)
            if is_running(config, dcontainer):
                print "Container has been started."
                return _get_container_infos(config, container)
        else:
            print "Container is already started."
            return _get_container_infos(config, container)
    except Exception as e:
        err = e
    utils.error("Unable to start your container: %s"%err)
    return None

def start_all(config, containers=None, binds=None, ports=None, port_bindings=None,
              lxc_conf=None, publish_all_ports=None, links=None,
              privileged=False,
              *args, **kwargs):
    failure = False
    containers_out = []
    for container in containers:
        started = start(config, container=container, binds=binds, ports=ports, port_bindings=port_bindings,
                        lxc_conf=lxc_conf, publish_all_ports=publish_all_ports, links=links,
                        privileged=privileged,
                        *args, **kwargs)
        if is_running(config, container) and started:
            print "Container started, id: %s"%started.get("Id")
            containers_out.append(started)
        else:
            failure = True
            utils.error("Unable to run container: %s - can't start"%container)
    return containers_out, failure

def get_images(config, name=None, quiet=False, all=True, *args, **kwargs):
    '''
    List docker images

    :type name: string
    :param name: A repository name to filter on

    :type quiet: boolean
    :param quiet: Only show image ids

    :type all: boolean
    :param all: Show all images

    :rtype: dict
    :returns: the images
    '''
    err = "Unknown"
    client = _get_client(config)
    try:
        infos = client.images(name=name, quiet=quiet, all=all)
        for i in range(len(infos)):
            inf = _set_id(infos[i])
            try:
                inf['Human_Size'] = _sizeof_fmt(int(inf['Size']))
            except ValueError:
                pass
            try:
                ts = int(inf['Created'])
                dts = datetime.datetime.fromtimestamp(ts)
                inf['Human_IsoCreated'] = dts.isoformat()
                inf['Human_Created'] = dts.strftime(
                    '%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
            try:
                inf['Human_VirtualSize'] = (
                    _sizeof_fmt(int(inf['VirtualSize'])))
            except ValueError:
                pass
        return infos
    except Exception as e:
        err = e
    utils.error("Unable to list Docker images: %s"%err)
    return None


def get_containers(config,
                   all=True,
                   trunc=False,
                   since=None,
                   before=None,
                   limit=-1,
                   *args,
                   **kwargs):
    '''
    Get a list of mappings representing all containers

    all
        Return all containers

    trunc
        Set it to True to have the short ID

    Returns a mapping of containers
    '''
    err = "Unknown"
    client = _get_client(config)
    try:
        ret = client.containers(all=all,
                                trunc=trunc,
                                since=since,
                                before=before,
                                limit=limit)
        return ret
    except Exception as e:
        err = e
    utils.error("Unable to list Docker containers: %s"%err)
    return None


def login(config, username=None, password=None, email=None, url=None, client=None, *args, **kwargs):
    '''
    Wrapper to the docker.py login method
    '''
    try:
        c = (_get_client(config) if not client else client)
        lg = c.login(username, password, email, url)
        print "%s logged to %s"%(username,(url if url else "default hub"))
    except Exception as e:
        utils.error("%s can't login to repo %s: %s"%(username,(url if url else "default repo"),e))
        return False
    return True
##


## Docker App actions
def installed(config,
              name,
              image,
              entrypoint=None,
              command=None,
              hostname=None,
              user=None,
              detach=True,
              stdin_open=False,
              tty=False,
              mem_limit=0,
              cpu_shares=None,
              ports=None,
              environment=None,
              dns=None,
              volumes=None,
              volumes_from=None,
              force=True,
              *args, **kwargs):
    '''
    Ensure that a container with the given name exists;
    if not, build a new container from the specified image.
    (`docker run`)

    name
        Name for the container
    image
        Image from which to build this container
    entrypoint
        Entrypoint of the container
    command
        command to execute while starting
    hostname
        hostname of the container
    user
        user to run docker as
    detach
        daemon mode
    entrypoint
        entrypoint to the container
    stdin_open
        let stdin open
    tty
        attach ttys
    mem_limit:
        memory size limit
    cpu_shares:
        cpu shares authorized
    ports
        ports redirections ({'222': {}})
    environment
        environment variable mapping ({'foo':'BAR'})
    dns
        list of DNS servers
    ports
        List of ports definitions, either:
            - a port to map
            - a mapping of mapping portInHost : PortInContainer
    volumes
        List of volumes
    volumes_from

    Returns
        container

    .. note::
        This command does not verify that the named container
        is running the specified image.
    '''
    iinfos = _get_image_infos(config, image)
    if not iinfos:
        utils.error("Image not found.")
        return None
    cinfos = _get_container_infos(config, name)
    force = (config["force"] if config.get("force") != None else force)
    if cinfos and force:
        remove_container(config, container=name,force=True)
        print "Old container removed."
    elif cinfos and (not force):
        print "Container found: %s."%cinfos.get("Id")
        return cinfos

    dports, dvolumes, denvironment, de = {}, [], {}, {}
    if not ports:
        ports = []
    if not volumes:
        volumes = []
    if isinstance(environment, dict):
        print "Setting environment ..."
        for k in environment:
            denvironment[u'%s' % k] = u'%s' % environment[k]
    if isinstance(environment, list):
        print "Setting environment ..."
        for p in environment:
            if isinstance(p, dict):
                for k in p:
                    denvironment[u'%s' % k] = u'%s' % p[k]
    if ports:
        print "Setting ports mapping ..."
        for p in ports:
            if not isinstance(p, dict):
                dports[str(p)] = {}
            else:
                for k in p:
                    dports[str(p)] = {}
    if volumes:
        print "Setting volumes ..."
        for p in volumes:
            vals = []
            if not isinstance(p, dict):
                vals.append('%s' % p)
            else:
                for k in p:
                    vals.append('{0}:{1}'.format(k, p[k]))
            dvolumes.extend(vals)
    container = create_container(
        config,
        image=image,
        command=command,
        entrypoint=entrypoint,
        hostname=hostname,
        user=user,
        detach=detach,
        stdin_open=stdin_open,
        tty=tty,
        mem_limit=mem_limit,
        ports=dports,
        environment=denvironment,
        dns=dns,
        volumes=dvolumes,
        volumes_from=volumes_from,
        name=name)

    if container:
        print "Container created, id: %s"%(container.get("Id"))
    else:
        utils.error("Couldn't create container.")
    return container


def running(config,
            containers,
            image,
            tag=None,
            entrypoint=None,
            command=None,
            environment=None,
            ports=None,
            volumes=None,
            mem_limit=0,
            cpu_shares=None,
            binds=None,
            publish_all_ports=False,
            links=None,
            port_bindings=None,
            force=True,
            hostname=None,
            *args, **kwargs):
    '''
    Ensure that a container is running. (`docker inspect`)

    containers
        name of the containers to start
    image
        name of the image to start the container from
    entrypoint
        Entrypoint of the container
    command
        command to execute while starting
    environment
        environment variable mapping ({'foo':'BAR'})
    ports
        List of ports definitions, either:
            - a port to map
            - a mapping of mapping portInHost : PortInContainer
    volumes
        List of volumes
    mem_limit:
        memory size limit
    cpu_shares:
        cpu shares authorized
    binds
        like -v of docker run command
    publish_all_ports
    links
        Link several container together
    port_bindings
        List of ports to expose on host system
            - a mapping port's guest, hostname's host and port's host.

    Returns
        Container Id
    '''
    if not containers:
        utils.warning("No container specified")
        return [], True

    if ports and port_bindings:
        (ports,port_bindings) = _gen_ports(ports,port_bindings,len(containers))
        if not ports or not port_bindings:
            utils.error("Unable to generate port bindings (is there enough space between each allocation required?)")
            return [], True

    containers_out = []
    failure = False

    if tag:
        image = "%s:%s"%(image,tag)

    for container in containers:
        port = (ports.pop() if ports else None)
        port_binding = (port_bindings.pop() if port_bindings else None)
        ret = installed(config,
                        container,image,entrypoint=entrypoint,command=command,environment=environment,ports=port,
                        volumes=volumes,mem_limit=mem_limit,cpu_shares=cpu_shares,force=force,hostname=hostname)
        if ret:
            started = start(config,
                container, binds=binds, port_bindings=port_binding,
                publish_all_ports=publish_all_ports, links=links)
            if is_running(config, container) and started:
                print "Container started, id: %s"%started.get("Id")
                containers_out.append(started)
            else:
                failure = True
                utils.error("Unable to run container: %s - can't start"%container)
        else:
            failure = True
            utils.error("Unable to run container: %s - can't install"%container)

    return containers_out, failure


def pull(config, repo, tag=None, username=None, password=None, email=None, *args, **kwargs):
    '''
    Pulls an repo from any registry. See above documentation for
    how to configure authenticated access.

    :type repo: string
    :param repo: The repository to pull. \
        [registryurl://]REPOSITORY_NAME
        eg::

            index.docker.io:MyRepo
            superaddress.cdn:MyRepo
            MyRepo

    :type tag: string
    :param tag: The specific tag  to pull

    :rtype: dict
    :returns: the repo details
    '''
    err = "Unknown"
    client = _get_client(config)
    try:
        if username:
            url = repo.split(":")
            url = (url[0] if len(url) > 1 else None)
            if not login(config,username,password,email,url):
                raise Exception("Can't login")
        print "Pulling repository %s ... (This may take a while)"%repo
        ret = client.pull(repo, tag=tag)
        if ret:
            logs, infos = _parse_image_multilogs_string(config, ret, repo)
            if infos and infos.get('Id', None):
                repotag = repo
                if tag:
                    repotag = '{0}:{1}'.format(repo, tag)
                print 'Repo {0} was pulled ({1})'.format(repotag, infos['Id'])
                return infos, False
            else:
                err = _pull_assemble_error_status(logs)
    except Exception as e:
        err = e
    utils.error("An error has occured pulling repo %s: %s"%(repo,err))
    return None, True
##


## Files state
def create_files(config, container, files=[]):
    failure = False
    for f in files:
        path = f.get("key")
        if not path:
            failure = True
            utils.error("Unable to read config file path.")
            continue
        dir_path = os.path.join(config["config_path"],"docker","files",container)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        host_path = os.path.join(dir_path,("%s"%path).replace('/','-'))
        content = f.get("value","")
        try:
            with open(host_path, 'w') as f:
                f.write(content)
            print "Configuration file %s created: %s."%(path,host_path)
        except Exception as e:
            failure = True
            utils.error("Unable to store configuration file %s: %s"%(host_path,e))
    return None, failure
##


## Deploy
def _create_files_volumes(config, state_params, exec_params):
    volumes = []
    for f in state_params.get("files",[]):
        path = f.get("key")
        if not path:
            utils.error("Unable to read config file path.")
            continue
        print "Configuration file found: %s."%path
        dir_path = os.path.join(config["config_path"],"docker","files",state_params["container"])
        host_path = os.path.join(dir_path,("%s"%path).replace('/','-'))
        volumes.append({"key":host_path,"value":path})
    exec_params["volumes"] = exec_params.get("volumes",[])+volumes
    return exec_params

def _replace_params(config, hostname, addin, param):
    config.setdefault(param,{})
    config[param].setdefault(hostname,{})
    config[param][hostname].setdefault(addin["container"],{})
    res = config[param][hostname][addin["container"]]
    if res and type(res) is dict:
        return [{"key":key,"value":res[key]} for key in res]
    elif res:
        return res
    return addin.get(param)

def _convert_running(config, appname, hostname, addin):
    addin["port_bindings"] = _replace_params(config, hostname, addin,"port_bindings")
    addin["volumes"] = _replace_params(config, hostname, addin,"volumes")
    addin["mem_limit"] = _replace_params(config, hostname, addin,"mem_limit")
    addin["cpu_shares"] = _replace_params(config, hostname, addin,"cpu_shares")
    addin["count"] = _replace_params(config, hostname, addin,"count")
    if addin.get("port_bindings"):
        ports = []
        pb = {}
        for item in addin["port_bindings"]:
            key = item.get("key",None)
            value = item.get("value",None)
            if not key: continue

            # get user input
            ui = utils.user_param(config,
                                  "Update port binding for %s (host=container)"%addin["container"],
                                  ("%s=%s"%(key,value)
                                   if key not in config["port_bindings"][hostname].get(addin["container"],{})
                                   else "%s=%s"%((key if key else ""),(value if value else ""))))
            # parse result
            if not ui:
                config["port_bindings"][hostname][addin["container"]][key] = value
                continue
            ui = ui.split("=")
            if len(ui) != 2:
                utils.error("Wrong port binding syntax")
                continue
            key, value = ui[1], ui[0]
            # persist
            config["port_bindings"][hostname][addin["container"]][key] = value

            if not key or not value: continue
            v = value.split(":")
            pb[key] = ({
                "HostIp": v[0],
                "HostPort": v[1]
            } if len(v) == 2 else {
                "HostIp": "0.0.0.0",
                "HostPort": v[0]
            })
            ports.append(key)
        addin.pop("port_bindings")
        if pb and ports:
            addin["port_bindings"] = pb
            addin["ports"] = ports
    if addin.get("volumes"):
        volumes = []
        binds = {}
        vol = addin.get("volumes",{})
        for item in vol:
            key = item.get("key")
            value = item.get("value")
            if not key: continue

            # get user input
            ui = utils.user_param(config,
                                  "Update mount point for %s"%addin["container"],
                                  ("%s=%s"%(key,value)
                                   if key not in config["volumes"][hostname].get(addin["container"],{})
                                   else "%s=%s"%((key if key else ""),(value if value else ""))))
            # parse result
            if not ui:
                config["volumes"][hostname][addin["container"]][key] = value
                continue
            ui = ui.split("=")
            if len(ui) != 2:
                utils.error("Wrong volume syntax")
                continue
            key, value = ui[0], ui[1]
            if config.get("chroot"):
                key = os.path.join(config["chroot"],appname,hostname,addin["container"],key)
            # persist
            config["volumes"][hostname][addin["container"]][key] = value




            mp = value.split(":")
            ro = (True if (len(mp) == 2 and mp[1] == "ro") else False)
            value = mp[0]
            volumes.append(value)
            binds[key] = {
                'bind': value,
                'ro': ro
            }
        addin.pop("volumes")
        if volumes and binds:
            addin["volumes"] = volumes
            addin["binds"] = binds
    if addin.get("environment"):
        env = {}
        for item in addin["environment"]:
            key = item.get("key","")
            value = item.get("value","")
            if not key: continue
            env[key] = value
        addin.pop("environment")
        addin["environment"] = env
    if addin.get("links"):
        links = {}
        for item in addin["links"]:
            key = item.get("key","")
            value = item.get("value","")
            if not key or not value: continue
            links[key] = value
        addin.pop("links")
        addin["links"] = links
    if addin.get("cpu_shares"):
        # get user input
        ui = utils.user_param(config,
                              "Update CPU shares for %s"%addin["container"],
                              ("%s"%(addin.get("cpu_shares"))
                               if addin["container"] not in config["cpu_shares"][hostname]
                               else addin.get("cpu_shares")))
        # parse result
        addin["cpu_shares"] = ui
        # persist
        config["cpu_shares"][hostname][addin["container"]] = ui
    if addin.get("mem_limit"):
        # get user input
        ui = utils.user_param(config,
                              "Update memory limit for %s"%addin["container"],
                              ("%s"%(addin.get("mem_limit"))
                               if addin["container"] not in config["mem_limit"][hostname]
                               else addin.get("mem_limit")))
        # parse result
        mem = ui
        # persist
        config["cpu_shares"][hostname][addin["container"]] = ui

        mem_eq={
            'b': lambda x: x,
            'k': lambda x: x << 10,
            'm': lambda x: x << 20,
            'g': lambda x: x << 30,
            't': lambda x: x << 40,
        }
        addin["mem_limit"] = (mem_eq[mem[-1].lower()](int(mem[:-1])) if mem[-1].lower() in mem_eq else int(mem))
    if not addin.get("count"):
        addin["containers"] = [addin["container"]]
    else:
        # get user input
        ui = utils.user_param(config,
                              "Update number of containers for %s"%(addin["container"]),
                              addin["count"])
        # parse result
        addin["count"] = ui
        # persist
        config["count"][hostname][addin["container"]] = ui

        addin["containers"] = []
        count = int(addin["count"])
        i=0
        while i < count:
            addin["containers"].append("%s_%s"%(addin["container"],i+1))
            i += 1
    addin.pop("container")
    return addin


_deploy = {
    'attr' : {
        "create_files": {
            'container'     : 'container',
            'files'         : 'files',
        },
        "pull" : {
            'image'         : 'repo',
            'tag'           : 'tag',
            'username'      : 'username',
            'password'      : 'password',
            'email'         : 'email',
        },
        "running" : {
            # installed
            'container'     : 'container',
            'image'         : 'image',
            'tag'           : 'tag',
            'command'       : 'command',
            'environment'   : 'environment',
            'volumes'       : 'volumes',
            'mem_limit'     : 'mem_limit',
            'cpu_shares'    : 'cpu_shares',
            'ports'         : 'ports',
            'hostname'      : 'hostname',
            'force'         : 'force',
            # running
#            'publish_all_ports': 'publish_all_ports',
            'binds'         : 'binds',
#            'links'         : 'links',
            'port_bindings' : 'port_bindings',
            'count'         : 'count',
            # deploy
            'files'         : _create_files_volumes,
        },
        "start_all" : {
            'container'     : 'container',
            'ports'         : 'ports',
            'hostname'      : 'hostname',
            'force'         : 'force',
            'binds'         : 'binds',
            'port_bindings' : 'port_bindings',
            'count'         : 'count',
            'volumes'       : 'volumes',
        },
    },
    'actions': {
        'deploy' : [
            "create_files",
            "pull",
            "running"
        ],
        'start' : [
            "start_all"
        ],
    },
    'convert': {
        "running": _convert_running,
        "start_all": _convert_running,
    },
}



# preproc deploy a container
@has_docker
def preproc_deploy(config, appname, hostname, state, act):
    if "container" not in state:
        utils.error("Container name missing")
        return {}
    elif "image" not in state:
        utils.error("Image name missing")
        return {}
    print "--> Preparing to run container(s) %s from image %s ..."%(state["container"],state["image"])
    actions = {}
    for action in _deploy.get('actions',{}).get(act,[]):
        params = {}
        for param in _deploy.get('attr',{}).get(action,{}):
            if not state.get(param): continue
            if hasattr(_deploy['attr'][action][param], '__call__'):
                params.update(_deploy['attr'][action][param](config,state,params))
            elif type(state[param]) is list:
                params[_deploy['attr'][action][param]] = params.get(_deploy['attr'][action][param],[])+state[param]
            elif type(state[param]) is dict:
                params[_deploy['attr'][action][param]] = dict(params.get(_deploy['attr'][action][param],{}).items()
                                                              +state[param].items())
            else:
                params[_deploy['attr'][action][param]] = state[param]
        if hasattr(eval(action), '__call__'):
            if action in _deploy.get("convert",{}):
                actions[action] = _deploy["convert"][action](config, appname, hostname, params)
            else:
                actions[action] = params.copy()
        else:
            utils.error("Action not found: %s"%action)
    return actions


# deploy a container
@has_docker
def deploy(config, actions):
    out = {}
    for action in actions:
        if hasattr(eval(action), '__call__'):
            out[action], failure = eval(action)(config, **actions[action])
            if failure:
                break
    app = {}
    db.delete_app_info( config["appname"] )
    for container in (out.get("running",[])+out.get("start_all",[])):
        name = container.get("Name").replace("/","")
        print "--> Container successfully started %s."%name
        db.create_container(config["appname"], container.get("Id"), name)
        app[name] = container
    return app

# generate app hosts
def generate_hosts(config, app):
    '''
    app: {
        "container id": continer details
        ...
    }
    '''
#    hosts = {app[container]["NetworkSettings"]["IPAddress"]:app[container]["Name"].replace('/','') for container in app}
    hosts = {}
    for container in app:
        hosts[app[container]["NetworkSettings"]["IPAddress"]] = [app[container]["Name"].replace('/','')]
    for container in app:
        path = (app[container]["HostsPath"]
                if boot2docker.has() is not True
                else os.path.join(config["config_path"],"docker","containers",app[container]["Id"],"hosts"))
        try:
            with open(path, 'r+') as f:
                for host in hosts:
                    f.write("%s\t%s\n"%(host," ".join(hosts[host])))
        except Exception as e:
            utils.error(e)
##

## renderer
def list_containers(host):
    return [c for container in host for c in host[container].get("running",{}).get("containers",[])]

def render(config, filename, content):
    rendered = ""
    l = 1
    for line in content.split("\n"):
        objs = re.findall("@{(?P<uid>.*?)\.(?P<param>.*?)}",line)
        for obj in objs:
            if obj[1] not in IPS: continue
            hostname = config["hosts_table"].get(obj[0])
            containers = list_containers(config["actions"].get(hostname,{}))
            if len(containers) == 0:
                ip = socket.gethostbyname(socket.getfqdn())
            elif len(containers) == 1:
                ip = containers.pop()
            else:
                # TODO (release 2): render with config
                ip = utils.user_param(config,
                                      '''
Multiple containers found on instance %s.
Note: if you are not sure, correctly binded your ports,
      and have an external access to your machine,
      you can try to use your host IP address (default).

Warning: Using localhost (or 127.0.0.1) won't work in most cases

Context: %s %s, line %s: %s
Please, specify which container to use: %s
                                      '''%(hostname,
                                           ("file" if filename else "parameter"),
                                           filename,
                                           l,
                                           line,
                                           ", ".join(containers)),
                                      socket.gethostbyname(socket.getfqdn()))
            line = re.sub("@{%s\.(.*?)}"%obj[0],ip,line,count=1)
        rendered += "%s\n"%line
        l += 1
    return (rendered[:-1] if (rendered[-1:] == '\n' and content[-1:] != '\n') else rendered)

def render_all(config, content, name="Undefined"):
    if type(content) is dict:
        if ("key" in content) and ("value" in content):
            return {"key":content["key"],
                    "value":render_all(config,content["value"],content["key"])}
        ret = {}
        for key in content:
            ret[key] = render_all(config,content[key],key)
        return ret
    elif type(content) is list:
        return [render_all(config,item,name) for item in content]
    elif isinstance(content, basestring):
        return render(config, name, content)
    return content
##
