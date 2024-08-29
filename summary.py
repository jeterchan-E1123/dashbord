import pandas as pd
import boto3
import os

from dotenv import load_dotenv
from langchain_aws import BedrockLLM
from langchain.agents import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor


load_dotenv()

# 1. load LLM
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name = os.getenv('AWS_DEFAULT_REGION'),
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
)

llm = BedrockLLM(model_id='anthropic.claude-v2:1', model_kwargs={"temperature": 0}, client=bedrock_client)

# 2. define tool
@tool
def save_to_csv(df):
    """Save dataframe to csv file"""
    df.to_csv("task_analysis.csv",index=False)
    
tools = [save_to_csv, ]

# 3. define prompt
template = """
    You are an expert in data analyzing.
    You need to judge the relation weight between 'task_name' and 'description' columns.
    Return the relation weight between 0 to 1, you can return by float type.
    
    0 means this 'description' does not have any relation to 'task_name'.
    1 means this 'description' has strongly relation to 'task_name'.
    You can also return 0.5 for relation weight, it means you think this 'description' is obscure.
    
    -Input type-
    Input will be a dataframe, you need to analyze every task and return relation weight between 'task_name' and 'description' columns.
    
    
    -Examples-
    Here is the example:
    if 'task_name' is "[HRM-2246] [Develop] HRM：測試環境加 KPI 上傳功能 [CRS]" and "description" is "開發 HRM 設定電腦環境",
    You should output the relationship weight close to 1, because 'task_name' has HRM keywords, and 'description' also has HRM keyword.
    However, only check the keyword is not a accurate way to judge relation between 'task_name' and 'description'.
    For example, task_name="[HRM-2172] [Develop] ARDue：AR 主動回饋 Nebula API", description="研究程式碼" , API is a conception and "程式碼" means code in Chinese Language.
    So, in this case, you should return higher than 0.5, it can be 0.6, 0.7, or higher.
    Being aware of 'task_name' and 'description' may contain Chinese and English.
    
    -Query-
    I will give you a dataframe, you need to analyze this data and return the relation weight between "task_name" and "description".
    Also, new a column which name is 'weight', and add relation weight to this column.
    return the whole dataframe for me.
    Here is input dataframe {dataframe}
    
"""

prompt = PromptTemplate(input_variables=["dataframe"],template=template)

# print(prompt.format(task_name="[HRM-2355] [Develop] Webhook issue",description="[HRM-2355] [Develop] Webhook issue"))

# llm_chain = LLMChain(prompt = prompt, llm=llm)

# set dataframe
df = get_df_all()
df_description = df.loc[df.description != ''].dropna()
df_final = df_description[['task_name','user_id','description']]
df_final['description'] = df_final['description'].str.replace(r'<[^<>]*>', '', regex=True)
# print(df_description.head())

chain = prompt | llm
print(chain.invoke({'dataframe':df_final}))
# chain.get_graph().print_ascii()


# my_dict = llm_chain.run({"dataframe":df_description})
# print(my_dict)

# 4. build agent




# 5. build agent 
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)