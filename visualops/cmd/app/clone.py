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

    # Clone app
    def clone_app(self, config, app_dict):
        appname = utils.user_param(config, "Enter app name",app_dict.get("name","default-app"))
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

            if not boot2docker.gen_config(config, appname):
                utils.error("Unable to generate boot2docker configuration")
                return False
            boot2docker.delete(config, appname)
            boot2docker.init(config, appname)
            boot2docker.mount(appname, [{
                "volume": "root",
                "hostpath": "/",
            },{
                "volume": "containers",
                "hostpath": config["dirs"]["containers"],
            }])
            boot2docker.run(config, appname)
            config["chroot"] = os.path.join("/mnt/host",config.get("chroot",""))
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        app = {}
        config["hosts_table"] = app_dict.get("hosts_table",{})
        config["render_table"] = utils.render_table(app_dict.get("hosts_table",{}))
        for hostname in app_dict.get("hosts",{}):
            for state in app_dict["hosts"][hostname]:
                if state == "linux.docker.deploy":
                    for container in app_dict["hosts"][hostname][state]:
                        app.update(dockervisops.deploy(config, appname, hostname, app_dict["hosts"][hostname][state][container]))
        dockervisops.generate_hosts(config, app)
