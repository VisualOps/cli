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
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        (username, session_id)   = utils.load_session()
        if not(username and session_id):
            return (),()

        # get stack info
        (err, result) = rpc.stack_info(username, session_id, parsed_args.region_name, [parsed_args.stack_id])

        if err:
            if err == constant.E_SESSION:
                raise RuntimeError('Your Session is invalid, please re-login!')
            else:
                raise RuntimeError('get stack info failed:( ({0})'.format(err))
        else:
            self.app.stdout.write('get {0} stack(s) info\n'.format(len(result)))

            if len(result) == 0:
                return (),()

            columns = ( 'Id',
                        'Name',
                        'CloudType',
                        'Provider',
                        'Component',
                       )
            data = (
                    result[0]["id"],
                    result[0]["name"],
                    result[0]["cloud_type"],
                    result[0]["provider"],
                    len(result[0]["component"]),
                    )
            return (columns, data)
