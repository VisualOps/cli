import logging
import os
import yaml
import json
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

        if parsed_args.run_stack_local:
            print 'running %s to local ....' % parsed_args.stack_id
        else:
            print 'running %s to visualops.io (not support yet, please try -l)....' % parsed_args.stack_id
            return

        stack_file = os.path.join(os.getcwd(), '%s.yaml' % parsed_args.stack_id)
        if not os.path.isfile(stack_file):
            print( '%s is not exist, please pull stack first!' % stack_file )
            return
        try:
            print "Load data from %s" % stack_file
            stream = open(stack_file, 'r')
            app = yaml.load(stream)
        except Exception:
            raise RuntimeError('Load yaml error!')

        if not app:
            raise RuntimeError('stack json is invalid!')

        print "=============================================================="
        print json.dumps(app, indent=4)
        print "=============================================================="

