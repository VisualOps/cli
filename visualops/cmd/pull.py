from .. import settings
from .client import get_client

def pull(args):
	username, session_id = load_session()
	client   = rpc()

	print 'pulling %s from visualops.io ....' % stack['id']
	stack = client.stack_info()
	with open(os.path.join(os.getcwd(), '/%s.yaml' % stack['id'])) as f:
		f.writelines(stack)
	print '%s is cloned locally' % stack['id']
