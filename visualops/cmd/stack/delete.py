# Copyright 2014 MadeiraCloud LTD.

import logging

from cliff.command import Command


class Delete(Command):
    "Delete your stack, locally or on AWS"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('stack delete TO-DO!\n')

