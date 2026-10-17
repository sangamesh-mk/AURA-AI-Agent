
import os

from dotenv import load_dotenv
from google import genai
from tools import calculate


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    try:
        client = genai.Client(api_key=api_key)

        chat = client.chats.create(
            model="gemini-3.6-flash",
            config={
                "tools": [calculate],
                "system_instruction": (
                    "You are AURA, a helpful AI assistant. "
                    "You can use the calculate tool for arithmetic. "
                    "When a user requests a calculation, use this tool "
                    "instead of calculating mentally. Explain the result "
                    "clearly. Never claim a tool was used unless it was."
                ),
            },
        )

        print("=" * 40)
        print("       AURA AI ASSISTANT")
        print("=" * 40)
        print("Calculator tool enabled!")
        print("Type 'exit' to quit.\n")

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ("exit", "quit", "bye"):
                print("AURA: Goodbye!")
                break

            if not user_input:
                continue

            try:
                response = chat.send_message(user_input)
                print(f"\nAURA: {response.text}\n")

            except Exception as error:
                print(f"\nRequest failed: {error}\n")

    except Exception as error:
        print(f"Could not initialize AURA: {error}")


if __name__ == "__main__":
    main()
