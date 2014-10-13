'''
note: Local db operation wrapper
Copyright 2014 MadeiraCloud LTD.
'''

import sqlite3
import os
import datetime
import base64
import logging
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
            .format(app_id, app_name, source_id, region, constant.STATE_APP_RUNNING, create_at, create_at, app_data))
        conn.commit()
        conn.close()
        print 'create app %s succeed!' % app_id
    except Exception, e:
        raise RuntimeError('create app %s failed! %s' % (app_id,e))

def delete_app_info(app_id):
    """
    delete app info from local db
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM container WHERE app_id='{0}'".format(app_id))
        c.execute("DELETE FROM app WHERE id='{0}'".format(app_id))
        conn.commit()
        print 'clear old app %s in db succeed!' % app_id
    except Exception, e:
        raise RuntimeError('clear old app %s in db failed! %s' % (app_id,e))


def stop_app(app_id, is_finished=False):
    """
    update app state to 'Stopped'
    """
    state = constant.STATE_APP_STOPPED if is_finished else constant.STATE_APP_STOPPING
    app_update_state(app_id, state)


def start_app(app_id, is_finished=False):
    """
    update app state to 'Running'
    """
    state = constant.STATE_APP_RUNNING if is_finished else constant.STATE_APP_STARTING
    app_update_state(app_id, state)


def reboot_app(app_id, is_finished=False):
    """
    update app state to 'Running'
    """
    state = constant.STATE_APP_RUNNING if is_finished else constant.STATE_APP_REBOOTING
    app_update_state(app_id, state)


def terminate_app(app_id, is_finished=False):
    """
    update app state to 'Terminated'
    """
    state = constant.STATE_APP_TERMINATED if is_finished else constant.STATE_APP_TERMINATING
    app_update_state(app_id, state)
    if is_finished:
        delete_app_info(app_id)


def get_app_list(region_name=None,filter_name=None):
    """
    get local app list
    """
    try:
        conn = get_conn()
        c = conn.cursor()

        cond = []
        where_clause = ""
        if region_name:
            cond.append( "region='{0}' ".format(region_name) )
        if filter_name:
            cond.append( "lower(name) like '%{0}%' ".format(filter_name.lower()) )
        if len(cond) > 0:
            where_clause = 'and ' + 'and '.join( cond )

        sqlcmd = "SELECT name,source_id,region,state,create_at,change_at FROM app where state<>'Terminated' %s " % where_clause
        log = logging.getLogger(__name__)
        log.debug('> sql : %s' % sqlcmd)

        c.execute(sqlcmd)
        rlt = c.fetchall()
        conn.commit()
        conn.close()

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
    get app info( exclude app_data )
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT name,source_id,region,state,create_at,change_at FROM app WHERE id='{0}' ".format(app_id))
        app_info = c.fetchone()
        c.execute("SELECT app_data FROM app WHERE id='{0}' ".format(app_id))
        app_data = c.fetchone()
        c.execute("SELECT id,name,app_id FROM container WHERE app_id='{0}' ".format(app_id))
        container_rlt = c.fetchall()
        conn.close()
        return (app_info, app_data, container_rlt)
    except Exception,e:
        raise RuntimeError('get app info failed! %s' % e)

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

        if result:
            appname = result[1]
            app_data = utils.str2dict( base64.b64decode(result[2]) )

            return (appname,app_data)
        else:
            return (None,None)

    except Exception,e:
        raise RuntimeError('get app data failed! %s' % e)

def get_app_state(app_id):
    """
    get app state
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT state FROM app WHERE id='{0}' ".format(app_id))
        result = c.fetchone()
        conn.close()

        if result:
            state = result[0]
            return state
        else:
            return None

    except Exception,e:
        raise RuntimeError('get app state failed! %s' % e)
