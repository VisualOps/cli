import os
import re
import subprocess
import sys
from datetime import date

DEFAULT_YEAR  = date.today().year
PROGRESS_RE = re.compile(r'\((\s?\d+)%\)')

def load_session:
	with open(os.path.join(os.environ['HOME']), '.visualops/session') as f:
		yaml = f.readlines()
	return (yaml.username, yaml.session_id)

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
