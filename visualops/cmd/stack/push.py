# Copyright 2014 MadeiraCloud LTD.

import logging
# from .. import settings
# from .client import get_client

from cliff.command import Command


class Push(Command):
    "Push a stack to VisualOps"
    #save stack to remote

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Push, self).get_parser(prog_name)
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('stack push TO-DO!\n')

        # username, session_id = load_session()
        # client   = rpc()

        # print 'pushing %s to visualops.io ....' % stack['id']
        # with open(os.path.join(os.getcwd(), '/%s.yaml' % stack['id'])) as f:
        #     stack = f.readlines()
        # stack = client.stack_save(username, session_id, stack)
        # print '%s is pushed to remote' % stack['id']
