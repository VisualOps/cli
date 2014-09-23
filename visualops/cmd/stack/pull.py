import logging
import os
from visualops.utils import rpc
from visualops.utils import utils
from visualops.utils import constant
import json

from cliff.command import Command


class Pull(Command):
    "Pull a stack from VisualOps to local"
    #download stack to local

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Pull, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()

        print 'pulling %s from visualops.io ....' % parsed_args.stack_id
        # get stack info
        (err, result) = rpc.stack_info(username, session_id, parsed_args.region_name, [parsed_args.stack_id])

        if err:
            if err == constant.E_SESSION:
                raise RuntimeError('Your Session is invalid, please re-login!')
            else:
                raise RuntimeError('pull stack failed:( ({0})'.format(err))
        else:
            if len(result) == 0:
                self.app.stdout.write('The stack is not existed\n')
                return (),()

            self.app.stdout.write('pull stack succeed\n')

            stack_file = os.path.join(os.getcwd(), '%s.json' % parsed_args.stack_id)
            stack_json = result[0]

            del stack_json['layout']
            del stack_json['property']

            # import pudb
            # pudb.set_trace()
            for (uid,comp) in stack_json['component'].items():
                if unicode(comp['type']) == constant.RESTYPE['INSTANCE']:
                    print "found instance %s" % comp['name']
                    if comp['state']:
                        print "found state of instance %s" % comp['name']
                        print json.dumps( comp['state'],indent = 4)
                    else:
                        print "not found state of instance %s" % comp['name']


            with open(stack_file,'w+') as f:
                f.writelines(json.dumps(stack_json,indent = 4))
            print '%s is pulled to local %s' % (parsed_args.stack_id, stack_file)
