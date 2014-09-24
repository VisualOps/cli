import logging
import os
from visualops.utils import rpc
from visualops.utils import utils
from visualops.utils import Constant

from cliff.command import Command


class Pull(Command):
    "Pull a stack from VisualOps to local"
    #download stack to local

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Pull, self).get_parser(prog_name)
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()

        print 'pulling %s from visualops.io ....' % parsed_args.stack_id
        # get stack info
        (err, result) = rpc.stack_info(username, session_id, None, [parsed_args.stack_id])

        if err:
            if err == Constant.E_SESSION:
                raise RuntimeError('Your Session is invalid, please re-login!')
            else:
                raise RuntimeError('pull stack failed:( ({0})'.format(err))
        else:
            if len(result) == 0:
                self.app.stdout.write('The stack is not existed\n')
                return (),()

            self.app.stdout.write('pull stack succeed\n')

            stack_json = result[0]
            del stack_json['layout']
            del stack_json['property']

            #generate yaml
            app = {}
            for (uid,comp) in stack_json['component'].items():
                if unicode(comp['type']) == Constant.RESTYPE['INSTANCE']:
                    self.app.stdout.write('found instance {0}'.format(comp['name']))
                    if comp['state']:
                        print ': has %s state(s)' % len(comp['state'])
                        hostname = comp['name']
                        container = {}
                        for (idx,state) in enumerate(comp['state']):
                            state_type = state['module']
                            if state_type == 'linux.docker.deploy':
                                container_name = state['parameter']['container']
                                if not container.has_key(state_type):
                                    container[state_type] = {}
                                container[state_type][container_name] = state['parameter']
                        app[hostname] = container
                    else:
                        print ': has no state'

            stack_yaml = utils.dict2yaml(app)
            stack_file = os.path.join(os.getcwd(), '%s.yaml' % parsed_args.stack_id)
            with open(stack_file,'w+') as f:
                f.writelines( stack_yaml )
            print "=============================================================="
            print stack_yaml
            print "=============================================================="
            print '%s is pulled to local %s' % (parsed_args.stack_id, stack_file)
