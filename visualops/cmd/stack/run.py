import logging

from cliff.command import Command


class Run(Command):
    "Deploy the stack locally, or in the cloud"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('stack run TO-DO!\n')

        # username, session_id = load_session()
        # client   = rpc()

        # print 'running %s to visualops.io ....' % stack['id']
        # with open(os.path.join(os.getcwd(), '/%s.yaml' % stack['id'])) as f:
        #   stack = f.readlines()
        # stack = client.stack_save(username, session_id, stack)
        # print '%s is pushed to remote' % stack['id']
