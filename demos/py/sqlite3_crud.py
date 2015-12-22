import sqlite3
import os
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

#global var
DB_FILE_DEFAULT = "/home/your user name/proj2/test.db"
DB_FILE_PATH = '/home/your user name/proj2/db/test.db'
 
def get_conn(path):
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        return conn
    else:
        conn = None
        return sqlite3.connect(DB_FILE_DEFAULT)
 
def get_cursor(conn):
    if conn is not None:
        cur = conn.cursor()
    else:
        cur = get_conn(DB_FILE_PATH).cursor()
    conn.text_factory = str
    return cur

def close_all(conn, cu):
    try:
        if cu is not None:
            cu.close()
    finally:
        if conn is not None:
            conn.close()
        
def save(conn, sql, data):
    if sql is not None and sql != '':
        if data is not None:
            try:
                cu = get_cursor(conn)
                cu.execute(sql.encode('UTF-8'), data)
                conn.commit()
            except sqlite3.Error, e:
                if conn:
                    conn.rollback()
                return False
            finally:
                close_all(conn, cu)
            return True
    else:
        print('the [{}] is empty or equal None!'.format(sql))
    return False
        
def save_trans(conn, sql, data):
    if len(sql) != len(data):
        return False
    else:
        try:
            cu = get_cursor(conn)
            for e in range(len(sql)):
                if sql[e] is not None:
                    cu.execute(sql[e].encode('UTF-8'), data[e])
                else:
                    print('the [{}] is empty or equal None!'.format(sql[e]))
                    return False
            conn.commit()
            return True
        except sqlite3.Error, e:
            if conn:
                conn.rollback()
            return False
        finally:
            close_all(conn, cu)
        return False

def fetchall(conn, sql):
    if sql is not None and sql != '':
        cu = get_cursor(conn)
        cu.execute(sql.encode('UTF-8'))
        result = cu.fetchall()
        close_all(conn, cu)
        return result
    else:
        return None
 
def fetch(conn, sql, data):
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            cu.execute(sql.encode('UTF-8'), data)
            result = cu.fetchall()
            close_all(conn, cu)
            return result
        else:
            return None
    else:
        return None
 
def delete(conn, sql, data):
    if sql is not None and sql != '':
        if data is not None:
            try:
                cu = get_cursor(conn)
                for d in data:
                    cu.execute(sql.encode('UTF-8'), d)
                conn.commit()
                return True
            except lite3.Error, e:
                if conn:
                    conn.rollback()
                return False
            finally:
                close_all(conn, cu)
    else:
        #print('the [{}] is empty or equal None!'.format(sql))
        return False
