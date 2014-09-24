import logging
import getpass
from visualops.utils import utils
from visualops.utils import rpc
from cliff.command import Command

class Login(Command):
    "Login in VisualOps. Once succeceed, the session will be persisted for the next 24 hours, or another login takes somewhere else."

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        username = raw_input('Enter usename or email:')
        if not username:
            raise RuntimeError('must input a username')

        passwd = getpass.getpass('Your Password:')
        if not passwd:
            raise RuntimeError('must input a password')

        # Login
        (err, result) = rpc.login(username, passwd)

        if err:
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
        self.app.stdout.write('logout TO-DO!\n')
