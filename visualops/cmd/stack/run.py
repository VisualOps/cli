import logging
import os
import json
from visualops.utils import Global
from visualops.utils import Constant
from cliff.command import Command


class Run(Command):
    "Deploy the stack locally, or in the cloud"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='run_stack_local', help='deploy the stack locally')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('stack run TO-DO!\n')

        if parsed_args.run_stack_local:
            print 'running %s to local ....' % parsed_args.stack_id
        else:
            print 'running %s to visualops.io (not support yet)....' % parsed_args.stack_id
            return

        try:
            stack_file = os.path.join(os.getcwd(), '%s.json' % parsed_args.stack_id)
            f = file(stack_file);
            stack_json = json.load(f)
        except Exception:
            raise RuntimeError('Load json error!')

        if not stack_json:
            raise RuntimeError('stack json is invalid!')
        
        #generate Global.app
        for (uid,comp) in stack_json['component'].items():
            if unicode(comp['type']) == Constant.RESTYPE['INSTANCE']:
                self.app.stdout.write('found instance {0}\n'.format(comp['name']))
                if comp['state']:
                    hostname = comp['name']
                    container = {}
                    for (idx,state) in enumerate(comp['state']):
                        if state['module'] == 'linux.docker.deploy':
                            container_name = state['parameter']['container']
                            container[container_name] = state['parameter']
                    Global.app[hostname] = container
        print "===================================="
        print json.dumps(Global.app,indent=4)


