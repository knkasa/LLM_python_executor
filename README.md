# Code interpreter with AWS ECS.
This code implements a simple LLM execution pipeline using AWS managed services.
User prompts are sent via API Gateway, processed by AWS Lambda, and executed inside an ECS Fargate container.

---

## Architecture

```mermaid
flowchart TD
    Client -->|POST /prompt| APIGW[API Gateway (HTTP API)]
    APIGW --> Lambda[AWS Lambda]
    Lambda --> ECS[ECS Fargate Task]
    ECS --> LLM[LLM / Program Execution]

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
