# LLM API Console

## The Problem

APIs are powerful but intimidating. Even experienced developers spend time reading documentation, figuring out the right endpoint, constructing the correct parameters, and interpreting JSON responses. For less technical stakeholders — product managers, analysts, support teams — APIs are essentially inaccessible without engineering help.

This tool bridges that gap. You describe what you want in plain English, and the LLM figures out the correct API call, executes it, and explains the response back to you in plain English.

---

## Why I Built This

I built this as a portfolio project to simulate the kind of developer tooling a platform PM at Stripe, Plaid, or Twilio would champion internally. The goal was to demonstrate:

- **Context engineering** — designing prompts that reliably translate natural language into structured API calls
- **LLM tool use** — using GPT not just for text generation but as a reasoning layer over real external systems
- **Developer experience thinking** — reducing the cognitive load of API interaction for both technical and non-technical users
- **Production-ready architecture** — CLI for developers, FastAPI layer for integration into dashboards or internal tools

This project directly maps to the AI PM skill of understanding how LLMs can augment developer workflows, not just generate content.

---

## How It Works

1. User types a natural language request — e.g. "create a customer named John Doe"
2. interpreter.py builds a structured prompt and sends it to GPT-4o-mini
3. GPT returns a JSON object with method, endpoint, params, and a description
4. api_executor.py takes that JSON and fires the real HTTP request to the Stripe API
5. The response comes back from Stripe and is sent back to GPT for plain-English explanation
6. history.py logs the full request and response to SQLite
7. cli.py or api.py delivers the output to the user

---

## Project Structure and File Explanations

**src/llm_client.py** — OpenAI API wrapper. Accepts a prompt and system message and returns a completion. Isolated so you can swap GPT for any other model without touching other files.

**src/interpreter.py** — The brain of the project. Contains two functions: generate_api_request takes natural language and returns a structured Stripe API call as JSON. explain_response takes a Stripe response and returns a plain-English explanation.

**src/api_executor.py** — Takes the structured request from the interpreter and fires the actual HTTP request to Stripe using the requests library. Handles both GET and POST methods with proper auth headers.

**src/history.py** — Logs every request and response to a local SQLite database. Supports retrieval of the last N requests for the history view.

**src/cli.py** — Interactive terminal interface. Accepts natural language input in a loop, processes it through the full pipeline, and prints the explanation and raw response. Supports 'history' and 'exit' commands.

**src/api.py** — FastAPI REST API with three endpoints: /health, /query (POST), and /history (GET). Makes the console consumable by dashboards, Slack bots, or other internal tools.

**data/request_history.db** — SQLite database storing all request history.

---

## Quickstart (Local)

**1. Clone and set up environment**

```bash
git clone https://github.com/VarunNair2403/llm-api-console.git
cd llm-api-console
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv requests fastapi uvicorn stripe
```

**2. Add your API keys**

Create a .env file in the project root:

```env
OPENAI_API_KEY=sk-...
STRIPE_API_KEY=sk_test_...
```

**3. Run via CLI**

```bash
python -m src.cli
```

Example inputs:
- list my last 5 customers
- create a customer named Jane Smith with email jane@example.com
- show me all my products
- history
- exit

**4. Run via API**

```bash
uvicorn src.api:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive Swagger UI.

---

## API Endpoints

- GET /health — Service liveness check
- POST /query — Submit a natural language request, returns generated API call, Stripe response, and plain-English explanation
- GET /history?limit=10 — Returns the last N logged requests with explanations

---

## Example

Input: "create a customer named John Doe with email john@example.com"

Generated request:
- Method: POST
- Endpoint: /v1/customers
- Params: name=John Doe, email=john@example.com

Stripe response: Customer object with id cus_xyz, name John Doe, email john@example.com, balance 0, livemode false

Explanation: The Stripe API successfully created a customer named John Doe. The most important field is the id which uniquely identifies this customer. The livemode field is false confirming this is a test mode transaction.

---

## Taking This to Production

- **Target APIs** — extend beyond Stripe to support Plaid, Twilio, or internal APIs via a configurable API registry
- **Auth** — add OAuth2 so each user only sees their own Stripe account data
- **Database** — replace SQLite with PostgreSQL for multi-user history
- **Hosting** — Dockerize and deploy on AWS ECS or Cloud Run
- **Secrets** — move API keys to AWS Secrets Manager or Azure Key Vault
- **Safety layer** — add a confirmation step before executing POST, PUT, or DELETE requests to prevent accidental mutations
- **Multi-API support** — use MCP (Model Context Protocol) to let the LLM discover and call any registered API dynamically
- **Fine-tuning** — fine-tune on Stripe API documentation to improve request generation accuracy

---

## Tech Stack

- Python 3.7+
- SQLite — request history storage
- OpenAI GPT-4o-mini — request generation and response explanation
- Stripe API — target API (test mode)
- FastAPI + Uvicorn — REST API layer
- python-dotenv — environment config
- requests — HTTP client for Stripe calls