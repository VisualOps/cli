# Copyright 2014 MadeiraCloud LTD.

import logging
import copy


class ResultException(Exception):
        """A simple exception class used for Result exceptions"""
        pass

class Result(Exception):

    ## return code
    # common:   1*
    # stack:    2*
    # app:      3*

    ## usage
    # step 1 : 
    #   from visualops.utils.Result import Result
    # step 2 : 
    #   raise Result("ERR.STACK.RUN_FAILED", stack_id)
    # step 3:
    #   except Result,e:
    #       print '!!!Expected error occur %s' % str(e.format())


    _result = {
        'COMMON' : {
            'UNKNOWN' : {
                'code' : 100,
                'msg' : 'unknown error'
            }
        },
        'STACK' : {
            'RUN_FAILED' : {
                'code' : 200,
                'msg' : 'Stack {0} run failed!'
            }
        },
        'APP' : {
            'STOP_FAILED' : {
                'code' : 300,
                'msg' : 'App {0} stop failed!'
            },
            'START_FAILED' : {
                'code' : 310,
                'msg' : 'App {0} start failed!'
            },
            'RESTART_FAILED' : {
                'code' : 320,
                'msg' : 'App {0} restart failed!'
            },
            'TERMINATE_FAILED' : {
                'code' : 330,
                'msg' : 'App {0} terminate failed!'
            },
            'CLONE_FAILED' : {
                'code' : 340,
                'msg' : 'App {0} clone failed!'
            },
            
        }
    }

    def __init__(self, flag, *args):
        self.flag = flag
        self.args = args

    def format(self):
        try:

            # check flag
            flag = str(self.flag)
            if not flag or not flag.startswith('ERR.'):
                logging.error("Result.format(): Invalid result flag {0}".format(flag))
                raise ResultException("Invalid result flag")

            code_list = flag.split('.')
            if len(code_list) < 3:
                logging.error("Result.format(): Invalid result flag {0}".format(flag))
                raise ResultException("Invalid result flag format")

            # get return code
            code_list = code_list[1:]
            try:
                result = copy.deepcopy(self._result)

                for i in range(len(code_list)):
                    result = result[code_list[i]]
            except Exception, e:
                logging.error("Result.format(): Get flag {0} result exception {1}".format(flag, str(e)))
                raise ResultException("Invalid result flag")

            if not result or 'code' not in result or 'msg' not in result:
                logging.error("Result.format(): Not supported flag {0}".format(flag))
                raise ResultException("Not supported result flag")

            if self.args:
                if not result['msg']:
                    result['msg'] = self.args[0]
                else:
                    for i in range(len(self.args)):
                        result['msg'] = result['msg'].replace('{'+str(i)+'}', str(self.args[i]))

            return (result['code'], result['msg'])
        except Exception, e:
            logging.error("Result.format(): {0} - {1} - {2}".format(self.flag, str(self.args), str(e)))
            result = self._result['COMMON']['ERROR']
            return (result['code'], result['msg'])
