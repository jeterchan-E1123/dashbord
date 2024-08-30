import pandas as pd
import numpy as np
from datetime import datetime

from dataframes import *
from api_calls import get_dept_name

def get_main_project_list(df_proj):
    if df_proj.shape[0] < 3:
        return df_proj.project_name.tolist()
    
    avg_work_hours = df_proj.work_hours.mean()
    proj_list = []
    for index, row in df_proj.iterrows():
        if row.work_hours >= avg_work_hours:
            proj_list.append(row['project_name'])
    
    return proj_list

def get_project_type_percentage(df_proj, df_ratio, main_proj_list):
    proj_dict = {}
    for index, row in df_ratio.iterrows():
        row_dict = {
            'percentage' : row.ratio,
            'projects' : []
        }
        proj_dict[row.project_type] = row_dict

    for index, row in df_proj.iterrows():
        if row.project_name in main_proj_list:
            proj_dict[row.project_type]['projects'].append(row.project_name)

    return proj_dict

def get_proj_type_str(proj_type_dict, dept_type, dept_name):
    result = f''
    low_performance = False
    low_performance_percentage = 0

    for proj_type in proj_type_dict:
        percentage = proj_type_dict[proj_type]['percentage']
        proj_list = proj_type_dict[proj_type]['projects']
        if len(proj_list) > 0:
            result += f"- **{format(percentage, '.2%')}** of time was dedicated to **Project Type {proj_type}**, such as *{', '.join(proj_list)}*.\n"

        if dept_type == 'C' and proj_type == 'A' and percentage < 0.6:
            low_performance = True
            low_performance_percentage = percentage

    if low_performance:
        result += f'''
**Note:** As a member of {dept_name} Department, it is important to note that only **{format(low_performance_percentage, '0.2%')}**
of time was allocated to projects of type A.
'''

    return result

def get_lt8_date_list(df):
    '''
    Get the list of dates with less than 8 hours of work_hours.
    '''
    df_daily_hours = create_df_daily_hours(df)
    df_daily_hours = df_daily_hours.loc[df_daily_hours.under_8 == 1]
    result = df_daily_hours.record_date.tolist()
    return result

def get_duration_str(start_date, end_date):
    start_date_object = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_object = datetime.strptime(end_date, '%Y-%m-%d').date()
    duration = end_date_object - start_date_object
    return f'During the span of **{duration.days}** days'

def summary_dept(df, dept_no, start_date, end_date):
    if start_date.lower() == 'all':
        start_date = df.record_date.min()
        end_date = df.record_date.max()

    date_str = f'{start_date} ~ {end_date}'
    duration_str = get_duration_str(start_date, end_date)
    employee_count = len(df.user_id.unique())
    dept_name = get_dept_name(dept_no).json()[0][0]

    df_proj = create_df_project(df)
    df_ratio = create_df_ratio(df)
    df_ratio_dept = create_df_ratio_dept(df_ratio)
    main_proj_list = get_main_project_list(df_proj)
    proj_type_dict = get_project_type_percentage(df_proj, df_ratio_dept, main_proj_list)
    proj_type_str = get_proj_type_str(proj_type_dict, df.dept_type[0][0], dept_name)

    summary = f'''
###### Date: {date_str}\n
###### Department Name: {dept_name} ({dept_no})\n
###### No. of Employees: {employee_count}\n
###### Summary:
{duration_str}, the **{dept_name}** Department focused on the following key projects: *{', '.join(main_proj_list)}*.\n
{proj_type_str}
In total, {dept_name} Department contributed **{df_ratio_dept.work_hours.sum()} hours** during this period.\n
'''
    return summary

def summary_employee(df, employee_name, start_date, end_date):
    if start_date.lower() == 'all':
        start_date = df.record_date.min()
        end_date = df.record_date.max()
        
    date_str = f'{start_date} ~ {end_date}'
    duration_str = get_duration_str(start_date, end_date)
    dept_name = df.dept_name[0]

    df_proj = create_df_project(df)
    df_ratio = create_df_ratio(df)
    main_proj_list = get_main_project_list(df_proj)
    proj_type_dict = get_project_type_percentage(df_proj, df_ratio, main_proj_list)
    proj_type_str = get_proj_type_str(proj_type_dict, df.dept_type[0][0], dept_name)
    lt8_date_list = get_lt8_date_list(df)

    summary = f'''
###### Date: {date_str}\n
###### Employee Name: {employee_name}\n
###### Department: {dept_name} ({df.dept_no[0]})\n
###### Summary:
{duration_str}, **{employee_name}** focused on the following projects: *{', '.join(main_proj_list)}*.\n
{proj_type_str}
In total, {employee_name} contributed **{df_ratio.work_hours.sum()} hours** during this period.\n
'''
    
    if len(lt8_date_list) > 0:
        summary += f"Notably, {employee_name} worked **less than 8 hours** on the following dates: {', '.join(lt8_date_list)}.\n"
    
    return summary
