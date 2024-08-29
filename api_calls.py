import requests

instance_ip = '44.242.221.194'
port = '8000'

def get_dept_names():
    response = requests.get(url=f'http://{instance_ip}:{port}/dept_names')
    if response.status_code != 200:
        return None
    return response

def get_dept_name(dept_no: str):
    response = requests.get(url=f'http://{instance_ip}:{port}/dept_name/{dept_no}')
    if response.status_code != 200:
        return None
    return response

def get_employee_names(dept_no: str):
    response = requests.get(url=f'http://{instance_ip}:{port}/employee_names/dept/{dept_no}')
    if response.status_code != 200:
        return None
    return response

def get_dept_structure_raw():
    response = requests.get(url=f'http://{instance_ip}:{port}/dept_structure')
    if response.status_code != 200 or len(response.json()) == 0:
        return None
    return response
    
def get_ts_dept(dept_no, start_date, end_date):
    ts = requests.get(url=f'http://{instance_ip}:{port}/ts_dept/{dept_no}/date/{start_date}/{end_date}')
    if ts.status_code != 200 or len(ts.json()) == 0:
        return None
    return ts
    
def get_ts_employee(employee_name, dept_no, start_date, end_date):
    ts = requests.get(url=f'http://{instance_ip}:{port}/ts_employee/{employee_name}/dept/{dept_no}/date/{start_date}/{end_date}')
    if ts.status_code != 200 or len(ts.json()) == 0:
        return None
    return ts

def get_children_dept(dept_no):
    response = requests.get(url=f'http://{instance_ip}:{port}/children_dept/{dept_no}')
    if response.status_code != 200:
        return None
    return response

def children_dept_list(dept_no):
    children_dept = get_children_dept(dept_no)
    dept_list = sum(children_dept.json(), [])
    parameter = '&q='.join(dept_list)
    response = requests.get(url=f'http://{instance_ip}:{port}/ts_children_dept/?q={parameter}')
    if response.status_code != 200:
        return None
    return response
    
def test(employee_name, dept_no):
    response = requests.get(url=f'http://{instance_ip}:{port}/test/{employee_name}/{dept_no}')
    return response
