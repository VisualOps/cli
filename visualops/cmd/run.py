import os
import sys

def run(args):
    username, session_id = load_session()
    client   = rpc()

    print 'pushing %s to visualops.io ....' % stack['id']
    with open(os.path.join(os.getcwd(), '/%s.yaml' % stack['id'])) as f:
        stack = f.readlines()
    stack = client.stack_save(username, session_id, stack)
    print '%s is pushed to remote' % stack['id']