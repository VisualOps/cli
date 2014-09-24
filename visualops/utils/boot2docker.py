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
        return ""
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
def mount(volumes):
    '''
    volumes: [{
        "volume": "root",
        "mountpoint": "/"
    },
    ...
    ]
    '''
    stop()
    # TODO mount here
    return run()

# Test if has boot2docker
def has():
    try:
        subprocess.Popen(["boot2docker"]).wait()
    except Exception:
        return False
    return True



# TODO
# Run app
def run(config, appid):
    if not gen_config(config, appid):
        error("Unable to generate boot2docker configuration")
        return False

    mount([{
        "volume": "root",
        "mountpoint": "/",
    },{
        "volume": "containers",
        "mountpoint": os.path.join(config["config_path"],"docker","containers"),
    }])
