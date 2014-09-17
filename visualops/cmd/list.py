from .utils import rpc

def lists(args):
	username, session_id = load_session()
	client   = rpc()

	if stack:
		stacks = client.stack_list()
		display_stack(stacks)
	if app:
		apps = client.app_list()
		display_app(apps)

def display_stack(stack):
	
def display_app(app):


