'''
Docker module
@author: Thibault BRONCHAIN
(c) 2014 - MadeiraCloud LTD.

note: Part of these functions have been extracted and/or modified
      from the Salt (SaltStack) Docker module
'''

import json
import os
import docker

from utils import error,warning,user_param

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

def _get_client(version=None, timeout=None):
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
    client = docker.Client()
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
        id = None
        if infos.get("Id"): id = infos["Id"]
        elif infos.get("ID"): id = infos["ID"]
        elif infos.get("id"): id = infos["id"]
        if "id" not in infos:
            infos["id"] = id
        infos.pop("Id")
        infos.pop("ID")
    return infos

def _get_image_infos(image):
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
    client = _get_client()
    infos = None
    try:
        infos = _set_id(client.inspect_image(image))
    except Exception:
        pass
    return infos

def _get_container_infos(container):
    '''
    Get container infos

    container
        Image Id / grain name

    return: dict
    '''
    client = _get_client()
    infos = None
    try:
        infos = _set_id(client.inspect_container(container))
    except Exception:
        pass
    return infos

def is_running(container, *args, **kwargs):
    '''
    Is this container running

    container
        Container id

    Return container
    '''
    try:
        infos = _get_container_infos(container)
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

def _parse_image_multilogs_string(ret, repo):
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
                    infos = _get_image_infos(repo)
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
    except Exception:
        comment += traceback.format_exc()
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

    if test_ports(port_bindings,length) is False:
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
def create_container(image,
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
    client = _get_client()
    try:
        img_infos = _get_image_infos(image)
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
        print "Container '%s' created."%info['id']
        return info
    except Exception as e:
        err = e
    error("Unable to create your container: %s"%err)
    return None


def stop(container, timeout=10, *args, **kwargs):
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
    client = _get_client()
    try:
        dcontainer = _get_container_infos(container)['id']
        if is_running(dcontainer):
            client.stop(dcontainer, timeout=timeout)
            if not is_running(dcontainer):
                print "Container stopped."
                return True
        else:
            print "Container not running."
            return True
    except Exception as e:
        err = e
    error("Unable to stop the container: %s"%err)
    return False


def kill(container, *args, **kwargs):
    '''
    Kill a running container

    :type container: string
    :param container: The container id to kill

    :rtype: dict
    :returns: boolean
    '''
    err = "Unknown"
    client = _get_client()
    try:
        dcontainer = _get_container_infos(container)['id']
        if is_running(dcontainer):
            client.kill(dcontainer)
            if not is_running(dcontainer):
                print "Container killed."
                return True
        else:
            print "Container not running."
            return True
    except Exception as e:
        err = e
    error("Unable to kill the container: %s"%err)
    return False


def remove_container(container=None, force=True, v=False, *args, **kwargs):
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
    client = _get_client()
    dcontainer = None
    try:
        try:
            dcontainer = _get_container_infos(container)['id']
        except Exception:
            print "Container not existing."
            return True
        else:
            if is_running(dcontainer):
                if not force:
                    print "ERROR: Container running, won't remove it."
                    return False
                else:
                    kill(dcontainer)
            client.remove_container(dcontainer, v=v)
            try:
                _get_container_infos(dcontainer)
            except Exception:
                print "Container has been successfully removed."
                return True
    except Exception as e:
        err = e
    error("Unable to remove container: %s"%err)
    return False


def restart(container, timeout=10, *args, **kwargs):
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
    client = _get_client()
    try:
        dcontainer = _get_container_infos(container)['id']
        client.restart(dcontainer, timeout=timeout)
        if is_running(dcontainer):
            print "Container restarted."
            return True
    except Exception as e:
        err = e
    error("Unable to restart the container: %s"%err)
    return False


def start(container, binds=None, ports=None, port_bindings=None,
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
    client = _get_client()
    try:
        dcontainer = _get_container_infos(container)['id']
        if not is_running(container):
            bindings = None
#            if port_bindings is not None:
#                print "Binding container ports ..."
#                bindings = {}
#                for k, v in port_bindings.iteritems():
#                    bindings[k] = (v.get('HostIp', ''), v['HostPort'])
            client.start(dcontainer, binds=binds, port_bindings=bindings,
                         lxc_conf=lxc_conf,
                         publish_all_ports=publish_all_ports, links=links,
                         privileged=privileged)
            if is_running(dcontainer):
                print "Container has been started."
                return _get_container_infos(container)
        else:
            print "Container is already started."
            return _get_container_infos(container)
    except Exception as e:
        err = e
    error("Unable to start your container: %s"%err)
    return None


def get_images(name=None, quiet=False, all=True, *args, **kwargs):
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
    client = _get_client()
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
    error("Unable to list Docker images: %s"%err)
    return None


def get_containers(all=True,
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
    client = _get_client()
    try:
        ret = client.containers(all=all,
                                trunc=trunc,
                                since=since,
                                before=before,
                                limit=limit)
        return ret
    except Exception as e:
        err = e
    error("Unable to list Docker containers: %s"%err)
    return None


def login(username=None, password=None, email=None, url=None, client=None, *args, **kwargs):
    '''
    Wrapper to the docker.py login method
    '''
    try:
        c = (_get_client() if not client else client)
        lg = c.login(username, password, email, url)
        print "%s logged to %s"%(username,(url if url else "default hub"))
    except Exception as e:
        error("%s can't login to repo %s: %s"%(username,(url if url else "default repo"),e))
        return False
    return True
##


## Docker App actions
def installed(name,
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
              force=False,
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
    iinfos = _get_image_infos(image)
    if not iinfos:
        error("Image not found.")
        return None
    cinfos = _get_container_infos(name)
    if cinfos:
        remove_container(container=name,force=True)
        print "Old container removed."

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
        print "Container created, id: %s"%(container.get("id"))
    else:
        error("Couldn't create container.")
    return container


def running(containers,
            image,
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
            force=False,
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
        warning("No container specified")
        return [], True

    if ports and port_bindings:
        (ports,port_bindings) = _gen_ports(ports,port_bindings,len(containers))
        if not ports or not port_bindings:
            error("Unable to generate port bindings (is there enough space between each allocation required?)")
            return [], True

    containers_out = []
    failure = False

    for container in containers:
        port = (ports.pop() if ports else None)
        port_binding = (port_bindings.pop() if port_bindings else None)
        ret = installed(
            container,image,entrypoint=entrypoint,command=command,environment=environment,
            ports=port,volumes=volumes,mem_limit=mem_limit,cpu_shares=cpu_shares,force=force)
        if ret:
            started = start(
                container, binds=binds, port_bindings=port_binding,
                lxc_conf=lxc_conf, publish_all_ports=publish_all_ports,
                links=links)
            if is_running(container) and started:
                print "Container started, id: %s"%started.get("id")
                containers_out.append(started)
            else:
                failure = True
                error("Unable to run container: %s - can't start"%container)
        else:
            failure = True
            error("Unable to run container: %s - can't install"%container)

    return containers_out, failure


def pull(repo, tag=None, username=None, password=None, email=None, *args, **kwargs):
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
    client = _get_client()
    try:
        if username:
            url = repo.split(":")
            url = (url[0] if len(url) > 1 else None)
            if not login(username,password,email,url):
                raise Exception("Can't login")
        ret = client.pull(repo, tag=tag)
        if ret:
            logs, infos = _parse_image_multilogs_string(ret, repo)
            if infos and infos.get('id', None):
                repotag = repo
                if tag:
                    repotag = '{0}:{1}'.format(repo, tag)
                print 'Repo {0} was pulled ({1})'.format(repotag, infos['id'])
                return infos
            else:
                error = _pull_assemble_error_status(logs)
    except Exception as e:
        err = e
    error("An error has occured pulling repo %s: %e"%(repo,err))
    return None
##


## Deploy
def _create_files(config, state_params, exec_params):
    volumes = []
    for f in state_params.get("files",{}):
        path = f.get("key")
        if not path:
            error("Unable to read config file path.")
            continue
        print "Configuration file found: %s."%path
        dir_path = os.path.join(config["config_path"],"docker","files",state_params["container"])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        host_path = os.path.join(dir_path,("%s"%key).replace('/','-'))
        content = f.get("value","")
        try:
            with open(host_path, 'w') as f:
                f.write(content)
        except Exception as e:
            error("Unable to store configuration file %s."%host_path)
            continue
        volumes.append({"key":host_path,"value":path})
    return exec_params.get("volumes",[])+volumes

def _replace_params(config, hostname, addin, param):
    config.setdefault(param,{})
    config[param].setdefault(hostname,{})
    config[param][hostname].setdefault(addin["container"],{})
    res = config[param][hostname][addin["container"]]
    if res:
        return [{"key":key,"value":res[key]} for key in res]
    return addin[param]

def _convert_running(config, hostname, addin):
    addin["port_bindings"] = _replace_params(config, hostname, addin,"port_bindings")
    addin["volumes"] = _replace_params(config, hostname, addin,"volumes")
    if addin.get("port_bindings"):
        ports = []
        pb = {}
        for item in addin["port_bindings"]:
            key = item.get("key",None)
            value = item.get("value",None)
            if not key or not value: continue

            # get user input
            ui = user_param(config,
                            "Update port binding for %s: %s:%s"%(addin["container"],key,value),
                            (None if not config["port_bindings"][hostname][addin["container"]] else "%s:%s"%(key,value)))
            # parse result
            if not ui: continue
            ui = ui.split(":")
            if len(ui) != 2: continue
            key, value = ui[0], ui[1]
            # persist
            config["port_bindings"][hostname][addin["container"]] = "%s:%s"%((key if key else ""),(value if value else ""))

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
            if not item.get("value") or not item.get("key"): continue
            value = item["value"]
            key = user_param(config, "Enter custom path for mount point %s"%value, item["key"])
            if not key: continue
            if config.get("chroot"):
                key = os.path.join(config["chroot"],key)
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
        addin["cpu_shares"] = user_param(config, "Enter custom cpu shares", addin["cpu_shares"])
    if addin.get("mem_limit"):
        mem = user_param(config, "Enter custom mememory limit", addin["mem_limit"])
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
            'command'       : 'command',
            'environment'   : 'environment',
            'volumes'       : 'volumes',
            'mem_limit'     : 'mem_limit',
            'cpu_shares'    : 'cpu_shares',
            'ports'         : 'ports',
            # running
            'publish_all_ports': 'publish_all_ports',
            'binds'         : 'binds',
            'links'         : 'links',
            'port_bindings' : 'port_bindings',
            'count'         : 'count',
            # deploy
            'files'         : _create_files,
        },
    },
    'split' : [
        "pull",
        "running"
    ],
    'convert': {
        "running": _convert_running,
    },
}


def deploy(config, hostname, state):
    if "container" not in state:
        error("Container name missing")
        return {}
    elif "image" not in state:
        error("Image name missing")
        return {}
    print "--> Preparing to run container(s) %s from image %s ..."%(state["container"],state["image"])
    out = {}
    for action in _deploy.get('split',[]):
        params = {}
        for param in _deploy.get('attr',{}).get(action,{}):
            if not state.get(param): continue
            if hasattr(_deploy['attr'][action][param], '__call__'):
                params.update(_deploy['attr'][action][param](config,state[param],params))
            elif type(state[param]) is list:
                params[_deploy['attr'][action][param]] = params.get(_deploy['attr'][action][param],[])+state[param]
            elif type(state[param]) is dict:
                params[_deploy['attr'][action][param]] = dict(params.get(_deploy['attr'][action][param],{}).items()
                                                              +state[param].items())
            else:
                params[_deploy['attr'][action][param]] = state[param]
        if hasattr(eval(action), '__call__'):
            if action in _deploy.get("convert",{}):
                params = _deploy["convert"][action](config, hostname, params)
            out[action] = eval(action)(*params, **params)
        else:
            error("Action not found: %s"%action)
    app = {}
    for container in out["running"]:
        name = container.get("name")
        print "--> Container successfully started %s."%name
        app[name] = container
    return app
##

#config = {
#    "interactive": True,
#    "chroot": "/docker",
#    "config_path": "~/.visualops",
#}

#app = {
#    "container_name": {
#        "container details"
#        ...
#    }
#    ...
#}

#TODO
def generate_hosts(app):
    hosts = {app[container]["NetworkSettings"]["IPAddress"]:[app[container]["Name"].replace('/','')] for container in app}
    for container in app:
        path = app[container]["HostsPath"]
