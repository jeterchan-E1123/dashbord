import pandas as pd

from api_calls import get_dept_structure_raw, get_employee_names

def get_dept_structure():
    '''
    Returns a dataframe containing information about dept_no_root, dept_level, dept_no, dept_name.
    '''
    
    response = get_dept_structure_raw()
    
    if response is None:
        return None
    
    df = pd.DataFrame(response.json())
    df.rename(columns={
        0: 'dept_no_root',
        1: 'dept_level',
        2: 'dept_no',
        3: 'dept_name'
    }, inplace=True)
    
    return df

def create_dept_dict(df: pd.DataFrame):
    '''
    Returns a dictionary of each dept's name, parent and level, with the dept_no as the key.
    '''
    # max_depth = 0

    dept_dict = {}
    for index, row in df.iterrows():
        if row.dept_no not in dept_dict:
            dept_dict[row.dept_no] = {
                'dept_name' : row.dept_name,
                'formatted_name' : f'{row.dept_name} ({row.dept_no})',
                'depth' : row.dept_level
            }
        elif dept_dict[row.dept_no]['depth'] < row.dept_level:
            dept_dict[row.dept_no]['depth'] = row.dept_level
    
        if row.dept_level == 1:
            dept_dict[row.dept_no]['parent'] = row.dept_no_root
    
        # if row.dept_level > max_depth:
        #     max_depth = row.dept_level
    
    return dept_dict

def build_tree(dept_dict: dict) -> dict:
    tree = {}
    
    # Create a lookup for parent-child relationships
    children = {key: [] for key in dept_dict.keys()}
    for key, value in dept_dict.items():
        parent = value.get('parent')
        if parent is None:
            tree[key] = {}
        else:
            children[parent].append(key)
    
    # Recursive function to add nodes to the tree
    def add_children(node_key, subtree):
        if node_key not in subtree:
            subtree[node_key] = {}
        
        for child_key in children.get(node_key, []):
            add_children(child_key, subtree[node_key])
    
    # Build the tree by adding children to root nodes
    for root_key in tree.keys():
        add_children(root_key, tree)
    
    return tree

def generate_key_list(tree: dict):
    for key, children in tree.items():
        yield key
        yield from generate_key_list(children)

def generate_indented_list(dept_dict, tree, indent_level=0) -> list:
    indented_list = []
    indent = '\u2001' * 4 * indent_level  # 4 spaces per indentation level
    
    # recursive function to add indentation
    for key, children in tree.items():
        indented_list.append(f"{indent}{dept_dict[key]['formatted_name']}")
        indented_list.extend(generate_indented_list(dept_dict, children, indent_level + 1))
    
    return indented_list

def generate_formatted_dict(dept_tree: dict, key_list: list, dept_dict: dict) -> dict:
    value_list = generate_indented_list(dept_dict, dept_tree)
    result = {key_list[i]: value_list[i] for i in range(len(key_list))}
    return result

def get_selectbox_items():
    dept_structure = get_dept_structure()
    if dept_structure is None:
        return None, None
    dept_dict = create_dept_dict(dept_structure)
    dept_tree = build_tree(dept_dict)
    dept_list = list(generate_key_list(dept_tree)) # list of dept no
    formatted_dict = generate_formatted_dict(dept_tree, dept_list, dept_dict)
    return dept_list, formatted_dict

def get_employee_list(dept_no):
    employee_names = get_employee_names(dept_no)
    if employee_names is None:
        return None
    employee_list = sum(employee_names.json(), [])
    employee_list.sort()
    return employee_list
