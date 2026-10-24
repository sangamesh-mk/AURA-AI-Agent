
import os
import re

from dotenv import load_dotenv
from google import genai

from tools import calculate, get_current_datetime
from agent_engine import AgentEngine
from memory import save_memory, get_memory, detect_memory_request


load_dotenv()


class AuraService:
    """Shared AI service for AURA's chat and tool execution."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = "gemini-3.6-flash"

        self.engine = AgentEngine([
            calculate,
            get_current_datetime,
        ])

        self.system_instruction = (
            "You are AURA, a helpful personal AI agent. "
            "Answer clearly, accurately, and honestly. "
            "Use recent conversation history to understand follow-up questions. "
            "Use the calculator tool for arithmetic when available. "
            "Use the date/time tool when asked for the current date or time. "
            "Never claim to have executed an action unless it actually happened."
        )

    def offline_response(self, prompt: str) -> str:
        """Handle common requests without an external AI model."""
        text = prompt.strip()
        lowered = text.casefold()

        if lowered in {
            "hi", "hello", "hey", "hii", "helo",
            "good morning", "good afternoon", "good evening",
        }:
            return (
                "Hello! I'm AURA, your personal AI assistant. "
                "I'm in offline mode, but I can still help with "
                "memory, calculations, and date/time."
            )

        memory_request = detect_memory_request(text)

        if memory_request:
            key, value = memory_request
            try:
                return save_memory(key, value)
            except OSError as error:
                return f"I couldn't save that memory: {error}"

        if lowered.startswith("recall "):
            key = text[7:].strip()

            if not key:
                return "Please specify which memory to recall."

            return str(get_memory(key))

        if any(phrase in lowered for phrase in (
            "current date",
            "current time",
            "date and time",
            "what time is it",
            "today's date",
            "todays date",
            "what is the date",
            "what day is it",
        )):
            result = self.engine.execute_tool(
                "get_current_datetime",
                {},
            )
            return str(result)

        match = re.match(
            r"^(?:please\s+)?(?:calculate|compute|solve|what is|what's)\s+(.+?)\s*[?.!]*$",
            text,
            re.IGNORECASE,
        )

        if match:
            expression = (
                match.group(1)
                .replace("×", "*")
                .replace("÷", "/")
                .replace("−", "-")
                .replace("–", "-")
            )

            if re.fullmatch(r"[0-9\s()+*/%.\-]+", expression):
                result = self.engine.execute_tool(
                    "calculate",
                    {"expression": expression},
                )
                return f"Calculation result: {result}"

        if lowered in {
            "explain ai",
            "explain artificial intelligence",
            "what is ai",
            "what is artificial intelligence",
        }:
            return (
                "Artificial intelligence (AI) is technology that enables "
                "computers to perform tasks that usually require human "
                "intelligence, such as understanding language, recognizing "
                "patterns, and solving problems."
            )

        return (
            "I'm currently in offline mode because the AI service is "
            "unavailable. I can handle greetings, save and recall memories, "
            "perform basic calculations, and provide the current date and "
            "time. General questions require an available AI model."
        )

    def respond(self, prompt: str, history=None) -> str:
        """Generate a response using recent conversation history."""
        text = prompt.strip()

        if not text:
            return "Please enter a message."

        memory_request = detect_memory_request(text)

        if memory_request:
            key, value = memory_request
            try:
                return save_memory(key, value)
            except OSError as error:
                return f"Could not save memory: {error}"

        if text.casefold().startswith("recall "):
            key = text[7:].strip()

            if not key:
                return "Please specify which memory to recall."

            return str(get_memory(key))

        if self.client is None:
            return self.offline_response(text)

        try:
            contents = []

            for message in (history or [])[-20:]:
                role = message.get("role")
                content = message.get("content", "")

                if (
                    role in {"user", "assistant"}
                    and isinstance(content, str)
                    and content.strip()
                ):
                    contents.append({
                        "role": "model" if role == "assistant" else "user",
                        "parts": [{"text": content}],
                    })

            contents.append({
                "role": "user",
                "parts": [{"text": text}],
            })

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config={
                    "system_instruction": self.system_instruction,
                },
            )

            answer = response.text

            if answer and answer.strip():
                return answer.strip()

            return self.offline_response(text)

        except Exception as error:
            error_text = str(error).casefold()

            if "429" in error_text or "resource_exhausted" in error_text:
                return (
                    "Gemini's API quota is exhausted.\n\n"
                    + self.offline_response(text)
                )

            return (
                "Gemini is currently unavailable.\n\n"
                + self.offline_response(text)
            )
