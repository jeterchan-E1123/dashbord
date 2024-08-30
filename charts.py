import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dataframes import create_df_task, create_df_ratio

project_type_colors = {'A': '#d55454', 'B': '#eea964', 'C': '#968cce', 'D': '#f2dac2'}

def dept_chart_task(df, task_name, project_name = None):
    '''
    Bar/Pie Chart for Working Hours
    '''
    df_task = create_df_task(df)
    
    if project_name is not None and task_name == '*Project':
        df_task = df_task.loc[df_task.project_name == project_name]
    
    if task_name == 'All':
        fig = px.bar(df_task, x='task_name', y='work_hours', color='user_id', title='Hours per Task', text_auto=True)
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        df_total = df_task.groupby('task_name').sum()
        fig.add_trace(go.Scatter(x=df_total.index, y=df_total.work_hours, text=df_total.work_hours, mode='text', textposition='top center', showlegend=False))
    elif task_name == '*Project':
        fig = px.bar(df_task, x='project_name', y='work_hours', title='Hours per Project', color='project_name', text_auto=True, hover_data=['project_type'])
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        df_total = df_task.groupby('project_name').sum()
        fig.add_trace(go.Scatter(x=df_total.index, y=df_total.work_hours, text=df_total.work_hours, mode='text', textposition='top center', showlegend=False))
    else:
        df_task = df_task.loc[df_task.task_name == task_name]
        fig = px.pie(df_task, values='work_hours', names='user_id', title='Hours per Task')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
    return fig

def employee_chart_task(df, chart_option, project_name):
    df_task = create_df_task(df)
    
    if chart_option == 'All Projects':
        fig = px.bar(df_task, x='project_name', y='work_hours', title='Hours per Project', color='project_name', text_auto=True, hover_data=['project_type'])
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        df_total = df_task.groupby('project_name').sum()
        fig.add_trace(go.Scatter(x=df_total.index, y=df_total.work_hours, text=df_total.work_hours, mode='text', textposition='top center', showlegend=False))
    elif chart_option == 'Choose Project' and project_name != 'All':
        df_task = df_task.loc[df_task.project_name == project_name]
        fig = px.bar(df_task, x='task_name', y='work_hours', title='Hours per Task', color='task_name', text_auto=True)
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    else:
        fig = px.bar(df_task, x='task_name', y='work_hours', title='Hours per Task', color='project_name', text_auto=True)
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        df_total = df_task.groupby('task_name').sum()
        fig.add_trace(go.Scatter(x=df_total.index, y=df_total.work_hours, text=df_total.work_hours, mode='text', textposition='top center', showlegend=False))
    
    return fig

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
    
def dept_chart_ratio(df, employee_name):
    '''
    Pie/Sunburst Chart for Project Category Ratio
    '''
    df_ratio = create_df_ratio(df)
    
    if (employee_name != 'All' and employee_name != '全部') and (employee_name != 'All (Employee Detail)' and employee_name != '所有（員工細節）'):
        df_ratio = df_ratio.loc[df_ratio.user_id == employee_name]
    
    if employee_name == 'All (Employee Detail)' or employee_name == '所有（員工細節）':
        fig = px.sunburst(df_ratio, path=['project_type', 'user_id'], values='work_hours', color='project_type', color_discrete_map=project_type_colors)
        fig.update_traces(textinfo='label+percent root')
    elif employee_name == 'All (Project Detail)' or employee_name == '所有（專案細節）':
        fig = px.sunburst(df, path=['project_type', 'project_name'], values='work_hours', color='project_type', color_discrete_map=project_type_colors)
        fig.update_traces(textinfo='label+percent root')
    else:
        fig = px.pie(df_ratio, values='work_hours', names='project_type', color='project_type', color_discrete_map=project_type_colors)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
    return fig
    
def employee_chart_ratio(df, chart_option):
    df_ratio = create_df_ratio(df)
    
    if chart_option == 'Default':
        fig = px.pie(df_ratio, values='work_hours', names='project_type', color='project_type', color_discrete_map=project_type_colors)
        fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        fig = px.sunburst(df, path=['project_type', 'project_name'], values='work_hours', color='project_type', color_discrete_map=project_type_colors)
        fig.update_traces(textinfo='label+percent root')
        
    return fig
    
def gantt_dept(df, start_date_marker, end_date_marker):
    df = df[df.project_name != '請假']
    df.dropna(inplace=True)

    df_est = df[['project_name', 'est_start_date', 'est_end_date']]
    df_est['type'] = 'Estimated Date'
    df_est.rename(columns={'est_start_date': 'start_date', 'est_end_date': 'end_date'}, inplace=True)

    df_act = df[['project_name', 'act_start_date', 'act_end_date']]
    df_act['type'] = 'Actual Date'
    df_act.rename(columns={'act_start_date': 'start_date', 'act_end_date': 'end_date'}, inplace=True)

    df_gantt = pd.concat([df_est, df_act])

    gantt = px.timeline(df_gantt, x_start='start_date', x_end='end_date', color='type', y='project_name')
    gantt.update_layout(barmode='group')
    gantt.add_vline(x=start_date_marker, line_width=1, line_color="gray")
    gantt.add_vline(x=end_date_marker, line_width=1, line_color="gray")
    
    return gantt
    
def gantt_employee(df, start_date_marker, end_date_marker):
    df = df[df.project_name != '請假']
    df.dropna(inplace=True)

    df_est = df[['project_name', 'est_start_date', 'est_end_date']]
    df_est['type'] = 'Estimated Date'
    df_est.rename(columns={'est_start_date': 'start_date', 'est_end_date': 'end_date'}, inplace=True)

    df_act = df[['project_name', 'act_start_date', 'act_end_date']]
    df_act['type'] = 'Actual Date'
    df_act.rename(columns={'act_start_date': 'start_date', 'act_end_date': 'end_date'}, inplace=True)
    
    df_emp = df[['project_name']]
    df_emp['type'] = 'Employee Recorded Date'
    df_emp.drop_duplicates(inplace=True)
    
    df_emp_start = df.groupby(by='project_name', as_index=False)['record_date'].min()
    df_emp_start.rename(columns={'record_date': 'start_date'}, inplace=True)
    df_emp = df_emp.merge(df_emp_start, on='project_name', how='inner')

    df_emp_end = df.groupby(by='project_name', as_index=False)['record_date'].max()
    df_emp_end.rename(columns={'record_date': 'end_date'}, inplace=True)
    df_emp = df_emp.merge(df_emp_end, on='project_name', how='inner')

    df_gantt = pd.concat([df_est, df_act, df_emp])

    gantt = px.timeline(df_gantt, x_start='start_date', x_end='end_date', color='type', y='project_name')
    gantt.update_layout(barmode='group')
    gantt.add_vline(x=start_date_marker, line_width=1, line_color="gray")
    gantt.add_vline(x=end_date_marker, line_width=1, line_color="gray")
    
    return gantt
