import logging
# from .. import settings
# from .client import get_client

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
        self.app.stdout.write('stack pull TO-DO!\n')

        # username, session_id = load_session()
        # client   = rpc()

        # print 'pulling %s from visualops.io ....' % stack['id']
        # stack = client.stack_info()
        # with open(os.path.join(os.getcwd(), '/%s.yaml' % stack['id'])) as f:
        #     f.writelines(stack)
        # print '%s is cloned locally' % stack['id']
