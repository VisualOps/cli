import logging
import os

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils


class Clone(Command):
    "Clone a remote app to local"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Clone, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('app clone TO-DO!\n')

        app = {}# TODO (jimmy): get app details

        config = utils.gen_config(app.get("name","default-app"))
        self.clone_app(config, app)

        # TODO (jimmy): store db

    # Clone app
    def clone_app(self, config, app_dict):
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
            boot2docker.run(config, config["appname"])
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
                app.update(config, actions[hostname][container])
        dockervisops.generate_hosts(config, app)
