import logging
import os.path
import ConfigParser

from visualops.utils import rpc
from cliff.lister import Lister


class List(Lister):
    "List your stacks, locally or on AWS"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        home_folder = os.path.expanduser('~')
        ini_file    = home_folder + '/.visualops/session.ini'
        config      = ConfigParser.SafeConfigParser()
        config.read(ini_file)
        username   = config.get("config","username")
        session_id = config.get("config","session_id")
 
        # get stack list
        (err, result) = rpc.stack_list(username, session_id, parsed_args.region_name)
        # import pudb
        # pudb.set_trace()

        if err:
            raise RuntimeError('get stack list failed:( ({0})'.format(err))
        else:
            self.app.stdout.write('get {0} stack list succeed!\n'.format(len(result)))
            return (('Region', 'Id', 'Name', 'State'),
                ((stack["region"], stack["id"], stack["name"], stack["state"]) for stack in result)
            )
