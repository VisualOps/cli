import logging
from visualops.utils import rpc
from visualops.utils import utils
from visualops.utils import constant
from cliff.lister import Lister


class List(Lister):
    "List your stacks, locally or on AWS"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('--filter', action='store', dest='filter_name', nargs='?', default='', help='filter by stack name')
        parser.add_argument('--region', action='store', dest='region_name', nargs='?', default='', help='specified region')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()
 
        # get stack list
        (err, result) = rpc.stack_list(username, session_id, parsed_args.region_name)
        if err:
            if err == constant.ERROR['GlobalErrorSession']:
                raise RuntimeError('Your Session is invalid, please re-login!')
            else:
                raise RuntimeError('get stack list failed:( ({0})'.format(err))
        else:
            print parsed_args.filter_name
            self.log.debug('>get {0} stack(s) list succeed!\n'.format(len(result)))
            url = "https://ide.mc3.io/ops/"
            print "Stacks:"
            return (('Id', 'Name', 'Region', 'URL'),
                ((stack["id"], stack["name"], stack["region"], url+stack["id"]) for stack in result if parsed_args.filter_name.lower() in stack['name'].lower() )
            )
