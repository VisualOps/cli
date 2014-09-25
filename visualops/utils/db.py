import sqlite3
import os
import datetime

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
                    ,create_at varchar(15)
                    ,change_at varchar(20)
                    ,position varchar(10)
                    , Primary Key(id)   
                    );""")
        c.execute("""Create  TABLE container(
                    id varchar(15)
                    ,name varchar(50)
                    ,app_id varchar(15)
                    , Primary Key(id)
                    );""")
        print "init db file %s succeed! " % db_file
    else:
        conn = sqlite3.connect( db_file )
    return conn



#########################################
# app table
#########################################

def app_update_state(app_id,state):
    """
    update app state
    """
    try:
        create_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_conn()
        c = conn.cursor()
        c.execute("UPDATE app SET state='{0}',change_at='{1}' where id='{2}'".format(state, create_at, app_id))
        conn.commit()
        conn.close()
        print 'update app %s state to %s succeed!' % (app_id,state)
    except Exception:
        raise RuntimeError( 'update app %s state to %s succeed!' % (app_id,state) )



def create_app(app_id, app_name, stack_id, region):
    """
    insert app record when stack run as a app
    """
    try:
        create_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO app (id,name,stack_id,region,state,create_at,change_at,position) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')"
            .format(app_id,app_name,stack_id,region,'Running',create_at,create_at,'local'))
        conn.commit()
        conn.close()
        print 'create app %s succeed!' % app_id
    except Exception:
        raise RuntimeError('create app %s failed!' % app_id)


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


def get_app_list():
    """
    get app list
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("select id,name,stack_id,region,state,create_at,change_at,position from app ")
        rlt = c.fetchall()
        conn.commit()
        conn.close()
        #print '[app_list]list app succeed!'
        return rlt
    except Exception:
        raise RuntimeError('list app failed!')


#########################################
# container table
#########################################

def create_container(app_id,container_id,container_name):
    """
    insert container record when create container
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO container (id,name,app_id) VALUES ('{0}','{1}','{2}')"
            .format(container_id,container_name,app_id))
        conn.commit()
        conn.close()
        print 'create container %s succeed!' % app_id
    except Exception:
        raise RuntimeError('create container %s failed!' % app_id)

def get_app_info(app_id):
    """
    get app list
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("select id,name,stack_id,region,state,create_at,change_at,position from app where id='{0}' ".format(app_id))
        app_rlt = c.fetchall()
        c.execute("select id,name,app_id from container where app_id='{0}' ".format(app_id))
        container_rlt = c.fetchall()
        conn.close()
        #print '[app_list]list app succeed!'
        return (app_rlt, container_rlt)
    except Exception:
        raise RuntimeError('list app failed!')
