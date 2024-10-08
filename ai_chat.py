import pandas as pd
import boto3
from dotenv import load_dotenv

from langchain_aws import BedrockLLM, ChatBedrock
from langchain.agents import tool, Tool, AgentExecutor, create_tool_calling_agent
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_experimental.utilities import PythonREPL
from langchain.tools.render import render_text_description
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel

load_dotenv()

bedrock_client = boto3.client(service_name="bedrock-runtime")

def get_repl_functions():
    repl_func = """
def get_date():
    '''Get today's date in the string format yyyy-mm-dd. No input parameter necessary.'''
    from datetime import datetime
    return datetime.today().strftime('%Y-%m-%d')
"""
    return repl_func

@tool
def get_date():
    """Get today's date in the string format yyyy-mm-dd. No input parameter necessary."""
    from datetime import datetime
    return datetime.today().strftime('%Y-%m-%d')

def get_chat_tools(df):
    python_repl = PythonREPL()

    repl_tool = Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
        func=python_repl.run,
    )

    tools = [get_date]
    rendered_tools = render_text_description(tools)
    return tools, rendered_tools

def get_chat_prompt(df, rendered_tools):
    repl_functions = get_repl_functions()

    prompt_template = """You are a data analyst for a company, and you have access to a dataframe containing detailed information about employee timesheets. This dataframe includes data such as task names, descriptions, work hours, and other relevant details.

Here is the dataframe: {df}

Your role is to respond to questions from the company's managers regarding the data in this timesheet dataframe.
You answer should consist of only the answer to the question. **You do not need to explain the process, calculations, or steps you used to arrive at that answer.**

You have access to the following tools to assist in your analysis: {rendered_tools}

Focus on delivering precise, accurate answers directly based on the data, ensuring that your responses are concise and to the point.
"""
# for the python_repl_ast tool, you can utilize this additional function by declaring it in the repl if necessary: {repl_functions}

    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_template), ("user", "{input}")]
    )

    PREFIX = prompt_template

    return prompt, PREFIX

def get_chat_agent(df):
    tools, rendered_tools = get_chat_tools(df)
    prompt, PREFIX = get_chat_prompt(df, rendered_tools)
    llm = ChatBedrock(model_id='anthropic.claude-v2:1', client=bedrock_client, model_kwargs=dict(temperature=0))

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        prompt=prompt,
        prefix=PREFIX,
        extra_tools=tools,
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )

    return agent

def get_chat_answer(df, question):
    agent = get_chat_agent(df)
    _, rendered_tools = get_chat_tools(df)

    try:
        answer = agent.invoke({'input': question, 'df': df, 'rendered_tools': rendered_tools})['output']
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