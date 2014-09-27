'''
note: Local db operation wrapper
'''

import sqlite3
import os
import datetime
import base64
from visualops.utils import utils,constant


def init_db():
    try:
        if not os.path.isfile( constant.DB_FILE ):
            conn = sqlite3.connect( constant.DB_FILE )
            c = conn.cursor()
            c.execute("""Create  TABLE app(
                        id varchar(15)
                        ,name varchar(50)
                        ,source_id varchar(15)
                        ,region varchar(25)
                        ,state varchar(15)
                        ,create_at varchar(15)
                        ,change_at varchar(20)
                        ,app_data ntext
                        , Primary Key(id)
                        );""")
            c.execute("""Create  TABLE container(
                        id varchar(15)
                        ,name varchar(50)
                        ,app_id varchar(15)
                        , Primary Key(id)
                        );""")
            print "init db file %s succeed! " % constant.DB_FILE
            conn.close()
    except Exception,e:
        raise RuntimeError( 'init local db failed! %s' % e )

def reset_db():
    os.remove( constant.DB_FILE )
    init_db()

def get_conn():
    if not os.path.isfile( constant.DB_FILE ):
        init_db()

    conn = sqlite3.connect( constant.DB_FILE )
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
        c.execute("UPDATE app SET state='{0}',change_at='{1}' WHERE id='{2}'".format(state, create_at, app_id))
        conn.commit()
        conn.close()
        print 'UPDATE app %s state to %s succeed!' % (app_id,state)
    except Exception, e:
        raise RuntimeError( 'update app %s state to %s failed! %s' % (app_id,state,e) )



def create_app(app_id, app_name, source_id, region, app_data):
    """
    insert app record when stack run as a app
    """
    try:
        create_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_conn()
        c = conn.cursor()

        #check old app
        c.execute("SELECT count(*) FROM app WHERE name='{0}' ".format(app_name))
        old_app = c.fetchone()
        if old_app[0] > 0:
            print 'app name (%s) already existed, clear old app and container info ...' % app_name
            c.execute("DELETE FROM container WHERE app_id='{0}'".format(app_id))
            c.execute("DELETE FROM app WHERE name='{0}'".format(app_name))
            conn.commit()

        #insert new app
        c.execute("INSERT INTO app (id,name,source_id,region,state,create_at,change_at,app_data) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')"
            .format(app_id,app_name,source_id,region,'Running',create_at,create_at,app_data))
        conn.commit()
        conn.close()
        print 'create app %s succeed!' % app_id
    except Exception, e:
        raise RuntimeError('create app %s failed! %s' % (app_id,e))

def delete_app(app_id):
    """
    delete app from local db
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM container WHERE app_id='{0}'".format(app_id))
        c.execute("DELETE FROM app WHERE id='{0}'".format(app_id))
        conn.commit()
        print 'delete app %s succeed!' % app_id
    except Exception, e:
        raise RuntimeError('delete app %s failed! %s' % (app_id,e))    


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
        c.execute("SELECT name,source_id,region,state,create_at,change_at FROM app ")
        rlt = c.fetchall()
        conn.commit()
        conn.close()
        #print '[app_list]list app succeed!'
        return rlt
    except Exception,e:
        raise RuntimeError('list app failed! %s ' % e)


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
    except Exception,e :
        raise RuntimeError('create container %s failed! %s' % (app_id,e))

def get_app_info(app_id):
    """
    get app list( exclude app_data )
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT name,source_id,region,state,create_at,change_at FROM app WHERE id='{0}' ".format(app_id))
        app_info = c.fetchone()
        c.execute("SELECT id,name,app_id FROM container WHERE app_id='{0}' ".format(app_id))
        container_rlt = c.fetchall()
        conn.close()
        #print '[app_list]list app succeed!'
        return (app_info, container_rlt)
    except Exception,e:
        raise RuntimeError('list app failed! %s' % e)

def get_app_data(app_id):
    """
    get app data ( include name and app_data )
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id,name,app_data FROM app WHERE id='{0}' ".format(app_id))
        result = c.fetchone()
        conn.close()

        appname = result[1]
        app_data = utils.str2dict( base64.b64decode(result[2]) )

        return (appname,app_data)

    except Exception,e:
        raise RuntimeError('get app data failed! %s' % e)
