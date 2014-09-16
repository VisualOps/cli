from ../utils import rpc

def login(args):
	username = raw_input('Please enter your account name or registered email: ')
	if not username:

	passwd = raw_input('Please enter your password: ')

	# login
	(err, client) = rpc.login(username, password)
	if err:
	else:
		with open(os.path.join(os.environ['HOME']), '/.visualops/login', 'w+') as f:
			f.write()
