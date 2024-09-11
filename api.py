from fastapi import FastAPI, HTTPException
import uvicorn

from connect import fetch_records

app = FastAPI()

@app.get('/dept_names')
async def get_dept_names():
    query = '''SELECT DISTINCT dept.dept_name_en
    FROM ma_or_department AS dept
    JOIN huntergame.ts_record AS ts ON dept.dept_no = ts.dept_no'''
    response = fetch_records(query)
    return response

@app.get('/dept_name/{dept_no}')
async def get_dept_name(dept_no):
    query = f'''SELECT dept_name_en
    FROM ma_or_dept_graph_v
    WHERE dept_no = \'{dept_no}\''''
    response = fetch_records(query)
    return response
    
@app.get('/dept_structure')
async def get_dept_structure():
    query = '''SELECT dept.dept_no_root, dept.dept_level, dept.dept_no, dept.dept_name_en
    FROM ma_or_dept_graph_v AS dept'''
    response = fetch_records(query)
    return response

@app.get('/employee_names/dept/{dept_no}')
async def get_employee_names(dept_no):
    query = f'''SELECT DISTINCT ts.user_id
    FROM huntergame.ts_record AS ts
    JOIN ma_or_dept_graph_v AS dept ON ts.dept_no = dept.dept_no
    WHERE dept.dept_no_root=\'{dept_no}\''''
    response = fetch_records(query)
    return response

@app.get('/ts_dept/{dept_no}/date/{start_date}/{end_date}')
async def get_ts_dept(dept_no, start_date, end_date):
    if start_date.lower() == 'all':
        query = f'''SELECT dept.dept_no, dept.dept_name_en, dept2.or_level_id,
        ts.project_id, proj.proj_name_cn, proj.proj_type, ts.task_id, task.proj_tk_name, 
        ts.user_id, ts.record_date, ts.work_hours, ts.work_overtime, ts.description,
        proj.est_start_date, proj.est_end_date, proj.act_start_date, proj.act_end_date
        FROM ma_or_dept_graph_v AS dept
        JOIN huntergame.ts_record AS ts ON ts.dept_no = dept.dept_no
        JOIN huntergame.proj_info AS proj ON proj.proj_id = ts.project_id
        JOIN huntergame.proj_tk AS task ON task.id = ts.task_id
        JOIN ma_or_department AS dept2 ON dept2.dept_no = dept.dept_no
        WHERE dept_no_root = \'{dept_no}\''''
    else:
        query = f'''SELECT dept.dept_no, dept.dept_name_en, dept2.or_level_id,
        ts.project_id, proj.proj_name_cn, proj.proj_type, ts.task_id, task.proj_tk_name, 
        ts.user_id, ts.record_date, ts.work_hours, ts.work_overtime, ts.description,
        proj.est_start_date, proj.est_end_date, proj.act_start_date, proj.act_end_date
        FROM ma_or_dept_graph_v AS dept
        JOIN huntergame.ts_record AS ts ON ts.dept_no = dept.dept_no
        JOIN huntergame.proj_info AS proj ON proj.proj_id = ts.project_id
        JOIN huntergame.proj_tk AS task ON task.id = ts.task_id
        JOIN ma_or_department AS dept2 ON dept2.dept_no = dept.dept_no
        WHERE dept_no_root = \'{dept_no}\'
        AND ts.record_date >= \'{start_date}\'
        AND ts.record_date <= \'{end_date}\''''
    response = fetch_records(query)
    return response
    
@app.get('/ts_employee/{employee_name}/dept/{dept_no}/date/{start_date}/{end_date}')
async def get_ts_employee(employee_name, dept_no, start_date, end_date):
    if start_date.lower() == 'all':
        query = f'''SELECT dept.dept_no, dept.dept_name_en, dept2.or_level_id,
        ts.project_id, proj.proj_name_cn, proj.proj_type, ts.task_id, task.proj_tk_name, 
        ts.user_id, ts.record_date, ts.work_hours, ts.work_overtime, ts.description,
        proj.est_start_date, proj.est_end_date, proj.act_start_date, proj.act_end_date
        FROM ma_or_dept_graph_v AS dept
        JOIN huntergame.ts_record AS ts ON ts.dept_no = dept.dept_no
        JOIN huntergame.proj_info AS proj ON proj.proj_id = ts.project_id
        JOIN huntergame.proj_tk AS task ON task.id = ts.task_id
        JOIN ma_or_department AS dept2 ON dept2.dept_no = dept.dept_no
        WHERE dept_no_root = \'{dept_no}\'
        AND ts.user_id = \'{employee_name}\''''
    else:
        query = f'''SELECT dept.dept_no, dept.dept_name_en, dept2.or_level_id,
        ts.project_id, proj.proj_name_cn, proj.proj_type, ts.task_id, task.proj_tk_name, 
        ts.user_id, ts.record_date, ts.work_hours, ts.work_overtime, ts.description,
        proj.est_start_date, proj.est_end_date, proj.act_start_date, proj.act_end_date
        FROM ma_or_dept_graph_v AS dept
        JOIN huntergame.ts_record AS ts ON ts.dept_no = dept.dept_no
        JOIN huntergame.proj_info AS proj ON proj.proj_id = ts.project_id
        JOIN huntergame.proj_tk AS task ON task.id = ts.task_id
        JOIN ma_or_department AS dept2 ON dept2.dept_no = dept.dept_no
        WHERE dept_no_root = \'{dept_no}\'
        AND ts.user_id = \'{employee_name}\'
        AND ts.record_date >= \'{start_date}\'
        AND ts.record_date <= \'{end_date}\''''
    response = fetch_records(query)
    return response

@app.get("/test/{employee_name}/{dept_no}")
async def test(employee_name, dept_no):
    query = f'''SELECT dept.dept_no, dept.dept_name_en,
    ts.project_id, proj.proj_name_cn, ts.task_id, task.proj_tk_name, ts.user_id, 
    ts.record_date, ts.work_hours, ts.work_overtime, ts.description
    FROM ma_or_dept_graph_v AS dept
    JOIN huntergame.ts_record AS ts ON ts.dept_no = dept.dept_no
    JOIN huntergame.proj_info AS proj ON proj.proj_id = ts.project_id
    JOIN huntergame.proj_tk AS task ON task.id = ts.task_id
    WHERE dept_no_root = \'{dept_no}\''''
    
    query = f'''SELECT dept.dept_no, dept.dept_name_en, dept2.or_level_id,
    ts.project_id, proj.proj_name_cn, proj.proj_type, ts.task_id, task.proj_tk_name, 
    ts.user_id, ts.record_date, ts.work_hours, ts.work_overtime, ts.description,
    proj.est_start_date, proj.est_end_date, proj.act_start_date, proj.act_end_date
    FROM ma_or_dept_graph_v AS dept
    JOIN huntergame.ts_record AS ts ON ts.dept_no = dept.dept_no
    JOIN huntergame.proj_info AS proj ON proj.proj_id = ts.project_id
    JOIN huntergame.proj_tk AS task ON task.id = ts.task_id
    JOIN ma_or_department AS dept2 ON dept2.dept_no = dept.dept_no
    WHERE dept_no_root = \'{dept_no}\'
    AND ts.user_id = \'{employee_name}\''''
    response = fetch_records(query)
    return response

@app.get("/")
async def home():
    query = f'''SELECT dept_no, dept_name_en
    FROM ma_or_dept_graph_v'''
    return fetch_records(query)
 
    
if __name__ == "__main__":
    uvicorn.run('api_functions:app', port=8000, reload=True)
