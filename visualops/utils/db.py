import sqlite3
import uuid
import os


def get_conn():
    db_file = os.path.expanduser("~/.visualops/db")
    if not os.path.isfile( db_file ):
        conn = sqlite3.connect( db_file )
        c = conn.cursor()
        c.execute("""Create  TABLE app(
                    id varchar(15)
                    ,name varchar(50)
                    ,stack_id varchar(15)
                    ,region varchar(25)
                    ,state varchar(15)
                    ,position varchar(10)
                    , Primary Key(id)   
                    );""")
        print "init db file %s succeed! " % db_file
    else:
        conn = sqlite3.connect( db_file )
    return conn

def app_update_state(app_id,state):
    """
    update app state
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE app SET state='{0}' where id='{1}'".format(state, app_id))
        conn.commit()
        conn.close()
        print '[app_stop]update app state to %s succeed!' % state
    except Exception:
        raise RuntimeError( '[app_stop]update app state to %s succeed!' % state )



def create_app(app_name, stack_id, region):
    """
    insert app record when stack run as a app
    """
    try:
        app_id = 'app-%s' % str(uuid.uuid4())[:8]
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO app (id,name,stack_id,region,state,position) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')".format(app_id,app_name,stack_id,region,'Running','local'))
        conn.commit()
        conn.close()
        print '[app_create]insert app succeed!'
    except Exception:
        raise RuntimeError('[app_create]insert app failed!')

def get_app_list():
    """
    get app list
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("select id,name,stack_id,region,state,position from app ")
        rlt = c.fetchall()
        conn.commit()
        conn.close()
        #print '[app_list]list app succeed!'
        return rlt
    except Exception:
        raise RuntimeError('[app_list]list app failed!')        

    
def stop_app(app_id):
    """
    update app state to 'Stopped'
    """
    app_update_state(app_id, 'Stopped')


def start_app(app_id):
    """
    update app state to 'Running'
    """
    app_update_state(app_id, 'Running')


def terminate_app(app_id):
    """
    update app state to 'Terminated'
    """
    app_update_state(app_id, 'Terminated')

