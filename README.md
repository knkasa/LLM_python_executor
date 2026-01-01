# 🚀 Code Interpreter with AWS ECS

A lightweight **LLM execution pipeline** built entirely on **AWS managed services**.  
User prompts are sent through an API endpoint, processed serverlessly, and executed inside a scalable ECS Fargate container.

---

## ✨ Overview

This project demonstrates how to:

- Accept user prompts via **API Gateway**
- Orchestrate execution with **AWS Lambda**
- Run arbitrary code or LLM-based tasks on **ECS Fargate**
- Query and reason over **Amazon Redshift** tables using an LLM deployed on **Amazon Bedrock**

The LLM understands the database schema and can:
- Answer analytical questions about the data
- Generate SQL queries
- Build and execute machine learning models from the tables

---

## 🗄️ Data Sources

There are two tables stored in **Amazon Redshift** (see `/input`):

- **`users`**
- **`interactions`**

The LLM agent is aware of these schemas and can reason over them directly.

---

## 🧩 Architecture

```mermaid
flowchart TD
    Client -->|POST /prompt| APIGW[API Gateway<br/>HTTP API]
    APIGW --> Lambda[AWS Lambda]
    Lambda --> ECS[ECS Fargate Task]
    ECS --> LLM[LLM / Program Execution]

---

## Components
### API Gateway - HTTP API - Endpoint: POST /prompt - Accepts JSON input Example request:
json
{
  "prompt": "Please make a machine learning model from 'interaction' table."
}

