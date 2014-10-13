'''
Boot2docker module (boot2docker wrapper)
@author: Thibault BRONCHAIN
Copyright 2014 MadeiraCloud LTD.
'''

import subprocess
from subprocess import PIPE
import re
import os
from visualops.utils import utils


# Check if boot2docker VM is running
def running(config, appid, verbose=False):
    try:
        env = os.environ.copy()
        env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
        out, err = subprocess.Popen(["boot2docker","status"],
                                    env=env,
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return False
    if not re.search("running",out): return False
    if verbose:
        print "Boot2docker VM ip: %s\nTo use the docker client in a terminal, set the following environment variable:\n\n%s"%(
            ip(config,appid),
            shellinit(config,appid)
        )
    return True

# Get boot2docker VM IP
def ip(config, appid):
    try:
        env = os.environ.copy()
        env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
        out, err = subprocess.Popen(["boot2docker","ip"],
                                    env=env,
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return "127.0.0.1"
    return out

# Run boot2docker VM
def run(config, appid, verbose=True):
    if running(config, appid, verbose) is not True:
        try:
            env = os.environ.copy()
            env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
            out, err = subprocess.Popen(["boot2docker","start"],
                                        env=env,
                                        stdout=PIPE,stderr=PIPE).communicate()
            return running(config, appid, verbose)
        except Exception:
            pass
    return running(config, appid, verbose=False)

# Stop boot2docker VM
def stop(config, appid):
    if running(config, appid) is True:
        try:
            env = os.environ.copy()
            env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
            out, err = subprocess.Popen(["boot2docker","stop"],
                                        env=env,
                                        stdout=PIPE,stderr=PIPE).communicate()
        except Exception:
            pass
    return not running(config, appid)

# Delete boot2docker VM
def delete(config, appid):
    try:
        env = os.environ.copy()
        env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
        out, err = subprocess.Popen(["boot2docker","destroy"],
                                    env=env,
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return False
    return (True if not err else False)

# Init boot2docker VM
def init(config, appid):
    delete(config,appid)
    try:
        env = os.environ.copy()
        env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
        out, err = subprocess.Popen(["boot2docker","init"],
                                    env=env,
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception as e:
        return False
    if err:
        utils.error(err)
        return False
    return True

# Get boot2docker shell init
def shellinit(config, appid):
    try:
        env = os.environ.copy()
        env.update({"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)})
        out, err = subprocess.Popen(["boot2docker","shellinit"],
                                    env=env,
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return ""
    return out

# Generates configuration file
def gen_config(config, appid, replace=True):
    if os.path.isfile(os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)) and not replace:
        return True
    try:
        out, err = subprocess.Popen(["boot2docker","config"],
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        out = None
    if not out:
        return False
    conf = {
        "VM":"\"%s\""%appid,
        "Dir":"\"%s\""%config["dirs"]["boot2docker"],
        "ISO":"\"%s\""%os.path.join(config["dirs"]["boot2docker"],"boot2docker.iso"),
        "SerialFile":"\"%s\""%os.path.join(config["dirs"]["boot2docker"],"%s.sock"%appid),
    }
    out = re.sub(r"boot2docker profile filename:(.*)\n","", out)
    for key in conf:
        out = re.sub(r"%s = (.*)\n"%(key),"%s = %s\n"%(key,conf[key]),out)
    with open(os.path.join(config["dirs"]["boot2docker"],
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
            utils.error(e)
            return False
    return True


# Test if has boot2docker
def has():
    try:
        subprocess.Popen(["boot2docker"],stdout=PIPE,stderr=PIPE).wait()
    except Exception:
        return False
    return True
