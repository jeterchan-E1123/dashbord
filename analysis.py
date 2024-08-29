from connect import fetch_records, get_task_names
# import streamlit as st


def region():
    # 選 region 顯示該 region 的所有 department
    query = """
        SELECT regions_name, regions_acc_code
        FROM ma_or_regions
    """
    return fetch_records(query)

def dept(region_no):

    query = """
        SELECT dept_no, dept_name_en
        FROM ma_or_department
        WHERE dept_no LIKE %s
    """

    params = (region_no +'%',)
    return fetch_records(query,params)
    # return array
def fetch_all_dept():
    query = """
        SELECT DISTINCT dept_name_en
        FROM ma_or_department
    """

    return fetch_records(query)

def fetch_project_task_employee():
    query = """
        SELECT huntergame.proj_info.job_code
        FROM huntergame.proj_info
        INNER JOIN huntergame.proj_tk
        ON huntergame.proj_tk.proj_id = huntergame.proj_info.proj_id
    """

    return fetch_records(query)

def fetch_end_date():
    # get task esti end date is today
    query = 'SELECT * FROM huntergame.proj_tk WHERE actual_end_date is NOT NULL'

    return fetch_records(query)

def get_description():
    # 選定部門 + 員工 -> with description
    query = '''
        SELECT proj_name_cn FROM huntergame.proj_info
        JOIN huntergame.ts_record  ON huntergame.proj_info.proj_id = huntergame.ts_record.project_id  
    '''

    return fetch_records(query)

def main():
    
    arr_des = get_description()
    print(arr_des)


if __name__ == '__main__':
    main()
