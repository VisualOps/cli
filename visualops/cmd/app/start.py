import logging

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,db


class Start(Command):
    "Start an stopped app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Start, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='start_app_local', help='start local app')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('app start TO-DO!\n')

        app_id = parsed_args.app_id
        appname = ""# TODO jimmy
        app = {}#TODO jimmy

        config = utils.gen_config(appname)

        if parsed_args.start_app_local:
            self.start_app(config, appname, app)
            print 'start local app ...'
        else:
            print 'start remote app ...(not support yet)'
            return

        #save app state
        db.start_app(appname)


    # Start app
    def start_app(self, config, appname, app_dict):
        if boot2docker.has():
            boot2docker.run(config, appname)
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        for hostname in app_dict.get("hosts",{}):
            for state in app_dict["hosts"][hostname]:
                if state == "linux.docker.deploy":
                    for container in app_dict["hosts"][hostname][state]:
                        if dockervisops.start(config, container):
                            print "Container %s started"%container
                        else:
                            utils.error("Unable to start container %s"%container)
        print "app %s started."%appname
