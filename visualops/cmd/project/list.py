# Copyright 2014 MadeiraCloud LTD.

import logging
import os
import os.path
from visualops.utils import rpc,utils,constant
from cliff.lister import Lister


class List(Lister):
    "List your projects in VisualOps"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('--filter', action='store', dest='filter_name', nargs='?', default='', help='filter by project name')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()

        # get project list
        (err, result) = rpc.project_list(username, session_id)
        if err:
            print('Get project list failed')
            utils.hanlde_error(err,result)
        else:
            self.log.debug('> get {0} project(s) list succeed!\n'.format(len(result)))

            #set current workspace
            if len(result) > 0:

                home_folder = os.path.expanduser('~')
                project_cfg = home_folder + '/.visualops/project'
                project_name=""
                current_project = None

                if os.path.isfile(project_cfg):
                    (project_name, project_id, key_id) = utils.load_current_project()

                for project in result:
                    if not 'name' in project:
                        my_project = project
                    else:
                        if project['name'] == project_name:
                            current_project = project
                if not current_project:
                    current_project = my_project
                utils.set_current_project(current_project)
                print '\n"%s" is current project' % (current_project["name"] if 'name' in current_project else constant.DEFAULT_PROJECT)
                print 'Please run "visualops project select <project id>" to set current project.\n'

            print "Projects:"
            return (('Id', 'Name', 'URL'),
                ((project["id"], project["name"] if 'name' in project else constant.DEFAULT_PROJECT, constant.IDE_URL + project['id']) for project in result if ( 'name' in project and parsed_args.filter_name.lower() in project['name'].lower()) or (not 'name' in project) )
            )
