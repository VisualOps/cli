'''
note: AppService api wrapper
Copyright 2014 MadeiraCloud LTD.
'''

import requests
import json
import logging
from visualops.utils import constant


# Disable log message for request
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


def _call(url, method, params):
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    rlt = requests.post(
        '%s/%s/' % ( constant.API_URL , url),
        data    = json.dumps(payload),
        headers	= {'content-type': 'application/json'}
    )
    return rlt.json()["result"]


### session operation ###
def login(username, password):
	params = [username, password]
	return _call('session', 'login', params)

def logout(username, session_id):
    params = [username, session_id]
    return _call('session', 'logout', params)


### stack operation ###
def stack_list(username, session_id, region_name):
    params = [username, session_id, region_name]
    return _call('stack', 'list', params)

def stack_info(username, session_id, region_name, stack_ids):
    params = [username, session_id, region_name, stack_ids]
    return _call('stack', 'info', params)


### app operation ###
def app_list(username, session_id, region_name):
    params = [username, session_id, region_name]
    return _call('app', 'list', params)

def app_info(username, session_id, region_name, app_ids):
    params = [username, session_id, region_name, app_ids]
    return _call('app', 'info', params)
