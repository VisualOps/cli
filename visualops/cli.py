import os
import sys
import getpass
import argparse

from __init__ import __version__
from .utils import settings, utils
from . import cmd
	
def print_shared_with(users):
	print 'shared with:'
	for user in users:
		print '  {0} ({0})'.format(user.permalink, user.permalink_url)

def main():
	#viso list stack
	#viso list app [--local / aws]
	#viso pull stack-id
	#viso run stack-id [--local / aws]
	#viso run -f stack_yaml [--local / aws]
	#viso login
	#viso logout
	
	# load session
	session = Session(os.path.join(os.environ['HOME']), '/.visualops/session')
	
	# setup args
	parser = argparse.ArgumentParser('VisualOps CLI: www.visualops.io')
	parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

	subparsers = parser.add_subparsers()

	login_parser = subparsers.add_parser('login', help='login')
	login_parser.set_defaults(command=cmd.login)

	logout_parser = subparsers.add_parser('logout', help='logout')
	logout_parser.set_defaults(command=cmd.logout)

	list_parser = subparsers.add_parser('list', help='list stack or app')
	list_parser.add_argument('stack', action='store_const', dest='list_stack', help='list stack')
	list_parser.add_argument('app', action='store_const', dest='list_app', help='list app')
	list_parser.add_argument('-l', '--local', action='store_true', dest='list_app_local', help='list local apps only')
	list_parser.add_argument('-a', '--aws', action='store_true', dest='list_app_aws', help='list apps at AWS only')
	list_parser.set_defaults(command=cmd.list)

	pull_parser = subparsers.add_parser('pull', help='pull a stack from origin')
	pull_parser.add_argument('id', help='the stack id')
	pull_parser.set_defaults(command=cmd.pull)

	push_parser = subparsers.add_parser('push', help='push a stack to origin')
	push_parser.add_argument('id', help='the stack id')
	push_parser.set_defaults(command=cmd.push)

	run_parser = subparsers.add_parser('run', help='deploy the stack')
	run_parser.add_argument('id', help='the stack id)
	run_parser.add_argument('--public', action='store_true', help='make track public')
	run_parser.add_argument('-l', '--local', action='store_true', dest='run_stack_local', help='deploy the stack locally')
	run_parser.add_argument('-a', '--aws', action='store_true', dest='run_stack_aws', help='deplocal the stack at AWS')
	run_parser.set_defaults(command=cmd.run)

	# default to login command
	if sys.argv[1:]:
		choices = subparsers.choices.keys()
		choices += ['-h', '--help', '-v', '--version']

		# unless recognized command is passed, treat first argument as login
		if sys.argv[1] not in choices:
			sys.argv = [sys.argv[0], 'login']

	args = parser.parse_args()

	try:
		args.command(args)
	except KeyboardInterrupt:
		print
		sys.exit(1)
