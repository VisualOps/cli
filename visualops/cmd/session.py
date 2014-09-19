import logging
import os.path
import getpass
from visualops.utils import rpc
from cliff.command import Command

class Login(Command):
    "Login in VisualOps. Once succeceed, the session will be persisted for the next 24 hours, or another login takes somewhere else."
    #store session to ~/.visualops/session.ini

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        username = raw_input('Enter usename or email:')
        if not username:
            raise RuntimeError('must input a username')

        passwd = getpass.getpass('Your Password:')
        if not passwd:
            raise RuntimeError('must input a password')

        # login
        (err, result) = rpc.login(username, passwd)

        if err:
            raise RuntimeError('login failed:( ({0})'.format(err))
        else:
            self.app.stdout.write('login succeed!\n')
            home_folder = os.path.expanduser('~')
            #ensure ~/.visualops exist
            if os.path.isdir(home_folder + '/.visualops'):
                pass
            else:
                os.mkdir(home_folder + '/.visualops')
            #store session info to ~/.visualops/session.ini
            ini_file = home_folder + '/.visualops/session.ini'
            with open( ini_file, 'w+') as file:
                file.write("[config]\n")
                k, v = result.keys(), result.values()
                for i in range(len(k)):
                    file.write( k[i] + " = " + unicode(str(v[i])) + "\n" )
            self.app.stdout.write( 'wrote to {0} succeed!\n'.format(ini_file) )


class Logout(Command):
    "Logout from VisualOps, and remove the persisted temporary session"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.app.stdout.write('logout TO-DO!\n')
