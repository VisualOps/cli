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
        parser.add_argument('region_name', nargs='?', default='', help='region of stack')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()
 
        # get stack list
        (err, result) = rpc.stack_list(username, session_id, parsed_args.region_name)
        if err:
            if err == constant.E_SESSION:
                raise RuntimeError('Your Session is invalid, please re-login!')
            else:
                raise RuntimeError('get stack list failed:( ({0})'.format(err))
        else:
            self.log.debug('>get {0} stack(s) list succeed!\n'.format(len(result)))
            url = "https://ide.mc3.io/ops/"
            print "Stacks:"
            return (('Name', 'Region', 'Id', 'URL', 'Position' ),
                ((stack["name"], stack["region"], stack["id"], url+stack["id"], 'remote') for stack in result)
            )
