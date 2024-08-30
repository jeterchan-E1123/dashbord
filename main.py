import streamlit as st
import pandas as pd
from requests.exceptions import ConnectTimeout

from selectbox import get_selectbox_items, get_employee_list
from charts import dept_chart_task, dept_chart_ratio, employee_chart_task, employee_chart_ratio, gantt_dept, gantt_employee
from summaries import summary_dept as _summary_dept, summary_employee as _summary_employee
from dataframes import get_df_dept as _get_df_dept, get_df_employee as _get_df_employee
from task_summary import task_summary as _task_summary
from ai_chat import get_chat_answer

## for translate 
from googletrans import Translator
from googletrans.models import Translated
from text_dict import getdefaultDict,getChineseDict

# initial google translator
translator = Translator()
# origin_dict = getTextDict()

## translate language to dest_lang
def translate_text(text,dest_lang):
    translation = translator.translate(text, dest=dest_lang)
    return translation.text

project_type_colors = {'A': '#d55454', 'B': '#eea964', 'C': '#968cce', 'D': '#f2dac2'}


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
        dept_no = st.selectbox(st.session_state.text_dict['Department'], dept_list, format_func=lambda x: formatted_dict.get(x))
    with cols[1]:
        choose_date = st.selectbox(st.session_state.text_dict['Date'], [st.session_state.text_dict['Choose Date'], st.session_state.text_dict['All']])
    if choose_date == st.session_state.text_dict['Choose Date']:
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
        dept_no = st.selectbox(st.session_state.text_dict['Department'], dept_list, format_func=lambda x: formatted_dict.get(x))
    with cols[1]:
        employee_list = get_employee_list(dept_no)
        if employee_list is None:
            return 404
        employee_name = st.selectbox(st.session_state.text_dict['Employee'], employee_list)
    with cols[2]:
        choose_date = st.selectbox(st.session_state.text_dict['Date'], [st.session_state.text_dict['Choose Date'], st.session_state.text_dict['All']])
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
        st.subheader(st.session_state.text_dict['Working Hours'])
        
        subcols_l = st.columns(2)
        with subcols_l[0]:
            project_list = df.project_name.unique().tolist()
            project_list.insert(0, st.session_state.text_dict['All'])
            project_name = st.selectbox(st.session_state.text_dict['Project'], project_list)
            disable_task_option = (project_name == st.session_state.text_dict['All'])
            
        with subcols_l[1]:
            task_list = df.loc[df.project_name == project_name].task_name.unique().tolist()
            task_list.insert(0, st.session_state.text_dict['All'])
            task_name = st.selectbox(st.session_state.text_dict['Task'], task_list, disabled=disable_task_option)
        
        if disable_task_option:
            # projects chart
            fig_left = dept_chart_task(df, '*Project')
        else:
            # tasks chart
            fig_left = dept_chart_task(df, task_name, project_name)
        
        st.plotly_chart(fig_left, use_container_width=True)
        
    with cols[1].container(border=True):
        st.subheader(st.session_state.text_dict['Project Category Ratio'])
        
        subcols_r = st.columns(2, vertical_alignment='bottom')
        with subcols_r[0]:
            employee_list = df.user_id.unique().tolist()
            employee_list.insert(0, st.session_state.text_dict['All (Employee Detail)'])
            employee_list.insert(0, st.session_state.text_dict['All (Project Detail)'])
            employee_list.insert(0, st.session_state.text_dict['All'])
            employee_name = st.selectbox(st.session_state.text_dict['Employee'], employee_list)
        with subcols_r[1]:
            container = st.container(border=True)
            container.markdown(f"**{st.session_state.text_dict['Dept Type']}:** {df.dept_type.iat[0][0]}")
            
        st.write(employee_name)
        fig_right = dept_chart_ratio(df, employee_name)
        
        st.plotly_chart(fig_right, use_container_width=True)

def display_charts_employee(df: pd.DataFrame):
    cols = st.columns(2)
    with cols[0].container(border=True):
        st.subheader(st.session_state.text_dict['Working Hours'])
        
        subcols_l = st.columns(2)
        with subcols_l[0]:
            chart_option = st.selectbox(st.session_state.text_dict['Chart'], [st.session_state.text_dict['All Projects'], st.session_state.text_dict['All Tasks'], st.session_state.text_dict['Choose Project']])
            
        with subcols_l[1]:
            project_list = df.project_name.unique().tolist()
            project_list.insert(0, st.session_state.text_dict['All'])
            project_name = st.selectbox(st.session_state.text_dict['Project'], project_list, disabled=(chart_option!=st.session_state.text_dict['Choose Project']))
            
        fig_left = employee_chart_task(df, chart_option, project_name)
        
        st.plotly_chart(fig_left, use_container_width=True)
        
    with cols[1].container(border=True):
        st.subheader(st.session_state.text_dict['Project Category Ratio'])

        subcols_r = st.columns(2, vertical_alignment='bottom')
        with subcols_r[0]:
            pie_chart_option = st.selectbox(st.session_state.text_dict['Chart'], [st.session_state.text_dict['Default'], st.session_state.text_dict['Project Detail']])
        with subcols_r[1]:
            container = st.container(border=True)
            container.markdown(f"**{st.session_state.text_dict['Dept Type']}:** {df.dept_type.iat[0][0]}")
        
        fig_right = employee_chart_ratio(df, pie_chart_option)
        
        st.plotly_chart(fig_right, use_container_width=True)

def display_problematic_entries(df: pd.DataFrame):
    cols = st.columns(2)
    with cols[0]:
        project_list = df.project_name.unique().tolist()
        project_list.insert(0, st.session_state.text_dict['All'])
        project_name = st.selectbox(st.session_state.text_dict['Project'], project_list, key='problem_project')
        
        if project_name != st.session_state.text_dict['All']:
            df = df.loc[df.project_name == project_name]
    with cols[1]:
        task_list = df.task_name.unique().tolist()
        task_list.insert(0, st.session_state.text_dict['All'])
        task_name = st.selectbox(st.session_state.text_dict['Task'], task_list, key='problem_task')
        
        if task_name != st.session_state.text_dict['All']:
            df = df.loc[df.task_name == task_name]
    
    container = st.container(border=True)
    task_employees = ', '.join(df.user_id.unique().tolist())

    if df.shape[0] == 0:
        no_desc_percentage = 0
        with_desc_percentage = 0
    else:
        no_desc_percentage = df.loc[df.description == ''].shape[0] / df.shape[0]
        with_desc_percentage = df.loc[df.description != ''].shape[0] / df.shape[0]
    container.markdown(f'''**{st.session_state.text_dict['Employees']}:** {task_employees}\n
**{st.session_state.text_dict['Ratio']}:** {st.session_state.text_dict['No Description']} :blue-background[{format(no_desc_percentage, '.0%')}] &mdash; {st.session_state.text_dict['With Description']} :blue-background[{format(with_desc_percentage, '.0%')}]''')
    
    tab_list = [st.session_state.text_dict['No Description'], st.session_state.text_dict['With Description']]
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
        project_list.insert(0, st.session_state.text_dict['All'])
        project_name = st.selectbox(st.session_state.text_dict['Project'], project_list, key='task_summary_project', on_change=reset_tasksum)
        
        if project_name != 'All':
            df = df.loc[df.project_name == project_name]
    with cols[1]:
        task_list = df.task_name.unique().tolist()
        task_name = st.selectbox(st.session_state.text_dict['Task'], task_list, key='task_summary_task', on_change=reset_tasksum)
    
    st.button(st.session_state.text_dict['Create Task Summary'], use_container_width=True, on_click=tasksum_clicked)
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
    try:
        data = choosebox_dept()
    except ConnectTimeout as e:
        st.error('Please check your API server.')
        return
    if data is None:
        st.error('Please check your API connection.')
        return
    elif data == 404:
        st.info(st.session_state.text_dict['No data found.'])
        return
    
    dept_no, start_date, end_date, is_valid_date = data
    
    if not is_valid_date:
        st.error(st.session_state.text_dict['Invalid Date'])
        return
    
    df = get_df_dept(dept_no, start_date, end_date)
    
    if df is None:
        st.info(st.session_state.text_dict['No timesheet data found'])
        return
    
    tab_list = [st.session_state.text_dict['Charts'], st.session_state.text_dict['Gantt'], st.session_state.text_dict['Table']]
    tabs = st.tabs(tab_list)
    with tabs[0]: # Charts
        display_charts_dept(df)
    with tabs[1]: # Gantt
        gantt = gantt_dept(df, start_date, end_date)
        st.plotly_chart(gantt, use_container_width=True)
    with tabs[2]: # Table
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader(st.session_state.text_dict['Problematic Entries'])
    display_problematic_entries(df)
    
    st.divider()
    st.subheader(st.session_state.text_dict['Task Summary'])
    display_task_summary(df, type='dept')

    st.divider()
    st.subheader(st.session_state.text_dict['Summary'], divider='gray')
    summary = summary_dept(df, dept_no, start_date, end_date)
    st.markdown(summary)

    st.divider()
    st.subheader(st.session_state.text_dict['Ask AI'])
    ai_chat(df)

def display_dashboard_employee():
    try:
        data = choosebox_employee()
    except ConnectTimeout as e:
        st.error('Please check your API server.')
        return
    if data is None:
        st.error('Please check your API connection.')
        return
    elif data == 404:
        st.info(st.session_state.text_dict['No data found.'])
        return
    
    employee_name, dept_no, start_date, end_date, is_valid_date = data
    
    if not is_valid_date:
        st.error(st.session_state.text_dict['Invalid Date'])
        return
    
    df = get_df_employee(employee_name, dept_no, start_date, end_date)
    
    if df is None:
        st.info(st.session_state.text_dict['No timesheet data found'])
        return
    
    tab_list = [st.session_state.text_dict['Charts'], st.session_state.text_dict['Gantt'], st.session_state.text_dict['Table']]
    tabs = st.tabs(tab_list)
    with tabs[0]: # Charts
        display_charts_employee(df)
    with tabs[1]: # Gantt
        gantt = gantt_employee(df, start_date, end_date)
        st.plotly_chart(gantt, use_container_width=True)
    with tabs[2]: # Table
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader(st.session_state.text_dict['Problematic Entries'])
    display_problematic_entries(df)

    st.divider()
    st.subheader(st.session_state.text_dict['Task Summary'])
    display_task_summary(df, type='employee')

    st.divider()
    st.subheader(st.session_state.text_dict['Summary'], divider='gray')
    summary = summary_employee(df, employee_name, start_date, end_date)
    st.markdown(summary)

    st.divider()
    st.subheader(st.session_state.text_dict['Ask AI'])
    ai_chat(df)


def main():
    
    st.set_page_config(page_title=st.session_state.text_dict['page_title'], layout='wide', page_icon='clown_face')

    ## mutil language
    languages = {'English': 'en', 'Chinese': 'zh-tw'}
    selected_language = st.selectbox('Select Language', list(languages.keys()))
    dest_lang = languages[selected_language]
    

    # change language
    if dest_lang != st.session_state.language:
        st.session_state.language = dest_lang
        st.session_state.text_dict.update(text_dict[dest_lang])
        

    st.header('Dashboard API')

    dashboard = st.radio('Choose Dashboard', [st.session_state.text_dict['Department'], st.session_state.text_dict['Employee']], horizontal=True, label_visibility='collapsed')
    
    if dashboard == st.session_state.text_dict['Department']:
        display_dashboard_dept()
    else:
        display_dashboard_employee()
    
    
if __name__ == '__main__':

    # get English & Chinese Dictionary
    default_dict = getdefaultDict()
    chinese_dict = getChineseDict()

    # combine en & zh-tw dict
    text_dict = {
        'en':default_dict,
        'zh-tw':chinese_dict
    }

    # set default value of text_dict
    if 'text_dict' not in st.session_state:
        st.session_state.text_dict = default_dict.copy()

    # default is English
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    main()