
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools import calculate, get_current_datetime
from memory import save_memory, get_memory, detect_memory_request
from agent_engine import AgentEngine


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    # Register the tools AURA is allowed to execute.
    engine = AgentEngine([calculate, get_current_datetime])

    def aura_calculate(expression: str):
        """Safely calculate a mathematical expression."""
        print("\n[TOOL CALL] Function: calculate")
        print(f"[TOOL CALL] Arguments: expression={expression!r}")

        return engine.execute_tool(
            "calculate",
            {"expression": expression},
        )

    def aura_get_current_datetime():
        """Get the current local date and time."""
        print("\n[TOOL CALL] Function: get_current_datetime")

        return engine.execute_tool(
            "get_current_datetime",
            {},
        )

    try:
        client = genai.Client(api_key=api_key)

        chat = client.chats.create(
            model="gemini-3.6-flash",
            config={
                "tools": [
                    aura_calculate,
                    aura_get_current_datetime,
                ],
                "automatic_function_calling": (
                    types.AutomaticFunctionCallingConfig(
                        maximum_remote_calls=5
                    )
                ),
                "system_instruction": (
                    "You are AURA, an AI assistant designed to solve tasks. "
                    "Use aura_calculate for arithmetic instead of calculating "
                    "mentally. Use aura_get_current_datetime whenever the user "
                    "asks for the current date, current time, or day of the week. "
                    "Use tools when appropriate and explain their results clearly. "
                    "Never claim a tool was used unless it actually was. "
                    "If you cannot complete a task, explain why honestly."
                ),
            },
        )

        print("=" * 45)
        print("          AURA AI AGENT")
        print("=" * 45)
        print("Tools enabled: Calculator, Date/Time")
        print("Memory enabled: Remember, Recall")
        print("Automatic tool-call limit: 5 per model turn")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAURA: Goodbye!")
                break

            if user_input.lower() in ("exit", "quit", "bye"):
                print("AURA: Goodbye!")
                break

            if not user_input:
                continue

            # Handle natural-language memory requests.
            detected_memory = detect_memory_request(user_input)

            if detected_memory:
                key, value = detected_memory

                try:
                    print(f"\nAURA: {save_memory(key, value)}\n")
                except OSError as error:
                    print(f"\nAURA: Could not save memory: {error}\n")

                continue

            # Handle explicit "remember key = value" requests.
            if user_input.lower().startswith("remember "):
                memory_text = user_input[9:].strip()

                if "=" not in memory_text:
                    print(
                        "AURA: Use this format: remember key = value\n"
                    )
                    continue

                key, value = memory_text.split("=", 1)
                key = key.strip()
                value = value.strip()

                if not key or not value:
                    print(
                        "AURA: Both the memory key and value are required.\n"
                    )
                    continue

                try:
                    print(f"\nAURA: {save_memory(key, value)}\n")
                except OSError as error:
                    print(f"\nAURA: Could not save memory: {error}\n")

                continue

            # Retrieve a saved memory.
            if user_input.lower().startswith("recall "):
                key = user_input[7:].strip()

                if not key:
                    print(
                        "AURA: Tell me which memory key to recall.\n"
                    )
                    continue

                print(f"\nAURA: {get_memory(key)}\n")
                continue

            # Send other messages to the model.
            try:
                response = chat.send_message(user_input)
                answer = response.text

                if answer:
                    print(f"\nAURA: {answer}\n")
                else:
                    print(
                        "\nAURA: The model returned no text response.\n"
                    )

            except Exception as error:
                print(f"\nRequest failed: {error}\n")

    except Exception as error:
        print(f"Could not initialize AURA: {error}")


if __name__ == "__main__":
    main()
