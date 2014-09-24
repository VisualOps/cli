import logging

from cliff.command import Command


class Stop(Command):
    "stop an Running app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Stop, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('app stop TO-DO!\n')
