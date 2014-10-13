#Copyright 2014 MadeiraCloud LTD.

from __future__ import print_function
import os
import re
import sys
import os.path
import ConfigParser
import yaml
import urllib2
import contextlib
import logging
from datetime import date
from prettytable import PrettyTable
from visualops.utils import constant

DEFAULT_YEAR  = date.today().year
PROGRESS_RE = re.compile(r'\((\s?\d+)%\)')

def save_session(result):
    try:
        home_folder = os.path.expanduser('~')

        #Ensure ~/.visualops exist
        if os.path.isdir(home_folder + '/.visualops'):
            pass
        else:
            os.mkdir(home_folder + '/.visualops')

        #Save session to ~/.visualops/session
        ini_file = home_folder + '/.visualops/session'
        with open( ini_file, 'w+') as file:
            output = '[config]\n'
            output += 'username = ' + result['username'] + '\n'
            output += 'session_id = ' + result['session_id'] + '\n'
            file.write( output )

    except Exception:
        return False


def load_session():
    try:
        home_folder = os.path.expanduser('~')
        ini_file    = home_folder + '/.visualops/session'
        if not os.path.isfile(ini_file):
            print('please login first!')
            return (None, None)
        config      = ConfigParser.SafeConfigParser()
        config.read(ini_file)
        username   = config.get('config','username')
        session_id = config.get('config','session_id')
        return (username, session_id)
    except:
        print('load session failed, try login again!')
        return (None, None)

#Handle AppService Error
def hanlde_error(err, result):
    if err:
        err_msg = constant.ERROR[err]
        if err_msg:
            log = logging.getLogger(__name__)
            log.debug('>AppService return code : %s' % err)
            raise RuntimeError(err_msg)
        else:
            raise RuntimeError('Uncaught exception (%s) %s' % (err,result))

class Progress(object):
    def __init__(self, filename=None):
        self.filename = filename

    def __call__(self, line):
        percent   = int(PROGRESS_RE.search(line).groups()[0])
        bars      = percent / 2
        done      = '=' * bars
        remaining = ' ' * (50 - bars)

        sys.stdout.write('\rcompressing {0} [{1}{2}] {3}%'.format(self.filename, done, remaining, percent))
        sys.stdout.flush()

def copy_to_clipboard(text):
    # reliable on mac
    if sys.platform == 'darwin':
        os.system('echo "{0}" | pbcopy'.format(text))
        return

    # okay we'll try cross-platform way
    try:
        from Tkinter import Tk
    except ImportError:
        return

    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text.encode('ascii'))
    r.destroy()

def open_browser(url):
    import webbrowser

    webbrowser.open_new_tab(url)

#def require_login(f):
#    def wrapper(*args, **kwargs):
#        if settings.session_id is None:
#            print('Please login first')
#            sys.exit(1)
#        return f(*args, **kwargs)
#    return wrapper


def error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def user_param(config, text, default):
    if not config.get("interactive"): return default
    print("%s (use '-' for None) [%s]: "%(text,default))
    res = raw_input().strip(' \t\n\r')
    res = (res if res else default)
    return (res if res != "-" else None)

def dict2yaml(data):
    rlt = yaml.safe_dump(data)
    return rlt

def yaml2dict(data):
    rlt = yaml.load(data)
    return rlt

def dict2str(data):
    return str(data)

def str2dict(str):
    return eval(str)

# Pretty Print table in tabular format
def print_prettytable(title,rows):
    x = PrettyTable(title)
    x.padding_width = 1 # One space between column edges and contents (default)
    for col in title:
        x.align[col] = "l"
    for row in rows:
        x.add_row(row)
    return x

# Downlaod file with progress bar
def download(url, file_name=None, verbose=True):
    if not file_name:
        file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: %s Bytes:%s"%(file_name, file_size))
    file_size_dl = 0
    block_sz = 8*1024
    buf = ""
    while True:
        buf = u.read(block_sz)
        if not buf:
            break
        file_size_dl += len(buf)
        f.write(buf)
        if verbose:
            status = r"%10d  [%3.2f%%]"%(file_size_dl,file_size_dl*100./file_size)
            status = status + chr(8)*(len(status)+1)
            print(status,end="")
    f.close()
    print("%10d  [100.00%%]"%(file_size_dl))

# mute call
class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    save_stderr = sys.stderr
    sys.stderr = DummyFile()
    yield
    sys.stdout = save_stdout
    sys.stderr = save_stderr

# configuration generator
def gen_config(appname=None):
    return ({
        "appname" : appname,
        "interactive": True,
        "config_path": os.path.expanduser("~/.visualops"),
        "boot2docker_iso": "https://s3.amazonaws.com/visualops-cli/boot2docker.iso",
    })


# Save user input to app_dict
def persist_app(actions, app_dict):
    for (host,v1) in  actions.items():
        for (container,v2) in v1.items():
            try:
                #save source to target
                app_dict_container = app_dict['hosts'][host]['linux.docker.deploy'][container]  #target
                actions_container  = actions[host][container]['running']                        #source

                #1. save count
                if actions_container.has_key('count'):
                    app_dict_container['count'] = actions_container['count']

                #2. save volume
                if actions_container.has_key('binds'):
                    app_dict_volumes = []
                    action_volumes   = actions_container['binds']
                    for (volume,v3) in action_volumes.items():
                        mountpoint = {}
                        mountpoint['key']   = volume
                        mountpoint['value'] = v3['bind']
                        app_dict_volumes.append(mountpoint)
                    app_dict_container['volumes'] = app_dict_volumes

                #3. save port_bindings
                if actions_container.has_key('port_bindings'):
                    app_dict_port_bindings = []
                    actions_port_bindings  = actions_container['port_bindings']
                    for (port,v4) in actions_port_bindings.items():
                        bingding = {}
                        bingding['key']   = v4['HostPort']
                        bingding['value'] = port
                        app_dict_port_bindings.append(bingding)
                    app_dict_container['port_bindings'] = app_dict_port_bindings

            except Exception,e:
                raise RuntimeError("Save user's input failed! %s" % e)
