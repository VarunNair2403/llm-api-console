# PRD: LLM API Console

**Author:** Varun Nair
**Status:** v1.0 — Complete
**Last Updated:** March 2026

---

## Problem Statement

APIs power modern fintech infrastructure — Stripe processes payments, Plaid connects bank accounts, Twilio sends notifications. But interacting with these APIs requires technical knowledge: knowing the right endpoint, constructing valid parameters, understanding JSON responses, and interpreting error codes.

This creates two problems:

1. **Developer friction** — even experienced engineers spend time context-switching between documentation and their terminal to form and debug API calls
2. **Non-technical exclusion** — product managers, analysts, support teams, and business stakeholders cannot interact with APIs directly, creating bottlenecks and dependency on engineering

There is no tool today that lets you describe what you want in plain English, executes the correct API call, and explains the result back to you — the way a senior engineer who has memorized the Stripe docs would.

---

## Target Users

- **Platform developers** — want to explore and debug API endpoints faster without constantly referencing documentation
- **Developer advocates** — need to demo API capabilities to non-technical audiences
- **Product managers** — want to query production or test data directly without filing tickets to engineering
- **Support engineers** — need to look up customer or transaction data quickly during incident response
- **Internal tooling teams** — want to expose API capabilities to business stakeholders via a natural language interface

---

## Goals

**Primary Goals**
- Translate natural language requests into valid, executable Stripe API calls using an LLM
- Execute those calls against the real Stripe API and return structured responses
- Explain API responses in plain English so non-technical users can understand the output
- Log all requests and responses for auditability and debugging

**Secondary Goals**
- Expose the console as a REST API so it can be embedded in dashboards or internal tools
- Demonstrate a production-ready architecture pattern for LLM-augmented developer tooling

**Non-Goals for v1**
- Support for APIs beyond Stripe
- User authentication or multi-user access control
- Write operation safety guardrails (confirmation before POST/DELETE)
- Fine-tuning on Stripe documentation
- Real-time streaming responses

---

## Success Metrics

- **Request accuracy** — LLM generates the correct Stripe endpoint and parameters for common natural language inputs
- **Response clarity** — plain-English explanations correctly identify the most important fields in the response
- **Execution reliability** — API executor correctly handles both GET and POST requests with proper auth
- **History completeness** — every request and response is logged to SQLite with no data loss
- **API response time** — /query endpoint returns in under 5 seconds including LLM calls

---

## Scope — What Is In v1

- Natural language to Stripe API request generation via GPT-4o-mini
- Support for GET and POST HTTP methods
- Real Stripe API execution in test mode
- Plain-English response explanation via LLM
- Request and response history logging to SQLite
- CLI with interactive loop, history view, and exit command
- FastAPI REST API with /health, /query, and /history endpoints
- Swagger UI auto-documentation

## Scope — What Is Out of v1

- Support for APIs beyond Stripe
- PUT, PATCH, and DELETE method support
- Confirmation step before mutating API calls
- User authentication and per-user history isolation
- Fine-tuning on Stripe API documentation
- Streaming responses for long-running queries
- Frontend UI

---

## Feature Breakdown

**1. Natural Language to API Request (interpreter.py)**
Uses a carefully engineered system prompt to instruct GPT-4o-mini to act as a Stripe API expert. Given a plain-English input, the model returns a structured JSON object containing the HTTP method, endpoint path, query or body parameters, and a one-sentence description of what the call does.

**2. API Execution (api_executor.py)**
Takes the structured request from the interpreter and fires the actual HTTP request to the Stripe API using the requests library. Handles GET requests with query params and POST requests with form-encoded body params. Attaches the Stripe secret key as a Bearer token in the Authorization header.

**3. Response Explanation (interpreter.py)**
Sends the raw Stripe API response back to GPT with a second prompt instructing it to explain the response in 2-3 plain-English sentences, highlighting the most important fields and what they indicate.

**4. History Logging (history.py)**
Logs every request and response to a local SQLite database with timestamp, user input, generated method and endpoint, params, raw response, and plain-English explanation. Supports retrieval of the last N records.

**5. CLI (cli.py)**
Interactive terminal interface with a continuous input loop. Accepts natural language queries, processes them through the full pipeline, and prints both the explanation and raw response. Supports special commands: history to view past requests and exit to quit.

**6. REST API (api.py)**
Three endpoints via FastAPI. GET /health for liveness. POST /query accepts a natural language input and returns the generated request, Stripe response, and explanation. GET /history returns the last N logged requests.

---

## Technical Architecture

Data flows in one direction:

User input → interpreter.py → GPT-4o-mini → structured JSON request → api_executor.py → Stripe API → raw response → interpreter.py → GPT-4o-mini → plain-English explanation → history.py → SQLite → cli.py or api.py → output

Stack: Python 3.7+, SQLite, OpenAI GPT-4o-mini, Stripe API, FastAPI, Uvicorn, python-dotenv, requests

---

## Production Roadmap

- **Multi-API support** — extend to Plaid, Twilio, and internal APIs via a configurable API registry; use MCP (Model Context Protocol) for dynamic tool discovery
- **Safety layer** — add a confirmation step before executing any POST, PUT, or DELETE request to prevent accidental data mutations
- **Auth** — add OAuth2 so each user only accesses their own API credentials and history
- **Database** — replace SQLite with PostgreSQL for multi-user concurrent access
- **Fine-tuning** — fine-tune a model on Stripe API documentation and common developer queries to improve accuracy
- **Hosting** — Dockerize and deploy on AWS ECS or Cloud Run
- **Secrets** — move API keys to AWS Secrets Manager or Azure Key Vault
- **Audit trail** — extend history logging to include user identity, IP address, and outcome for compliance purposes
- **Rate limiting** — add per-user rate limiting on the /query endpoint to control LLM costs
- **Evals** — build an evaluation suite to measure request generation accuracy across a benchmark set of natural language inputs

---

## Open Questions

1. Should the console support multiple target APIs simultaneously or focus deeply on one API per deployment?
2. How should the system handle ambiguous natural language inputs that could map to multiple valid endpoints?
3. Should write operations (POST, PUT, DELETE) require explicit user confirmation before execution?
4. At what scale does SQLite need to be replaced with a proper relational database?
5. Should the response explanation be streamed token by token for a better user experience on slow connections?