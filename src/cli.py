from .interpreter import generate_api_request, explain_response
from .api_executor import execute_request
from .history import log_request, get_history


def main():
    print("\n=== LLM API Console ===")
    print("Type a natural language request to query the Stripe API.")
    print("Type 'history' to see past requests.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input(">> ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("Goodbye.")
            break

        if user_input.lower() == "history":
            records = get_history(limit=5)
            if not records:
                print("No history yet.\n")
            else:
                for r in records:
                    print(f"[{r['timestamp']}] {r['user_input']}")
                    print(f"  → {r['method']} {r['endpoint']}")
                    print(f"  → {r['explanation']}\n")
            continue

        print("\nGenerating API request...")
        req = generate_api_request(user_input)

        if "error" in req:
            print(f"Error generating request: {req['error']}\n")
            continue

        print(f"Calling Stripe: {req['method']} {req['endpoint']} {req.get('params', {})}")
        result = execute_request(req['method'], req['endpoint'], req.get('params', {}))

        print("\nExplaining response...")
        explanation = explain_response(result, user_input)

        log_request(user_input, req['method'], req['endpoint'], req.get('params', {}), result, explanation)

        print(f"\nRESPONSE SUMMARY:\n{explanation}\n")
        print(f"RAW RESPONSE:\n{result}\n")


if __name__ == "__main__":
    main()