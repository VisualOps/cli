# Copyright 2014 MadeiraCloud LTD.

import logging
from visualops.utils import rpc,utils,constant
from cliff.lister import Lister


class List(Lister):
    "List your stacks in VisualOps"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('--filter', action='store', dest='filter_name', nargs='?', default='', help='filter by stack name')
        parser.add_argument('--region', action='store', dest='region_name', nargs='?', default='', help='specified region'  )
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()
 
        # get stack list
        (err, result) = rpc.stack_list(username, session_id, parsed_args.region_name)
        if err:
            print('Get stack list failed')
            utils.hanlde_error(err,result)
        else:
            self.log.debug('> get {0} stack(s) list succeed!\n'.format(len(result)))
            print "Stacks:"
            return (('Id', 'Name', 'Region', 'URL'),
                ((stack["id"], stack["name"], stack["region"], constant.IDE_URL + stack['id']) for stack in result if parsed_args.filter_name.lower() in stack['name'].lower() )
            )
