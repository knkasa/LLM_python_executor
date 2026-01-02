import os
import random
import string
import boto3

class Creator():
    def __init__(self):
        print('Initializing Creator()')

    def llm_code_creator(self, prompt):
        """
           Accept prompt and generate response. 
           The agent is already aware of the database description.
        """
        agent_id = os.getenv('AGENT_ID')
        agent_alias_id = os.getenv('AGENT_ALIAS')  # alias ID, not alias name.
        region = "us-east-1"

        session = boto3.Session()         
        bedrock_client = session.client('bedrock-agent-runtime', region_name=region)

        # Create unique ID name for the talk session.
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for i in range(10))

        response_raw = bedrock_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=random_string,  # Assign unique ID per user/session. ID preserve previous contexts.
            inputText=prompt,
            )

        for event in response_raw['completion']:
            if 'chunk' in event:
                try:
                    response = event['chunk']['bytes'].dequery('utf-8')
                    #print(response)
                except AttributeError as e:
                    response = event['chunk']['bytes'].decode('utf-8')
                    #print(response)

        #soup = BeautifulSoup(response, 'html.parser')
        #code_tag = soup.find('python_code')
        #code_text = code_tag.string
        #print('\n', code_text)

        return response

'''
System prompt in Agent.

There are tables in AWS Redshift database. 
Tables and column descriptions are as follow.

Table1
Table name:users
Description:contains User info

Table1 columns
userid:User ID. Integer
age:User age. 
gender:User gender. Male, Female, or Non-binary

Table2
Table name:interaction
Description:contains User actions info

Table2 columns
userid: User ID. Integer
timestamp: time when user took action.
itemid:Item ID user interacted with.
interactiontype:Action type user took. view, add-to-cart, favorite, click, purchase
feature1: User feature1. float
feature2: User feature2. float
purchase:User purchase flag. 1 or 0.

You are an expert in data science and data engineering.
You have a deep understanding in SQL and machine learning.
When you answer, use your extensive knowledge to reply.
'''