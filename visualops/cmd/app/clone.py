# Copyright 2014 MadeiraCloud LTD.

import logging
import os
import yaml
import base64

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,rpc,constant,db
from visualops.utils.Result import Result

from visualops.cmd.stack.run import run_stack

class Clone(Command):
    "Clone a remote app to local"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Clone, self).get_parser(prog_name)
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        print 'Show remote app info....'

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()

        app_id = parsed_args.app_id

        print 'Pulling %s from remote ....\n' % app_id
        (err, result) = rpc.app_info(username, session_id, None, [app_id])

        if err:
            utils.hanlde_error(err,result)
        else:
            if len(result) == 0:
                print('The app does not exist\n')
                return (),()

            self.log.debug('> pull app %s succeed\n' %  app_id )

            app_json = result[0]
            del app_json['layout']
            del app_json['property']

            #generate yaml
            app = {
                'name'  : app_json['name'],
                'region': app_json['region'],
                'hosts' : {},
                'hosts_table' : {},
            }
            for (uid,comp) in app_json['component'].items():
                if unicode(comp['type']) == constant.RESTYPE['INSTANCE']:

                    app['hosts_table'][uid] = comp['name']

                    log_str = '> found instance {0}'.format(comp['name'])

                    if comp['state']:
                        log_str+=': has %s state(s)' % len(comp['state'])
                        hostname = comp['name']
                        container = {}
                        for (idx,state) in enumerate(comp['state']):
                            state_type = state['module']
                            if state_type == 'linux.docker.deploy':
                                container_name = state['parameter']['container']
                                if not container.has_key(state_type):
                                    container[state_type] = {}
                                container[state_type][container_name] = state['parameter']
                        app['hosts'][hostname] = container
                    else:
                        log_str+=': has no state'

                    self.log.debug(log_str)

            app_yaml = utils.dict2yaml(app)
            app_file = os.path.join(os.getcwd(), '%s.yaml' % app_id)
            with open(app_file,'w+') as f:
                f.writelines( app_yaml )

            self.log.debug( '\n> docker state info' )
            self.log.debug( '==============================================================' )
            self.log.debug( app_yaml )
            self.log.debug( '==============================================================' )
            self.app.stdout.write( '> %s is saved to %s\n' % (app_id, app_file) )

            print 'Done!'


            try:
                self.log.debug( "> load data from %s" % app_file )
                stream = open(app_file, 'r')
                app = yaml.load(stream)
            except Exception:
                raise RuntimeError('Load yaml error!')

            config = utils.gen_config(app.get("name","default-app"))
            is_succeed = False
            try:
                app['src_app_id'] = app_id
                app["name"] = config["appname"]
                self.clone_app(config, app)
                #insert app to local db
                db.create_app(config["appname"], config["appname"], app_id, app['region'], base64.b64encode(utils.dict2str(app)) )
                is_succeed = True
            except Result,e:
                print '!!!Expected error occur %s' % str(e.format())
            except Exception,e:
                print '!!!Unexpected error occur %s' % str(e)
            finally:
                if not is_succeed:
                    self.log.debug( '> Clear failed app info in local db' )
                    db.delete_app_info( config["appname"] )
                    raise RuntimeError('Clone app to local failed!')

    # Clone app
    def clone_app(self, config, app_dict):
        run_stack(config, app_dict)
