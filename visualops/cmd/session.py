# Copyright 2014 MadeiraCloud LTD.

import logging
import getpass
from visualops.utils import utils,rpc
from cliff.command import Command

class Login(Command):
    "Login in VisualOps. Once succeceed, the session will be persisted for the next 24 hours, or another login takes somewhere else."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Login, self).get_parser(prog_name)
        parser.add_argument('-u', action='store', dest='username', nargs='?', default='', help='VisualOps IDE login username')
        return parser

    def take_action(self, parsed_args):

        username = parsed_args.username
        if not username:
            username = raw_input('Enter usename or email:')
        if not username:
            raise RuntimeError('Must input a username')

        passwd = getpass.getpass('Your Password:')
        if not passwd:
            raise RuntimeError('Must input a password')

        # Login
        (err, result) = rpc.login(username, passwd)

        if err:
            utils.hanlde_error(err,result)
        else:

            print('\nLogin Success!')
            # Save session
            self.log.debug('> start save session...')
            utils.save_session(result)
            self.log.debug('> save session succeed')


class Logout(Command):
    "Logout from VisualOps, and remove the persisted temporary session"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            print 'Invalid login, no need logout!'
            return

        while True:
            confirm = raw_input('Are you sure to logout? [Y/n]:')
            if not confirm or confirm.lower() in ['y','n']:
                break

        if not confirm or confirm.lower() == 'y':
            # Logout
            (err, result) = rpc.logout(username, session_id)

            if err:
                utils.hanlde_error(err,result)
            else:
                print('\nLogout Success!')
