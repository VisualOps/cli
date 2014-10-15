# Copyright 2014 MadeiraCloud LTD.

import logging
import json

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,db,constant
from visualops.utils.Result import Result


class Start(Command):
    "Start an stopped app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Start, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='local', help='start local app')
        parser.add_argument('-f', '--force', action='store_true', dest='force', help='force start app')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        app_id = parsed_args.app_id

        #get app data from local db
        (appname,app) = db.get_app_data( app_id )
        if not (appname and app):
            raise RuntimeError('Can not find local app {0}'.format(app_id))

        self.log.debug( '==============================================================' )
        self.log.debug("> found app %s in local db" % appname)
        self.log.debug("> app_data")
        self.log.debug( json.dumps(app, indent=4) )
        self.log.debug( '==============================================================' )

        config = utils.gen_config(appname)

        if parsed_args.local:
            is_succeed = False
            try:
                #1. check app state
                state = db.get_app_state(appname)
                if not parsed_args.force and state != constant.STATE_APP_STOPPED:
                    raise RuntimeError("App current state is {0}, only support stop 'Stopped' app!".format(state))

                print 'Starting local app ...'
                #2. update to starting
                db.start_app(appname)
                #3. do action
                self.start_app(config, appname, app)
                #4. update to running
                db.start_app(appname,True)
                print 'Local app %s started!' % appname
                is_succeed = True
            except Result,e:
                print '!!!Expected error occur %s' % str(e.format())
            except Exception,e:
                print '!!!Unexpected error occur %s' % str(e)
            finally:
                if not is_succeed:
                    raise RuntimeError('App start failed!')
        else:
            print 'Start remote app ...(not support yet, please try -l)'
            return


    # Start app
    def start_app(self, config, appname, app_dict):

        if boot2docker.has():
            boot2docker.run(config, appname)
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        for hostname in app_dict.get("hosts",{}):
            for state in app_dict["hosts"][hostname]:
                if state == "linux.docker.deploy":
                    for container in app_dict["hosts"][hostname][state]:
                        container_name = "%s-%s-%s"%(appname,hostname,container)
                        containers = ([container_name]
                                      if not app_dict["hosts"][hostname][state][container].get("count")
                                      else ["%s_%s"%(container_name,i)
                                            for i in range(1,int(app_dict["hosts"][hostname][state][container]["count"])+1)])
                        for cname in containers:
                            if dockervisops.start(config, cname):
                                print "Container %s started"%cname
                            else:
                                utils.error("Unable to start container %s"%container_name)

        print "App %s started."%appname
