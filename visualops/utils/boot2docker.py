'''
Boot2docker module (boot2docker wrapper)
@author: Thibault BRONCHAIN
(c) 2014 - MadeiraCloud LTD.
'''

import subprocess
import re
import os
from utils import error,warning

# Check if boot2docker VM is running
def running(config, appid):
    try:
        out, err = subprocess.Popen(["boot2docker","status"],
                                    env={"BOOT2DOCKER_PROFILE":os.path.join(config["config_path"],
                                                                            "docker",
                                                                            "boot2docker",
                                                                            "%s.cfg"%appid)},
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return False
    return (True if re.search(out,"running") else False)

# Get boot2docker VM IP
def ip(config, appid):
    try:
        out, err = subprocess.Popen(["boot2docker","ip"],
                                    env={"BOOT2DOCKER_PROFILE":os.path.join(config["config_path"],
                                                                            "docker",
                                                                            "boot2docker",
                                                                            "%s.cfg"%appid)},
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return "127.0.0.1"
    return out

# Run boot2docker VM
def run(config, appid):
    if running() is not True:
        try:
            out, err = subprocess.Popen(["boot2docker","start"],
                                        env={"BOOT2DOCKER_PROFILE":os.path.join(config["config_path"],
                                                                                "docker",
                                                                                "boot2docker",
                                                                                "%s.cfg"%appid)},
                                        stdout=PIPE,stderr=PIPE).communicate()
            if err:
                error(err)
        except Exception:
            pass
    return running()

# Stop boot2docker VM
def stop(config, appid):
    if running() is True:
        try:
            out, err = subprocess.Popen(["boot2docker","stop"],
                                        env={"BOOT2DOCKER_PROFILE":os.path.join(config["config_path"],
                                                                                "docker",
                                                                                "boot2docker",
                                                                                "%s.cfg"%appid)},
                                        stdout=PIPE,stderr=PIPE).communicate()
            if err:
                error(err)
        except Exception:
            pass
    return not running()

# Delete boot2docker VM
def delete(config, appid):
    try:
        out, err = subprocess.Popen(["boot2docker","destroy"],
                                    env={"BOOT2DOCKER_PROFILE":os.path.join(config["config_path"],
                                                                            "docker",
                                                                            "boot2docker",
                                                                            "%s.cfg"%appid)},
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return False
    return (True if not err else False)

# Init boot2docker VM
def init(config, appid):
    delete(config,appid)
    try:
        out, err = subprocess.Popen(["boot2docker","init"],
                                    env={"BOOT2DOCKER_PROFILE":os.path.join(config["config_path"],
                                                                            "docker",
                                                                            "boot2docker",
                                                                            "%s.cfg"%appid)},
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return False
    if err:
        error(err)
        return False
    return True

# Generates configuration file
def gen_config(config, appid):
    try:
        out, err = subprocess.Popen(["boot2docker","config"],
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        out = None
    if not out:
        return False
    conf = {
        "VM":appid,
        "Dir":os.path.join(config["config_path"],"docker","boot2docker"),
        "ISO":os.path.join(config["config_path"],"docker","boot2docker","boot2docker.iso"),
        "SerialFile":os.path.join(config["config_path"],"docker","boot2docker","%s.sock"%appid),
    }
    for key in conf:
        out = re.sub(r"%s = (.*)\n"%(key),"%s = %s\n"%(key,conf[key]),out)
    with open(os.path.join(config['config_path'],
                           "docker",
                           "boot2docker",
                           "%s.cfg"%appid), 'w') as f:
        f.write(out)
    return True

# Mount volume to boot2docker VM
def mount(name,volumes):
    '''
    volumes: [{
        "volume": "root",
        "hostpath": "/"
    },
    ...
    ]
    '''
    for vol in volumes:
        try:
            out, err = subprocess.Popen(["VBoxManage","sharedfolder","add",name,"--name",vol["volume"],"--hostpath",vol["hostpath"]],
                                        stdout=PIPE,stderr=PIPE).communicate()
        except Exception as e:
            error(e)
            return False
        if err:
            error(err)
            return False
    return True


# Test if has boot2docker
def has():
    try:
        subprocess.Popen(["boot2docker"]).wait()
    except Exception:
        return False
    return True




# TODO move
# Run app
def run(config, app_dict):
    appname = user_param(config, "Enter app name",app_dict.get("name","default-app"))
    if boot2docker.has():
        if not gen_config(config, appid):
            error("Unable to generate boot2docker configuration")
            return False
        boot2docker.delete(config, appid)
        boot2docker.mount(appname[{
            "volume": "root",
            "hostpath": "/",
        },{
            "volume": "containers",
            "hostpath": os.path.join(config["config_path"],"docker","containers"),
        }])
        boot2docker.start(config, appid)
        config["chroot"] = os.path.join("/mnt/host",config.get("chroot"))
        config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appid))
    app = {}
    config["hosts_table"] = app_dict.get("hosts_table")
    for hostname in app_dict.get("hosts",{}):
        for state in app_dict[hostname]:
            if state == "linux.docker.deploy":
                for container in app_dict[hostname][state]:
                    app.update(docker.deploy(config, appname, hostname, app_dict[hostname][state][container]))
    docker.generate_hosts(config, app)
