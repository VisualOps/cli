# Copyright 2014 MadeiraCloud LTD.

import logging
from visualops.utils import rpc
from visualops.utils import utils
from visualops.utils import constant
from cliff.show import ShowOne


class Info(ShowOne):
    "Show summary information for specified stack"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Info, self).get_parser(prog_name)
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()

        # get stack info
        stack_id = parsed_args.stack_id
        (err, result) = rpc.stack_info(username, session_id, None, [ stack_id ])

        if err:
            print('Get stack info failed')
            utils.hanlde_error(err,result)
        else:
            self.log.debug('> get {0} stack(s) info'.format(len(result)))

            if len(result) == 0:
                return (),()

            stack_json = result[0]

            del stack_json['layout']
            del stack_json['property']

            instance_with_state    = 0
            instance_without_state = 0
            for (uid,comp) in stack_json['component'].items():
                if unicode(comp['type']) == constant.RESTYPE['INSTANCE']:

                    log_str = '> found instance {0}'.format(comp['name'])

                    if comp['state']:
                        log_str+=': has %s state(s)' % len(comp['state'])
                        instance_with_state+=1
                    else:
                        log_str+=': has no state'
                        instance_without_state+=1

                    self.log.debug(log_str)

            print "Stacks Info:"
            columns = ( 'Id',
                        'Name',
                        'Region',
                        'Version',
                        'Module Tag',
                        'Component',
                        'Instance Total',
                        'Instance With State',
                        'Instance Without State',
                       )
            data = (
                    result[0]['id'],
                    result[0]['name'],
                    result[0]['region'],
                    result[0]['version'],
                    result[0]['agent']['module']['tag'],
                    len(result[0]['component']),
                    instance_with_state+instance_without_state,
                    instance_with_state,
                    instance_without_state,
                    )
            return (columns, data)
