# Copyright 2014 MadeiraCloud LTD.

import logging
from visualops.utils import db
from cliff.command import Command

class Reset(Command):
    "Reset local db"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):

        while True:
            confirm = raw_input('Are you sure to reset the local db? [Y/n]:')
            if not confirm or confirm.lower() in ['y','n']:
                break

        if not confirm or confirm.lower() == 'y':
            db.reset_db()
