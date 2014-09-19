import requests
import json

ide = "http://api.mc3.io"
headers = {'content-type': 'application/json'}

def _call(url, method, params):
    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    rlt = requests.post(
        '%s/%s/' % (ide, url),
        data    = json.dumps(payload),
        headers	= headers
    )
    return rlt.json()["result"]

def login(username, password):
	params = [username, password]
	return _call('session', 'login', params)

def stack_list(username, session_id, region_name):
    params = [username, session_id, region_name]
    return _call('stack', 'list', params)

def stack_info(username, session_id, region_name, stack_ids):
    params = [username, session_id, region_name, stack_ids]
    return _call('stack', 'info', params)
