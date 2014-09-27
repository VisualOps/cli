import logging
import os
import yaml
import base64

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,rpc,constant,db


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
            print app

            config = utils.gen_config(app.get("name","default-app"))
            try:
                #insert app to local db
                self.clone_app(config, app)
                app["name"] = config["appname"]
                db.create_app(config["appname"], config["appname"], app_id, app['region'], base64.b64encode(utils.dict2str(app)) )
            except Exception,e:
                raise RuntimeError('Clone app to local failed! %s' % e)
                db.delete_app( config["appname"] )


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
