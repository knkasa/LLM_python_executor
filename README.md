# Code interpreter with AWS ECS.
This code implements a simple LLM execution pipeline using AWS managed services.
User prompts are sent via API Gateway, processed by AWS Lambda, and executed inside an ECS Fargate container.

---

## Architecture
Client
|
| POST /prompt
v
API Gateway (HTTP API)
|
v
AWS Lambda
|
v
ECS Fargate Task
|
v
LLM / Program Execution


---

## Components

### API Gateway
- HTTP API
- Endpoint: `POST /prompt`
- Accepts JSON input

Example request:
```json
{
  "prompt": "Which columns are float in the interaction table?"
}

.
├── dockerfile
├── main.py
├── interpreter.py
├── creator.py
├── requirements.txt
└── README.md
