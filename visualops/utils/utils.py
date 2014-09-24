import os
import re
import sys
import os.path
import ConfigParser
import yaml
from datetime import date

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
        print ''
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

def require_login(f):
    def wrapper(*args, **kwargs):
        if settings.session_id is None:
            print 'Please login first'
            sys.exit(1)
        return f(*args, **kwargs)
    return wrapper


def error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def user_param(config, text, default):
    if not config.get("interactive"): return default
    print "%s [%s]: "%(text,default)
    res = raw_input().strip(' \t\n\r')
    return (res if res else default)


def dict2yaml(data):
    rlt = yaml.safe_dump(data)
    return rlt

def yaml2dict(data):
    rlt = yaml.load(data)
    return rlt
