import logging
import os
from visualops.utils import rpc
from visualops.utils import utils
from visualops.utils import constant

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

        stack_id = parsed_args.stack_id        

        print 'pulling %s from remote ....\n' % stack_id
        (err, result) = rpc.stack_info(username, session_id, None, [stack_id])

        if err:
            if err == constant.E_SESSION:
                raise RuntimeError('Your Session is invalid, please re-login!')
            else:
                raise RuntimeError('pull stack failed:( ({0})'.format(err))
        else:
            if len(result) == 0:
                self.app.stdout.write('The stack is not existed\n')
                return (),()

            self.log.debug('> pull stack %s succeed\n' %  stack_id )

            stack_json = result[0]
            del stack_json['layout']
            del stack_json['property']

            #generate yaml
            app = {
                'name'  : stack_json['name'],
                'hosts' : {},
                'hosts_table' : {},
            }
            for (uid,comp) in stack_json['component'].items():
                if unicode(comp['type']) == constant.RESTYPE['INSTANCE']:

                    app['hosts_table'][uid] = comp['name']

                    log_str = '>Found instance {0}'.format(comp['name'])
                    
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

            stack_yaml = utils.dict2yaml(app)
            stack_file = os.path.join(os.getcwd(), '%s.yaml' % stack_id)
            with open(stack_file,'w+') as f:
                f.writelines( stack_yaml )

            self.log.debug( '\nDocker state info' )
            self.log.debug( '==============================================================' )
            self.log.debug( stack_yaml )
            self.log.debug( '==============================================================' )
            self.log.debug( '> %s is saved to %s\n' % (stack_id, stack_file) )

            print 'Done!'
