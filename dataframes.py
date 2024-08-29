import pandas as pd
import numpy as np

from api_calls import get_ts_dept, get_ts_employee, get_children_dept

def create_df_task(df):
    df_task = df[['project_name', 'project_type', 'task_name', 'user_id', 'work_hours', 'description']]
    temp = df_task.groupby(by=['project_name', 'project_type', 'task_name', 'user_id'], as_index=False)
    df_task = temp[['work_hours']].sum()
    df_task.sort_values(by=['project_name', 'task_name'])
    
    return df_task
    
def create_df_ratio(df):
    '''
    Dataframe containing total work hours and ratio of each Project Type.
    '''
    
    df_type = df.groupby(by=['user_id', 'project_type'], as_index=False)
    df_type_hours = df_type[['work_hours']].sum()
    
    df_total_hours = df_type_hours.groupby(by=['user_id'], as_index=False).agg({'work_hours' : 'sum'})
    df_total_hours.rename(columns={'work_hours' : 'total_hours'}, inplace=True)
    
    df_ratio = pd.merge(df_type_hours, df_total_hours, on='user_id', how='left')
    df_ratio['ratio'] = df_ratio.work_hours / df_ratio.total_hours
    
    df_ratio.insert(loc=0, column='dept_name', value=df.dept_name)
    
    return df_ratio
    
def create_df_ratio_dept(df_ratio):
    temp = df_ratio.groupby(by=['project_type'], as_index=False)
    df_ratio_dept = temp[['work_hours']].sum()
    df_ratio_dept['total_hours'] = df_ratio_dept.work_hours.sum()
    df_ratio_dept['ratio'] = df_ratio_dept.work_hours / df_ratio_dept.total_hours

    return df_ratio_dept
    
def create_df_project(df):
    df_proj = df[['project_name', 'project_type', 'work_hours']]
    temp = df_proj.groupby(by=['project_name', 'project_type'], as_index=False)
    df_proj = temp[['work_hours']].sum()
    df_proj.sort_values(by='project_name')
    
    return df_proj

def create_df_daily_hours(df):
    # <8 Working Hours
    df_employee = df.groupby(by=['user_id', 'record_date'], as_index=False)
    df_daily_hours = df_employee[['work_hours']].sum()

    df_daily_hours['under_8'] = np.where(df_daily_hours['work_hours'] < 8, 1, 0)
    df_daily_hours.insert(loc=0, column='dept_name', value=df.dept_name)

    return df_daily_hours

def create_df_tasksum(df, task_name):
    df = df.loc[df.task_name == task_name]

    df_tasksum = df.loc[df.description != '']
    df_tasksum = df_tasksum[['task_name', 'record_date', 'work_hours', 'description']]
    df_tasksum.sort_values(by='record_date', inplace=True)
    return df_tasksum

def get_df_dept(dept_no, start_date, end_date):
    ts = get_ts_dept(dept_no, start_date, end_date)
    
    if ts is None:
        return None
    
    df = pd.DataFrame(ts.json())
    df.rename(columns={
        0: 'dept_no',
        1: 'dept_name',
        2: 'dept_type',
        3: 'project_id',
        4: 'project_name',
        5: 'project_type',
        6: 'task_id',
        7: 'task_name',
        8: 'user_id',
        9: 'record_date',
        10: 'work_hours',
        11: 'work_overtime',
        12: 'description',
        13: 'est_start_date',
        14: 'est_end_date',
        15: 'act_start_date',
        16: 'act_end_date'
    }, inplace=True)
    
    # df['actual_work_hours'] = df.work_hours + df.work_overtime
    df.work_hours = df.work_hours + df.work_overtime

    df.act_start_date.fillna(df.est_start_date, inplace=True)
    df.act_end_date.fillna(df.est_end_date, inplace=True)

    return df[[
        'dept_name', 
        'dept_no', 
        'dept_type', 
        'project_name', 
        'project_type', 
        'task_name', 
        'user_id', 
        'record_date', 
        'work_hours', 
        'description', 
        'est_start_date',
        'est_end_date',
        'act_start_date',
        'act_end_date'
    ]]

def get_df_employee(employee_name, dept_no, start_date, end_date):
    ts = get_ts_employee(employee_name, dept_no, start_date, end_date)
    
    if ts is None:
        return None
    
    df = pd.DataFrame(ts.json())
    df.rename(columns={
        0: 'dept_no',
        1: 'dept_name',
        2: 'dept_type',
        3: 'project_id',
        4: 'project_name',
        5: 'project_type',
        6: 'task_id',
        7: 'task_name',
        8: 'user_id',
        9: 'record_date',
        10: 'work_hours',
        11: 'work_overtime',
        12: 'description',
        13: 'est_start_date',
        14: 'est_end_date',
        15: 'act_start_date',
        16: 'act_end_date'
    }, inplace=True)
    
    # df['actual_work_hours'] = df.work_hours + df.work_overtime
    df.work_hours = df.work_hours + df.work_overtime
    
    df.act_start_date.fillna(df.est_start_date, inplace=True)
    df.act_end_date.fillna(df.est_end_date, inplace=True)
    
    return df[[
        'dept_name', 
        'dept_no', 
        'dept_type', 
        'project_name', 
        'project_type', 
        'task_name', 
        'user_id', 
        'record_date', 
        'work_hours', 
        'description', 
        'est_start_date',
        'est_end_date',
        'act_start_date',
        'act_end_date'
    ]]
