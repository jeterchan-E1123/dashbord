import streamlit as st
import pandas as pd

from selectbox import get_selectbox_items, get_employee_list
from charts import dept_chart_task, dept_chart_ratio, employee_chart_task, employee_chart_ratio, gantt_dept, gantt_employee
from summaries import summary_dept as _summary_dept, summary_employee as _summary_employee
from dataframes import get_df_dept as _get_df_dept, get_df_employee as _get_df_employee
from task_summary import task_summary as _task_summary
from ai_chat import get_chat_answer
from text_dict import text_dict

project_type_colors = {'A': '#d55454', 'B': '#eea964', 'C': '#968cce', 'D': '#f2dac2'}

st.set_page_config(page_title=text_dict['page_title'], layout='wide', page_icon='clown_face')

@st.cache_data
def summary_dept(df, dept_no, start_date, end_date):
    return _summary_dept(df, dept_no, start_date, end_date)

@st.cache_data
def summary_employee(df, employee_name, start_date, end_date):
    return _summary_employee(df, employee_name, start_date, end_date)

@st.cache_data
def get_df_dept(dept_no, start_date, end_date):
    return _get_df_dept(dept_no, start_date, end_date)

@st.cache_data
def get_df_employee(employee_name, dept_no, start_date, end_date):
    return _get_df_employee(employee_name, dept_no, start_date, end_date)

@st.cache_data(show_spinner=False)
def task_summary(df, task_name, type):
    return _task_summary(df, task_name, type)

def choosebox_dept():
    cols = st.columns(3)
    
    with cols[0]:
        dept_list, formatted_dict = get_selectbox_items()
        if dept_list is None or formatted_dict is None:
            return None
        dept_no = st.selectbox('Department', dept_list, format_func=lambda x: formatted_dict.get(x))
    with cols[1]:
        choose_date = st.selectbox('Date', ['Choose Date', 'All'])
    if choose_date == 'Choose Date':
        with cols[2]:
            subcols = st.columns(2)
            with subcols[0]:
                start_date = st.date_input('Start Date')
            with subcols[1]:
                end_date = st.date_input('End Date')
            is_valid_date = start_date <= end_date
            start_date = start_date.strftime('%Y-%m-%d')
            end_date = end_date.strftime('%Y-%m-%d')
    else:
        start_date = 'all'
        end_date = 'all'
        is_valid_date = True
        
    return dept_no, start_date, end_date, is_valid_date

def choosebox_employee():
    cols = st.columns(4)
    
    with cols[0]:
        dept_list, formatted_dict = get_selectbox_items()
        if dept_list is None or formatted_dict is None:
            return None
        dept_no = st.selectbox('Department', dept_list, format_func=lambda x: formatted_dict.get(x))
    with cols[1]:
        employee_list = get_employee_list(dept_no)
        if employee_list is None:
            return 404
        employee_name = st.selectbox('Employee', employee_list)
    with cols[2]:
        choose_date = st.selectbox('Date', ['Choose Date', 'All'])
    if choose_date == 'Choose Date':
        with cols[3]:
            subcols = st.columns(2)
            with subcols[0]:
                start_date = st.date_input('Start Date')    # start_date value
            with subcols[1]:
                end_date = st.date_input('End Date')    # end_date value
            is_valid_date = start_date <= end_date
            start_date = start_date.strftime('%Y-%m-%d')    # start_date format
            end_date = end_date.strftime('%Y-%m-%d')        # end_date format
    else:
        start_date = 'all'
        end_date = 'all'
        is_valid_date = True
        
    return employee_name, dept_no, start_date, end_date, is_valid_date

def display_charts_dept(df: pd.DataFrame):
    cols = st.columns(2)
    
    with cols[0].container(border=True):
        st.subheader('Working Hours')
        
        subcols_l = st.columns(2)
        with subcols_l[0]:
            project_list = df.project_name.unique().tolist()
            project_list.insert(0, 'All')
            project_name = st.selectbox('Project', project_list)
            disable_task_option = (project_name == 'All')
            
        with subcols_l[1]:
            task_list = df.loc[df.project_name == project_name].task_name.unique().tolist()
            task_list.insert(0, 'All')
            task_name = st.selectbox('Task', task_list, disabled=disable_task_option)
        
        if disable_task_option:
            # projects chart
            fig_left = dept_chart_task(df, '*Project')
        else:
            # tasks chart
            fig_left = dept_chart_task(df, task_name, project_name)
        
        st.plotly_chart(fig_left, use_container_width=True)
        
    with cols[1].container(border=True):
        st.subheader('Project Category Ratio')
        
        subcols_r = st.columns(2, vertical_alignment='bottom')
        with subcols_r[0]:
            employee_list = df.user_id.unique().tolist()
            employee_list.insert(0, 'All (Employee Detail)')
            employee_list.insert(0, 'All (Project Detail)')
            employee_list.insert(0, 'All')
            employee_name = st.selectbox('Employee', employee_list)
        with subcols_r[1]:
            container = st.container(border=True)
            container.markdown(f'**Dept Type:** {df.dept_type.iat[0][0]}')
            
        fig_right = dept_chart_ratio(df, employee_name)
        
        st.plotly_chart(fig_right, use_container_width=True)

def display_charts_employee(df: pd.DataFrame):
    cols = st.columns(2)
    with cols[0].container(border=True):
        st.subheader('Working Hours')
        
        subcols_l = st.columns(2)
        with subcols_l[0]:
            chart_option = st.selectbox('Chart', ['All Projects', 'All Tasks', 'Choose Project'])
            
        with subcols_l[1]:
            project_list = df.project_name.unique().tolist()
            project_list.insert(0, 'All')
            project_name = st.selectbox('Project', project_list, disabled=(chart_option!='Choose Project'))
            
        fig_left = employee_chart_task(df, chart_option, project_name)
        
        st.plotly_chart(fig_left, use_container_width=True)
        
    with cols[1].container(border=True):
        st.subheader('Project Category Ratio')

        subcols_r = st.columns(2, vertical_alignment='bottom')
        with subcols_r[0]:
            pie_chart_option = st.selectbox('Chart', ['Default', 'Project Detail'])
        with subcols_r[1]:
            container = st.container(border=True)
            container.markdown(f'**Dept Type:** {df.dept_type.iat[0][0]}')
        
        fig_right = employee_chart_ratio(df, pie_chart_option)
        
        st.plotly_chart(fig_right, use_container_width=True)

def display_problematic_entries(df: pd.DataFrame):
    cols = st.columns(2)
    with cols[0]:
        project_list = df.project_name.unique().tolist()
        project_list.insert(0, 'All')
        project_name = st.selectbox('Project', project_list, key='problem_project')
        
        if project_name != 'All':
            df = df.loc[df.project_name == project_name]
    with cols[1]:
        task_list = df.task_name.unique().tolist()
        task_list.insert(0, 'All')
        task_name = st.selectbox('Task', task_list, key='problem_task')
        
        if task_name != 'All':
            df = df.loc[df.task_name == task_name]
    
    container = st.container(border=True)
    task_employees = ', '.join(df.user_id.unique().tolist())
    if df.shape[0] == 0:
        no_desc_percentage = 0
        with_desc_percentage = 0
    else:
        no_desc_percentage = df.loc[df.description == ''].shape[0] / df.shape[0]
        with_desc_percentage = df.loc[df.description != ''].shape[0] / df.shape[0]
    container.markdown(f'''**Employees:** {task_employees}\n
**Ratio:** No Description :blue-background[{format(no_desc_percentage, '.0%')}] &mdash; With Description :blue-background[{format(with_desc_percentage, '.0%')}]''')
    
    tab_list = ['No Description', 'With Description']
    tabs = st.tabs(tab_list)
    df_display = df[['dept_name', 'project_name', 'project_type', 'task_name', 'user_id', 'record_date', 'work_hours', 'description']]
    with tabs[0]:
        df_nodesc = df_display.loc[df_display.description == '']
        st.dataframe(df_nodesc.reset_index(drop=True), use_container_width=True)
    with tabs[1]:
        df_desc = df_display.loc[df_display.description != '']
        st.dataframe(df_desc.reset_index(drop=True), use_container_width=True)

if 'tasksum_clicked' not in st.session_state:
    st.session_state.tasksum_clicked = False

def tasksum_clicked():
    st.session_state.tasksum_clicked = True
    task_summary.clear()

def reset_tasksum():
    st.session_state.tasksum_clicked = False

def display_task_summary(df: pd.DataFrame, type: str):
    cols = st.columns(2)
    with cols[0]:
        project_list = df.project_name.unique().tolist()
        project_list.insert(0, 'All')
        project_name = st.selectbox('Project', project_list, key='task_summary_project', on_change=reset_tasksum)
        
        if project_name != 'All':
            df = df.loc[df.project_name == project_name]
    with cols[1]:
        task_list = df.task_name.unique().tolist()
        task_name = st.selectbox('Task', task_list, key='task_summary_task', on_change=reset_tasksum)
    
    st.button('Create Task Summary', use_container_width=True, on_click=tasksum_clicked)
    # if st.button('Create Task Summary', use_container_width=True, on_click=task_summary.clear):
    if st.session_state.tasksum_clicked:
        with st.spinner('Creating task summary...'):
            try:
                result = task_summary(df, task_name, type=type)
                st.chat_message('ai').write(result)
            except Exception as e:
                st.error(e)

def ai_chat(df):
    container = st.container()
    question = container.chat_input('Ask a question')
    if question:
        with container.chat_message('user'):
            st.write(question)

        with st.spinner('AI is thinking...'):
            answer = get_chat_answer(df, question)
            
            with container.chat_message('ai'):
                st.write(answer)

def display_dashboard_dept():
    data = choosebox_dept()
    if data is None:
        st.error('Please check your API connection.')
        return
    elif data == 404:
        st.info('No data found.')
        return
    
    dept_no, start_date, end_date, is_valid_date = data
    
    if not is_valid_date:
        st.error('Invalid Date')
        return
    
    df = get_df_dept(dept_no, start_date, end_date)
    
    if df is None:
        st.info('No timesheet data found')
        return
    
    tab_list = ['Charts', 'Gantt', 'Table']
    tabs = st.tabs(tab_list)
    with tabs[0]: # Charts
        display_charts_dept(df)
    with tabs[1]: # Gantt
        gantt = gantt_dept(df, start_date, end_date)
        st.plotly_chart(gantt, use_container_width=True)
    with tabs[2]: # Table
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader('Problematic Entries')
    display_problematic_entries(df)
    
    st.divider()
    st.subheader('Task Summary')
    display_task_summary(df, type='dept')

    st.divider()
    st.subheader('Summary', divider='gray')
    summary = summary_dept(df, dept_no, start_date, end_date)
    st.markdown(summary)

    st.divider()
    st.subheader('Ask AI')
    ai_chat(df)

def display_dashboard_employee():
    data = choosebox_employee()
    if data is None:
        st.error('Please check your API connection.')
        return
    elif data == 404:
        st.info('No data found.')
        return
    
    employee_name, dept_no, start_date, end_date, is_valid_date = data
    
    if not is_valid_date:
        st.error('Invalid Date')
        return
    
    df = get_df_employee(employee_name, dept_no, start_date, end_date)
    
    if df is None:
        st.info('No timesheet data found')
        return
    
    tab_list = ['Charts', 'Gantt', 'Table']
    tabs = st.tabs(tab_list)
    with tabs[0]: # Charts
        display_charts_employee(df)
    with tabs[1]: # Gantt
        gantt = gantt_employee(df, start_date, end_date)
        st.plotly_chart(gantt, use_container_width=True)
    with tabs[2]: # Table
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader('Problematic Entries')
    display_problematic_entries(df)

    st.divider()
    st.subheader('Task Summary')
    display_task_summary(df, type='employee')

    st.divider()
    st.subheader('Summary', divider='gray')
    summary = summary_employee(df, employee_name, start_date, end_date)
    st.markdown(summary)

    st.divider()
    st.subheader('Ask AI')
    ai_chat(df)


def main():
    st.header('Dashboard API')
    dashboard = st.radio('Choose Dashboard', ['Department', 'Employee'], horizontal=True, label_visibility='collapsed')
    
    if dashboard == 'Department':
        display_dashboard_dept()
    else:
        display_dashboard_employee()
    
    
if __name__ == '__main__':
    main()
