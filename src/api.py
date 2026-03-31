from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .interpreter import generate_api_request, explain_response
from .api_executor import execute_request
from .history import log_request, get_history

app = FastAPI(
    title="LLM API Console",
    description="Natural language interface for the Stripe API powered by GPT",
    version="0.1.0",
)


class QueryRequest(BaseModel):
    user_input: str


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.post("/query")
def query(request: QueryRequest):
    user_input = request.user_input

    req = generate_api_request(user_input)

    if "error" in req:
        return {"error": req["error"]}

    result = execute_request(req["method"], req["endpoint"], req.get("params", {}))
    explanation = explain_response(result, user_input)

    log_request(user_input, req["method"], req["endpoint"], req.get("params", {}), result, explanation)

    return {
        "user_input": user_input,
        "generated_request": req,
        "stripe_response": result,
        "explanation": explanation,
    }


@app.get("/history")
def history(limit: Optional[int] = 10):
    return {
        "count": limit,
        "history": get_history(limit=limit),
    }