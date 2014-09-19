import logging
import os.path
import ConfigParser

from visualops.utils import rpc
from cliff.lister import Lister
from cliff.show import ShowOne

class List(Lister):
    "get stack name list"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='us-east-1')
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
            return (('Id', 'Name', 'State'),
                ((stack["id"], stack["name"], stack["state"]) for stack in result)
            )



class Info(ShowOne):
    "get stack name info"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Info, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='us-east-1')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        home_folder = os.path.expanduser('~')
        ini_file    = home_folder + '/.visualops/session.ini'
        config      = ConfigParser.SafeConfigParser()
        config.read(ini_file)
        username   = config.get("config","username")
        session_id = config.get("config","session_id")

        # get stack info
        (err, result) = rpc.stack_info(username, session_id, parsed_args.region_name, [parsed_args.stack_id])

        if err:
            raise RuntimeError('get stack info failed:( ({0})'.format(err))
        else:
            self.app.stdout.write('get {0} stack info succeed!\n'.format(len(result)))

            columns = ('Name',
                       'CloudType',
                       'Provider',
                       'Component',
                       )
            data = (result[0]["name"],
                    result[0]["cloud_type"],
                    result[0]["provider"],
                    len(result[0]["component"]),
                    )
            return (columns, data)
