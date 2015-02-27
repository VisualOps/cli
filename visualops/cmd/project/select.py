# Copyright 2014 MadeiraCloud LTD.

import logging
from visualops.utils import rpc,utils,constant
from cliff.command import Command


class Select(Command):
    "Set current projects"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Select, self).get_parser(prog_name)
        parser.add_argument('project_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return None

        project_id = parsed_args.project_id
        if not project_id:
            print "project_id can not be empty"
            return None

        # get project list
        (err, result) = rpc.project_list(username, session_id, project_id)
        if err:
            print('Get project list failed')
            utils.hanlde_error(err,result)
        else:
            self.log.debug('> get {0} project(s) list succeed!\n'.format(len(result)))

            #set current workspace
            if len(result) == 1:
                current_project = result[0]
                utils.set_current_project(current_project)
                print 'Select "%s" as current project\n' % (current_project["name"] if 'name' in current_project else constant.DEFAULT_PROJECT)
