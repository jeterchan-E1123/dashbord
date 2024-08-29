import psycopg2
from config import load_config

config = load_config()

def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            # print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def fetch_records(query:str,params: tuple = ()):
    conn = connect()
    if conn is None:
        return []
    
    records = []
    try:
        with conn.cursor() as cur:
            cur.execute(query,params)
            records = cur.fetchall()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
    finally:
        conn.close()
    
    return records

def get_timesheet():
    query = 'SELECT project_id, task_id, user_id, dept_no, record_date, work_hours, description FROM huntergame.ts_record WHERE dept_no IN (\'88A14111BF\',\'88A14112BF\',\'88A14121BF\')'
    return fetch_records(query)

def get_dept_names():
    query = 'SELECT dept_no, dept_name_en FROM ma_or_department'
    return fetch_records(query)
    
def get_proj_names():
    query = 'SELECT proj_id, proj_name_cn, proj_type FROM huntergame.proj_info'
    return fetch_records(query)

def get_task_names():
    query = 'SELECT id, proj_tk_name FROM huntergame.proj_tk'
    return fetch_records(query)

def get_unique_user():
    query = 'SELECT DISTINCT user_id FROM huntergame.ts_record WHERE dept_no IN (\'88A14111BF\',\'88A14112BF\',\'88A14121BF\')'
    return fetch_records(query)


if __name__ == '__main__':
    # config = load_config()
    # connect(config)
    # connect()
    print((get_dept_names()))
    print(type(get_timesheet()))