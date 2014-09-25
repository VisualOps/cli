import logging

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils


class Reboot(Command):
    "Reboot app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Reboot, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('app reboot TO-DO!\n')

    # Reboot app
    def reboot_app(self, config, appname, app_dict):
        if boot2docker.has():
            boot2docker.run(config, appname)
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        for hostname in app_dict.get("hosts",{}):
            for state in app_dict["hosts"][hostname]:
                if state == "linux.docker.deploy":
                    for container in app_dict["hosts"][hostname][state]:
                        if dockervisops.restart(config, container) is True:
                            print "Container %s restarted"%container
                        else:
                            utils.error("Unable to restart container %s"%container)
        print "app %s restarted."%appname
