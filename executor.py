import os
import boto3
import json
import subprocess
import sys
import pdb
from bs4 import BeautifulSoup
import pandas as pd
import redshift_connector

class program_execution_class:
    def __init__(self):
        session = boto3.Session()
        bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        user_prompt = "Calculates and displays the first 10 prime numbers"
        
        success, final_code, final_requirements, attempts_used = self.auto_fix_and_execute(
            bedrock_client, 
            user_prompt, 
            max_attempts=5
            )
        
    def auto_fix_and_execute(self, bedrock_client, user_prompt, max_attempts=5):
        """Automatically generate, execute, and fix code until it succeeds."""

        print(f"🚀 Starting auto-fix execution for: {user_prompt}.")
        system_prompt = self.initial_prompt(user_prompt)
        
        # Try executing in loops
        for attempt in range(1, max_attempts + 1):
            print(f"Attempt {attempt}/{max_attempts}")
            print("-" * 40)
            
            try:
                # Initial attempt
                response = self.invoke_bedrock_model(bedrock_client, system_prompt)            
                python_code, requirements = self.extract_python_code(response)
                success, stdout, stderr = self.save_and_execute_script(python_code, requirements)
                
                if success:
                    return True, python_code, requirements, attempt
                
                # If failed, get another prompt, keep trying.
                if attempt < max_attempts:
                    print(f"Preparing to fix errors for attempt {attempt + 1}...")
                    error_info = f"STDOUT: {stdout}\nSTDERR: {stderr}"
                    system_prompt = self.create_fix_prompt(
                        user_prompt, 
                        python_code, 
                        error_info, 
                        )
                
            except Exception as e:
                print(f"Unexpected error in attempt {attempt}: {e}")
                if attempt == max_attempts:
                    break
                continue
        
        print(f"FAILED: Could not generate working code after {max_attempts} attempts")
        return False, None, None, max_attempts

    def invoke_bedrock_model(self, bedrock_client, system_prompt, max_tokens=5000):

        session = boto3.Session()
        bedrock_client = session.client('bedrock-runtime', region_name='us-east-1')
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": "Please generate the code as requested."
                }
            ]
        }
        
        response_raw = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json",
            )
        
        response = json.loads(response_raw['body'].read())['content'][0]['text']
        return response

    def extract_python_code(self, text):
        """Extract Python code from Claude's response."""

        soup = BeautifulSoup(text, 'html.parser')
        code_tag = soup.find('python_code')
        requirements_tag = soup.find('requirements')
        
        code = code_tag.string
        requirements = requirements_tag.string
        
        return code, requirements

    def save_and_execute_script(self, code, requirements):
        """Save the generated code to a file and execute it."""
        try:
            python_file_name = "generated_script.py"
            requirement_file_name = "requirements.txt"
            
            with open(python_file_name, 'w') as f:
                f.write(code)
            print(f"Script saved as: {python_file_name}")

            with open(requirement_file_name, 'w') as f:
                f.write(requirements)
            print(f"Requirements saved as: {requirement_file_name}")
            
            if requirements.strip():
                print("Installing necessary libraries...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", requirement_file_name]
                )

            print("Generated script executing...")
            result = subprocess.run(
                [sys.executable, python_file_name],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
                )

            if result.stdout:
                print("Script Output:")
                print(result.stdout)
            if result.stderr:
                print("Script Errors:")
                print(result.stderr)

            print(f"{'='*60}")
            if result.returncode == 0:
                print("Script executed successfully!")
                return True, result.stdout, result.stderr
            else:
                print(f"Script failed with exit code: {result.returncode}")
                return False, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            print("Script execution timed out (30 seconds)")
            return False, "", "Script execution timed out"
        except KeyboardInterrupt:
            print("Execution interrupted by user")
            return False, "", "Execution interrupted by user"
        except Exception as e:
            print(f"Error executing script: {e}")
            return False, "", str(e)

    def initial_prompt(self, user_prompt):
        return f"""
Create a Python script that {user_prompt}.

Requirements:
- Follow the template below to provide the python code
- Also provide libraries to install in requirements.txt using the template below
- Make the code complete and executable
- Use standard Python libraries when possible

<python_code>
import ...
</python_code>

<requirements>
numpy
</requirements>
"""

    def create_fix_prompt(self, original_prompt, code, error_output):
        """Create a prompt to fix the failing code."""
        return f"""
The following Python code failed to execute properly. Please fix the issues and provide corrected code.

Original request: {original_prompt}

<python_code>
{code}
</python_code>

Error output:
{error_output}

Requirements:
- Fix all the errors shown above
- Follow the template below to provide the corrected python code
- Also provide libraries to install in requirements.txt using the template below

<python_code>
import ...
</python_code>

<requirements>
numpy
</requirements>
"""

def main():

    conn = redshift_connector.connect(
        # <workgroup-name>.<account-id>.<region>.redshift-serverless.amazonaws.com
        host='llm-executor-db.533267358966.us-east-1.redshift-serverless.amazonaws.com',
        database='dev',
        user=os.getenv('REDSHIFT_USER'),
        password=os.getenv('REDSHIFT_PASSWORD'),
        port=5439  # Default Redshift port
        )
    
    sql = "SELECT * FROM passenger_gender"
    df = pd.read_sql(sql, conn)
    conn.close()
    print(df.head())
    exit()

    program_execution_class()
    
if __name__ == "__main__":
    main()
