import logging
import getpass
from visualops.utils import utils
from visualops.utils import rpc
from visualops.utils import constant
from cliff.command import Command

class Login(Command):
    "Login in VisualOps. Once succeceed, the session will be persisted for the next 24 hours, or another login takes somewhere else."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Login, self).get_parser(prog_name)
        parser.add_argument('-u', action='store', dest='username', nargs='?', default='', help='login username')
        return parser

    def take_action(self, parsed_args):

        username = parsed_args.username
        if not username:
            username = raw_input('Enter usename or email:')
        if not username:
            raise RuntimeError('must input a username')

        passwd = getpass.getpass('Your Password:')
        if not passwd:
            raise RuntimeError('must input a password')

        # Login
        (err, result) = rpc.login(username, passwd)

        if err:
            if err == constant.ERROR['UserInvalidUser']:
                raise RuntimeError('Invalid username or password'.format(err))
            elif err == constant.ERROR['UserNoUser']:
                raise RuntimeError('User {0} not existed'.format(username))
            else:
                raise RuntimeError('login failed:( ({0})'.format(err))
        else:

            print('\nSucceeded!')
            # Save session
            self.log.debug('>Start save session...')
            utils.save_session(result)
            self.log.debug('>Finish session succeed')


class Logout(Command):
    "Logout from VisualOps, and remove the persisted temporary session"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            print 'Invalid login, no need logout!'
            return


        # Logout
        (err, result) = rpc.logout(username, session_id)

        if err:
            if err == constant.ERROR['GlobalErrorSession']:
                raise RuntimeError('Your Session is invalid, no need logout!')
            else:
                raise RuntimeError('logout failed:( ({0})'.format(err))
        else:
            print('\nSucceeded!')
