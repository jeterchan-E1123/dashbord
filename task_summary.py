import pandas as pd
import boto3
from dotenv import load_dotenv

from langchain_aws import BedrockLLM, ChatBedrock
from langchain.agents import tool, Tool
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_experimental.utilities import PythonREPL
from langchain.tools.render import render_text_description
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel

from dataframes import create_df_tasksum

load_dotenv()

bedrock_client = boto3.client(service_name="bedrock-runtime")

class TaskSummary(BaseModel):
    """Task Summary Output"""
    summary: str

def get_chat_prompt():
    prompt_template = """You are a data analyst for a company, and you have access to a dataframe containing detailed information about employee timesheets. This dataframe includes data such as task names, descriptions, work hours, and other relevant details.

Your role is to respond to questions from the company's managers regarding the data in this timesheet dataframe. When answering their questions, provide only the final result or answer—there's no need to explain the process, calculations, or steps you used to arrive at that result.

Focus on delivering precise, accurate answers directly based on the data, ensuring that your responses are concise and to the point.
"""

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_template), ("user", "{input}")]
    )

    return prompt

def get_chat_agent(df):
    llm = ChatBedrock(model_id='anthropic.claude-v2:1', client=bedrock_client)

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        prompt=get_chat_prompt(),
        verbose=True,
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )

    return agent

def get_chat_answer(df, question):
    agent = get_chat_agent(df)

    try:
        answer = agent.invoke({'input': question})['output']
    except ValueError as e:
        answer = str(e)
        prefix1 = 'An output parsing error occurred. In order to pass this error back to the agent and have it try again, pass `handle_parsing_errors=True` to the AgentExecutor. This is the error:'
        prefix2 = 'Could not parse LLM output: `'
        if not answer.startswith(prefix1) and not answer.startswith(prefix2):
            raise e
        answer = answer.removeprefix(prefix1).strip()
        answer = answer.removeprefix(prefix2).removesuffix('`').strip()
    except:
        answer = 'Please ask me a simpler question 😔'

    return answer

def get_agent(df):
    tools, rendered_tools = get_tools()
    system_prompt = get_system_prompt(rendered_tools)

    llm = BedrockLLM(model_id='anthropic.claude-v2:1', client=bedrock_client)
    
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        prompt=system_prompt,
        extra_tools=tools,
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )

    return agent

def get_tools():
    python_repl = PythonREPL()

    repl_tool = Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
        func=python_repl.run,
    )

    tools = [repl_tool]
    rendered_tools = render_text_description(tools)
    return tools, rendered_tools

def get_additional_functions():
    additional_functions = """
def date_calculator(start_date: str, end_date: str)->int:
    from datetime import datetime
    start_date_object = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_object = datetime.strptime(end_date, '%Y-%m-%d').date()
    duration = end_date_object - start_date_object
    return duration.days
    
def today() -> str:
    from datetime import datetime
    return datetime.today().strftime('%Y-%m-%d')
    """
    return additional_functions

def get_system_prompt(rendered_tools):
    additional_functions = get_additional_functions()

    prompt_template = """You are a data analyst for a company that has access to the following set of tools. Here are the names and descriptions for each tool:

    {rendered_tools}

    For the python_repl tool, you can utilize this additional function by declaring it in the repl if necessary: {additional_functions}
    
    Your manager will provide you with instructions containing the data needed for the task, the task itself, and specific guidelines to follow, presented in bullet points.
    Use the provided data effectively to complete the task thoroughly, ensuring that every point in the guidelines is followed. 
    **Output the result in string format.**
    
    
    Manager's Instructions: {input_prompt}
    
    Result:"""

    # system_prompt = """You are a data analyst for a company. Your manager will provide you with instructions containing the data needed for the task, the task itself, and specific guidelines to follow, presented in bullet points. Use the provided data effectively to complete the task thoroughly, ensuring that every point in the guidelines is followed. **Output the result in string format.**"""

    # PREFIX = prompt_template

    # prompt = ChatPromptTemplate.from_messages(
    #     [("system", system_prompt), ("user", "{input}")]
    # )

    system_prompt = PromptTemplate(template=prompt_template, input_variables=['rendered_tools', 'additional_functions', 'input_prompt'])

    return system_prompt

def desc_sentence(items: tuple):
    return f'- {items[0]} ({items[1]} hours)'

def get_input_prompt(df: pd.DataFrame, task_name: str, total_work_hours: float, type: str):
    desc_list = list(zip(df.description, df.work_hours))
    descriptions = '\n'.join(desc_sentence(items) for items in desc_list)

    if type == 'dept':
        prompt = f"""You are a manager reviewing your department's timesheet. Each entry in the timesheet includes a task name, description, and work hours. Your goal is to summarize what your employees have accomplished for a particular task.

You have grouped the timesheet entries by task name and extracted the relevant descriptions. The task you selected is: {task_name}

The total work hours for this task is: {total_work_hours}

Here are the descriptions for this task:

{descriptions}

**TASK:**
Provide a summary in paragraph format detailing what activities has been done for this task. The summary must contain at least 80 words.
Use the task name, descriptions, and work hours as the foundation for your summary, and include any additional insights gained from analyzing the data.
Output only the summary text itself, without any introductory or concluding phrases.

**GUIDELINES:**
- Consider the work hours associated with each description to identify the most time-consuming or significant tasks, and assess whether any difficulties were encountered (e.g., if a particular activity took longer than expected).
- Do not explicitly mention the time spent on each activity, but implicitly emphasize the activities that consume the most time.
- Maintain a professional tone, avoiding phrases like "my employees" and references to stakeholders or individuals outside the department.
- Ensure the summary is in paragraph format (no bullet points) and contains at least 80 words.
- If you do not have access to the dataframe, use only the descriptions provided above.
- **Output only the summary text itself, without any introductory or concluding phrases, in the string format.**
"""
    
    else:
        prompt = f"""You are a manager reviewing an employee's timesheet. Each entry in the timesheet includes a task name, description, and work hours. Your goal is to summarize what this employee has accomplished for a particular task.

You have grouped the timesheet entries by task name and extracted the relevant descriptions. The task you selected is: {task_name}

The total work hours for this task is: {total_work_hours}

Here are the descriptions for this task:

{descriptions}

**TASK:**
Provide a summary in paragraph format detailing what activities this employee has completed for this task. The summary must contain at least 80 words.
Use the task name, descriptions, and work hours as the foundation for your summary, and include any additional insights gained from analyzing the data.
Output only the summary text itself, without any introductory or concluding phrases.

**GUIDELINES:**
- Consider the work hours associated with each description to identify the most time-consuming or significant tasks, and assess whether any difficulties were encountered (e.g., if a particular activity took longer than expected).
- Do not explicitly mention the time spent on each activity, but implicitly emphasize the activities that consumed the most time.
- Maintain a professional tone, avoiding phrases like "my employee" and references to stakeholders or individuals outside the department.
- Ensure the summary is in paragraph format (no bullet points) and contains at least 80 words.
- If you do not have access to the dataframe, use only the descriptions provided above.
- **Output only the summary text itself, without any introductory or concluding phrases, in the string format.**
"""
    
    return prompt

def task_summary(df, task_name, type):
    total_work_hours = df.loc[df.task_name == task_name, 'work_hours'].sum()
    df = create_df_tasksum(df, task_name)

    if df.shape[0] == 0:
        return 'No description logged for this task.'

    input_prompt = get_input_prompt(df, task_name, total_work_hours, type=type)
    agent = get_agent(df)

    try:
        answer = agent.invoke({'input': input_prompt})['output']
    except ValueError as e:
        answer = str(e)
        prefix1 = 'An output parsing error occurred. In order to pass this error back to the agent and have it try again, pass `handle_parsing_errors=True` to the AgentExecutor. This is the error:'
        prefix2 = 'Could not parse LLM output: `'
        if not answer.startswith(prefix1) and not answer.startswith(prefix2):
            raise e
        answer = answer.removeprefix(prefix1).strip()
        answer = answer.removeprefix(prefix2).removesuffix('`').strip()
    
    return answer
