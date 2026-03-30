from .llm_client import chat

STRIPE_SYSTEM_PROMPT = """
You are an expert on the Stripe API. When given a natural language request, 
you respond with a JSON object describing the API call to make.

Always respond with valid JSON in this exact format:
{
  "method": "GET" or "POST",
  "endpoint": "/v1/...",
  "params": {} or {"key": "value"},
  "description": "one sentence explaining what this call does"
}

Only use real Stripe API endpoints. Use test mode assumptions.
Never include the base URL — only the path starting with /v1/.
"""

EXPLAIN_SYSTEM_PROMPT = """
You are a helpful API assistant explaining Stripe API responses to developers.
Given an API response, explain what it means in 2-3 plain English sentences.
Highlight the most important fields and what they indicate.
"""


def generate_api_request(user_input: str) -> dict:
    import json
    prompt = f"Generate a Stripe API call for: {user_input}"
    raw = chat(prompt, system=STRIPE_SYSTEM_PROMPT)
    try:
        # strip markdown code blocks if present
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"error": "Could not parse LLM response", "raw": raw}


def explain_response(api_response: dict, original_request: str) -> str:
    prompt = (
        f"The user asked: '{original_request}'\n\n"
        f"The Stripe API returned:\n{api_response}\n\n"
        f"Explain this response in plain English."
    )
    return chat(prompt, system=EXPLAIN_SYSTEM_PROMPT)