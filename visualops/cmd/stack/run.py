import logging
import os
import yaml
import json
from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils


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

        config = {
            "interactive": True,
            "config_path": os.path.expanduser("~/.visualops"),
            "boot2docker_iso": "https://s3.amazonaws.com/visualops-cli/boot2docker.iso",
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
        }

        self.run_app(config, app)


    # Run app
    def run_app(self, config, app_dict):
#        import pdb
#        pdb.set_trace()
        appname = utils.user_param(config, "Enter app name",app_dict.get("name","default-app"))
        config["dirs"] = {
            "containers": os.path.join(config["config_path"],"docker","containers"),
            "boot2docker": os.path.join(config["config_path"],"docker","boot2docker"),
        }
        for d in config.get("dirs",[]):
            if not os.path.exists(d):
                os.makedirs(d)
        if boot2docker.has():
            if not os.path.isfile(os.path.join(config["dirs"]["boot2docker"],"boot2docker.iso")):
                utils.download(config["boot2docker_iso"])

            if not boot2docker.gen_config(config, appname):
                utils.error("Unable to generate boot2docker configuration")
                return False
            boot2docker.delete(config, appname)
            boot2docker.mount(appname, [{
                "volume": "root",
                "hostpath": "/",
            },{
                "volume": "containers",
                "hostpath": config["dirs"]["containers"],
            }])
            boot2docker.run(config, appname)
            config["chroot"] = os.path.join("/mnt/host",config.get("chroot"))
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        app = {}
        config["hosts_table"] = app_dict.get("hosts_table",{})
        for hostname in app_dict.get("hosts",{}):
            for state in app_dict["hosts"][hostname]:
                if state == "linux.docker.deploy":
                    for container in app_dict["hosts"][hostname][state]:
                        app.update(dockervisops.deploy(config, appname, hostname, app_dict["hosts"][hostname][state][container]))
        dockervisops.generate_hosts(config, app)
