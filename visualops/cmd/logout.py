from .. import settings

def logout(args):
	os.remove(os.path.join(os.environ['HOME']), '/.visualops/session')
