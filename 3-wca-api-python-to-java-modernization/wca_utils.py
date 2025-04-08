import os
from github import Github
import json
import requests
import base64
import uuid
import time
from pathlib import Path

# WCA api URL (ENV BASE_URL overrides the default value)
DEFAULT_BASE_URL = "https://api.dataplatform.cloud.ibm.com/v2/wca/core/chat/text/generation"

#IBM IAM URL - to get a token for an APIKEY
DEFAULT_IBM_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

iam_apikey = os.environ.get("WCA_API_KEY")  # Loading WCA API KEY from .env

def get_bearer_token(apikey=None):
    """
    Returns a bearer token for authentication with IBM Cloud services.
    Uses the apikey specified in the IAM_APIKEY environment property

    Args:
        The apikey=None: The apikey to use for authentication. If not provided, the value of the IAM_APIKEY environment variable is used.

    Returns:
        str: The bearer token
        
    Throws an exception if the bearer cannot be obtained
    """
    if not apikey:
        apikey =  iam_apikey #os.getenv(IAM_APIKEY_ENV_PROPERTY)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'urn:ibm:params:oauth:grant-type:apikey', 'apikey':apikey}
    response = requests.post(DEFAULT_IBM_IAM_URL, headers=headers, data=data, timeout=30)
    if not response.ok:
        raise Exception(f'Status code: {response.status_code}, Error: {json.loads(response.content)}')
    return response.json()['access_token']

def call_wca_url( payload, file_dict=[], url=os.getenv("BASE_URL", DEFAULT_BASE_URL), request_id=str(uuid.uuid4()), apikey=None):
    """
    Call the Watson Code Assistant API to get a code completion response.

    Parameters:
    - prompt: The code prompt to send to the API.
    - url: The URL of the Watson Code Assistant API. Defaults to the value of the BASE_URL environment variable, or to a default URL if the environment variable is not set.
    - request_id: A unique identifier for the request. Defaults to a randomly generated UUID.
    - apikey: the APIKEY used to authenticate against the url.

    Returns:
    A JSON object containing the code completion response from the API.

    Raises:
    - If the request to the API fails, raises a requests.exceptions.RequestException exception.
    """
    headers = {
        'Authorization': f'Bearer {get_bearer_token(apikey)}',
        'Request-Id': request_id,
        'Origin': 'vscode'
    }

    files = []
    files.append(('message', (None, json.dumps(payload))))
    for a_file in file_dict:
        file_name = a_file.split("/")[-1]
        with open(a_file, 'rb') as file:
            encoded_content = base64.b64encode(file.read()).decode('utf-8')
        files.append(('files', (file_name, encoded_content, 'text/plain')))
    response = requests.post(
        url=url, 
        headers=headers,
        files=files,
        timeout=180
    )
    if not response.ok:
        handle_error(response=response.content,payload=payload,url=url,request_id=request_id)
        response.raise_for_status()
    return response.json()

# Assisted by WCA@IBM
# Latest GenAI contribution: ibm/granite-8b-code-instruct
def handle_error(response, payload, url, request_id):
    """
    Print an error message to stderr.

    Parameters:
    - response (bytes): The response from the API call.
    - payload (dict): The payload from the API call.
    - url (str): The URL of the API call.
    """
    try:
        response_json = json.loads(response.decode('utf-8'))
        print(response_json)
        print(f"Error response from {url}: {request_id}", file=sys.stderr)
        print(f"Payload: {json.dumps(payload, indent=2)}", file=sys.stderr)
        for detail in response_json['detail']:
            print(f"Location: {', '.join(detail['loc'])}", file=sys.stderr)
            print(f"Message: {detail['msg']}", file=sys.stderr)
            print(f"Type: {detail['type']}", file=sys.stderr)
    except Exception as e:
        print(f"Error parsing response: {e}", file=sys.stderr)

# Assisted by WCA@IBM
# Latest GenAI contribution: ibm/granite-8b-code-instruct



def encode_base64(payload):
    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    return payload_base64


def build_basic_prompt_paylod(text):
    payload = {
        "message_payload": {
            "messages": [{"content":text, "role": "USER"}],
        }
    }
    return encode_base64(payload)


def read_file(file_path: Path) -> str:
    """Read and return contents of file"""
    try:
        return file_path.read_text()
    except Exception as e:
        print(f"[red]Error reading file: {e}[/red]")


def analyze_requirements(spec: str) -> dict:
    """Analyze the specification to determine what needs to be generated"""
    analysis_prompt = f"""Analyze this technical specification and identify required components.
Categorize into:
1. Frontend Components (if any)
2. Backend Services
3. Infrastructure Requirements

Return the analysis in a structured format:

<<SYS>>
specification: ```markdown
{spec}
```
<</SYS>>

Return a JSON structure like:
```json
{{
    "frontend": {{
        "framework": "",
        "pages": []
    }},
    "backend": {{
        "api-endpoints": [
            {{
                "api-endpoint": "endpoint name",
                "api-endpoint-details": "details what this endpoint does"
            }},
            {{
                "api-endpoint": "endpoint name",
                "api-endpoint-details": "details what this endpoint does"
            }},
            {{
                "api-endpoint": "endpoint name",
                "api-endpoint-details": "details what this endpoint does"
            }} .. and so on
        ]
    }}
}}
```"""
    try:
        payload = {
            "message_payload": {
                "messages": [{"content": analysis_prompt, "role": "USER"}]
            }
        }
        response = call_wca_url(payload)

        return response
    except Exception as e:
        print(f"[red]Error analyzing requirements: {str(e)}[/red]")
        return {}
    


def generate_backend_code(spec: str, backend_specs=str) -> dict:
    backend_prompt = f"""Generate python backend code using Fast API for the following endpoints:
<<SYS>>
backend endpoints: {backend_specs}
<</SYS>>

Be very detail in generating the python Fast API code, and make sure you generate each endpoint and detailed logic for each endpoint.
"""
    try:
        payload = {
            "message_payload": {
                "messages": [{"content": backend_prompt, "role": "USER"}]
            }
        }
        response = call_wca_url(payload)

        return response
    except Exception as e:
        print(f"[red]Error analyzing requirements: {str(e)}[/red]")
        return {}
    


def generate_frontend_code(spec: str, front_end_specs: str, front_end_framework: str, back_end_points: str) -> dict:
    front_end_prompt = f"""Generate detailed {front_end_framework} code for the following components:

<<SYS>>
front end components: 
```
{front_end_specs}
```
which should conform with the business requirements
```
{spec}
```
corresponding backend endpoints are:
```
{back_end_points}
```
<</SYS>>

Make sure you generate a detailed {front_end_framework} code that conforms with the business requirements and the backend logic.
"""
    try:
        payload = {
            "message_payload": {
                "messages": [{"content": front_end_prompt, "role": "USER"}]
            }
        }
        response = call_wca_url(payload)

        return response
    except Exception as e:
        print(f"[red]Error analyzing requirements: {str(e)}[/red]")
        return {}
