import logging
import os.path
import ConfigParser

from visualops.utils import rpc
from cliff.show import ShowOne


class Info(ShowOne):
    "Show summary information for specified app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Info, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        home_folder = os.path.expanduser('~')
        ini_file    = home_folder + '/.visualops/session.ini'
        config      = ConfigParser.SafeConfigParser()
        config.read(ini_file)
        username   = config.get("config","username")
        session_id = config.get("config","session_id")

        # get app info
        (err, result) = rpc.app_info(username, session_id, parsed_args.region_name, [parsed_args.app_id])

        if err:
            raise RuntimeError('get app info failed:( ({0})'.format(err))
        else:
            self.app.stdout.write('get {0} app info succeed!\n'.format(len(result)))

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
