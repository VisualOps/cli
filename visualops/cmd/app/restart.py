# Copyright 2014 MadeiraCloud LTD.

import logging
import json

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,db,constant
from visualops.utils.Result import Result


class Restart(Command):
    "Restart app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Restart, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='local', help='restart local app')
        parser.add_argument('-f', '--force', action='store_true', dest='force', help='force restart app')
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
                if not parsed_args.force and state != constant.STATE_APP_RUNNING:
                    raise RuntimeError("App current state is {0}, only support restart 'Running' app!".format(state))

                print 'Restarting local app ...'
                #2. update to restarting
                db.restart_app(appname)
                #3. do action
                self.restart_app(config, appname, app)
                #4. update to running
                db.restart_app(appname,True)
                print 'Local app %s restarted!' % appname
                is_succeed = True
            except Result,e:
                print '!!!Expected error occur %s' % str(e.format())
            except Exception,e:
                print '!!!Unexpected error occur %s' % str(e)
            finally:
                if not is_succeed:
                    raise RuntimeError('App restart failed!')
        else:
            print 'Restart remote app ...(not support yet, please try -l)'
            return


    # Restart app
    def restart_app(self, config, appname, app_dict):

        if boot2docker.has():
            boot2docker.run(config, appname)
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        app = {}
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
                            if dockervisops.restart(config, cname) is True:
                                app[cname] = dockervisops.get_container_infos(config,cname)
                                print "Container %s restarted"%cname
                            else:
                                utils.error("Unable to restart container %s"%container_name)

        dockervisops.generate_hosts(config, app)

        print "App %s restarted."%appname
