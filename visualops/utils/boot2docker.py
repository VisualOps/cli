'''
Boot2docker module (boot2docker wrapper)
@author: Thibault BRONCHAIN
(c) 2014 - MadeiraCloud LTD.
'''

import subprocess
from subprocess import PIPE
import re
import os
from visualops.utils import utils


# Check if boot2docker VM is running
def running(config, appid):
    try:
        out, err = subprocess.Popen(["boot2docker","status"],
                                    env=os.environ.copy().update(
                                        {"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)}
                                    ),
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception as e:
        return False
    return (True if re.search("running",out) else False)

# Get boot2docker VM IP
def ip(config, appid):
    try:
        out, err = subprocess.Popen(["boot2docker","ip"],
                                    env=os.environ.copy().update(
                                        {"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)}
                                    ),
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return "127.0.0.1"
    return out

# Run boot2docker VM
def run(config, appid):
    if running(config, appid) is not True:
        try:
            out, err = subprocess.Popen(["boot2docker","start"],
                                        env=os.environ.copy().update(
                                            {"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)}
                                        ),
                                        stdout=PIPE,stderr=PIPE).communicate()
#            if err:
#                utils.error(err)
        except Exception:
            pass
    return running(config, appid)

# Stop boot2docker VM
def stop(config, appid):
    if running(config, appid) is True:
        try:
            out, err = subprocess.Popen(["boot2docker","stop"],
                                        env=os.environ.copy().update(
                                            {"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)}
                                        ),
                                        stdout=PIPE,stderr=PIPE).communicate()
#            if err:
#                utils.error(err)
        except Exception:
            pass
    return not running(config, appid)

# Delete boot2docker VM
def delete(config, appid):
#    import pdb
#    pdb.set_trace()
    try:
        out, err = subprocess.Popen(["boot2docker","destroy"],
                                    env=os.environ.copy().update(
                                        {"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)}
                                    ),
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception:
        return False
    return (True if not err else False)

# Init boot2docker VM
def init(config, appid):
#    import pdb
#    pdb.set_trace()
    delete(config,appid)
    try:
        out, err = subprocess.Popen(["boot2docker","init"],
                                    env=os.environ.copy().update(
                                        {"BOOT2DOCKER_PROFILE":os.path.join(config["dirs"]["boot2docker"],"%s.cfg"%appid)}
                                    ),
                                    stdout=PIPE,stderr=PIPE).communicate()
    except Exception as e:
        print e
        return False
    if err:
        utils.error(err)
        return False
    return True

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
#        if err:
#            utils.error(err)
#            return False
    return True


# Test if has boot2docker
def has():
    try:
        subprocess.Popen(["boot2docker"],stdout=PIPE,stderr=PIPE).wait()
    except Exception:
        return False
    return True
