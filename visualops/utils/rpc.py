import requests
import json

ide = "https://ide.visualops.io"
headers = {'content-type': 'application/json'}

def _call(url, method, params):
    payload = {
        "method": method,
        "params": params
        "jsonrpc": "2.0",
        "id": 0,
    }
    return requests.post(
        '%s/%s' % (ide, url), 
        data	= json.dumps(payload), 
        headers	= headers
    ).json()

def login(username, password):
	params = [username, password]
	return _call('session', 'login', params)

def logout(username, session_id):
	params = [username, session_id]
	return _call('session', 'logout', params)

def pull(username, session_id, stack_id):
	params = [username, session_id, None, [stack_id]]
	return _call('stack', 'info', params)

def push(username, session_id, stack_id):
	params = [username, session_id, None, [stack_id]]
	return _call('stack', 'save', params)