import logging

from cliff.command import Command


class Push(Command):
    "Push a stack to VisualOps"
    #save stack to remote

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Push, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('stack push TO-DO!\n')
