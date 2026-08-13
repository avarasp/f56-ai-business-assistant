from app.graph import ask


def main():
    print("F56 AI Business Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("> ").strip()

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            break

        try:
            result = ask(question)

            print()
            print(result["answer"])

            print(
                f"\n[intent={result.get('intent')} "
                f"tool={result.get('tool_name')}]"
            )

            if result.get("tool_input"):
                print(f"[tool_input={result['tool_input']}]")

            print()

        except Exception as exc:
            print()
            print("I couldn't process that question reliably.")
            print(f"[error={exc}]")
            print()


if __name__ == "__main__":
    main()