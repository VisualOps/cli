import logging
import os
import yaml
import json
import uuid
from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,db


class Run(Command):
    "Deploy the stack locally, or in the cloud"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='run_stack_local', help='deploy the stack locally')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        stack_id = parsed_args.stack_id

        stack_file = os.path.join(os.getcwd(), '%s.yaml' % stack_id)
        if not os.path.isfile(stack_file):
            print( '%s does not exist, please pull stack first!' % stack_file )
            return

        if parsed_args.run_stack_local:
            print 'Deploying %s.yaml ......' % stack_id
        else:
            print 'Deploying %s.yaml to remote (not support yet, please try -l)....' % stack_id
            return

        try:
            self.log.debug( ">Load data from %s" % stack_file )
            stream = open(stack_file, 'r')
            app = yaml.load(stream)
        except Exception:
            raise RuntimeError('Load yaml error!')

        if not app:
            raise RuntimeError('stack json is invalid!')

        self.log.debug( '==============================================================' )
        self.log.debug( json.dumps(app, indent=4) )
        self.log.debug( '==============================================================' )

#        #generate app_id
#        app_id = 'app-%s' % str(uuid.uuid4())[:8]
#
#        config = {
#            "app_id" : app_id,
#            "interactive": True,
#            "config_path": os.path.expanduser("~/.visualops"),
#            "boot2docker_iso": "https://s3.amazonaws.com/visualops-cli/boot2docker.iso",
#            "volumes": {
#                "hostname": {
#                    "container": {
#                        "/foo": "/bar",
#                    },
#                },
#            },
#            "cpu_shares": {
#                "hostname": {
#                    "container": "1",
#                },
#            },
#            "mem_limit": {
#                "hostname": {
#                    "container": "512m",
#                },
#            },
#            "chroot": "/path",
#            "port_bindings": {
#                "hostnameA": {
#                    "containerA": {
#                        "0.0.0.0:80": "80/tcp",
#                        "6666": "6666/udp",
#                        "127.0.0.1:7777": "7777",
#                        "9999": "9999/tcp",
#                        "23": "23",
#                    },
#                },
#            },
#        }

        config = utils.gen_config(app.get("name","default-app"))
        self.run_stack(config, app)

        #insert app to local db
        db.create_app(config["appname"], config["appname"], stack_id, app['region'])


    # Run stack
    def run_stack(self, config, app_dict):
        config["appname"] = utils.user_param(config, "Enter app name",config["appname"])
        config["dirs"] = {
            "containers": os.path.join(config["config_path"],"docker","containers"),
            "boot2docker": os.path.join(config["config_path"],"docker","boot2docker"),
        }
        for d in config["dirs"]:
            if not os.path.exists(config["dirs"][d]):
                os.makedirs(config["dirs"][d])
        if boot2docker.has():
            if not os.path.isfile(os.path.join(config["dirs"]["boot2docker"],"boot2docker.iso")):
                utils.download(config["boot2docker_iso"],os.path.join(config["dirs"]["boot2docker"],"boot2docker.iso"))

            if not boot2docker.gen_config(config, config["appname"]):
                utils.error("Unable to generate boot2docker configuration")
                return False
            boot2docker.delete(config, config["appname"])
            boot2docker.init(config, config["appname"])
            boot2docker.mount(config["appname"], [{
                "volume": "root",
                "hostpath": "/",
            },{
                "volume": "containers",
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
