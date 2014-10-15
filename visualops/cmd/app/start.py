# Copyright 2014 MadeiraCloud LTD.

import logging
import json
import os

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
        config["force"] = False
        start_app(config, appname, app_dict)

    def start_app_old(self, config, appname, app_dict):
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
                            if dockervisops.start(config, cname):
                                app[cname] = dockervisops.get_container_infos(config,cname)
                                print "Container %s started"%cname
                            else:
                                utils.error("Unable to start container %s"%container_name)

        dockervisops.generate_hosts(config, app)

        print "App %s started."%appname


# Run stack
def start_app(config,appname,app_dict,force=False):
    config["appname"] = appname
    config["dirs"] = {
        "containers": os.path.join(config["config_path"],"docker","containers"),
        "boot2docker": os.path.join(config["config_path"],"docker","boot2docker"),
    }
    for d in config["dirs"]:
        if not os.path.exists(config["dirs"][d]):
            os.makedirs(config["dirs"][d])
    if boot2docker.has():
        print "Starting Boot2docker ... (this may take a while)"
        if not os.path.isfile(os.path.join(config["dirs"]["boot2docker"],"boot2docker.iso")):
            utils.download(config["boot2docker_iso"],os.path.join(config["dirs"]["boot2docker"],"boot2docker.iso"))

        if not boot2docker.gen_config(config, config["appname"]):
            utils.error("Unable to generate boot2docker configuration")
            return False
        boot2docker.mount(config["appname"], [{
            "volume": "visops_root",
            "hostpath": "/",
        },{
            "volume": "visops_containers",
            "hostpath": config["dirs"]["containers"],
        }])
        if boot2docker.run(config, config["appname"]):
            print "Boot2docker successfully running!"
        else:
            utils.error("Unable to run Boot2docker.")
        config["chroot"] = os.path.join("/mnt/host",config.get("chroot",""))
        config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,config["appname"]))
    config["hosts_table"] = app_dict.get("hosts_table",{})
    actions = {}
    for hostname in app_dict.get("hosts",{}):
        actions[hostname] = {}
        for state in app_dict["hosts"][hostname]:
            if state == "linux.docker.deploy":
                for container in app_dict["hosts"][hostname][state]:
                    app_dict["hosts"][hostname][state][container]["force"] = force
                    actions[hostname][container] = (dockervisops.preproc_deploy(config,
                                                                                config["appname"],
                                                                                hostname,
                                                                                app_dict["hosts"][hostname][state][container]))
    config["actions"] = actions
    app = {}
    for hostname in actions:
        for container in actions[hostname]:
            app.update(dockervisops.deploy(config, actions[hostname][container]))
    dockervisops.generate_hosts(config, app)

    #save user input parameter to app_dict
    utils.persist_app(actions,app_dict)
