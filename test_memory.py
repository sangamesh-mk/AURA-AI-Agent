
from memory import detect_memory_request

test_messages = [
    "Remember that my favorite language is Python.",
    "Remember my project is Connect Campus.",
    "Remember that my goal is to win a hackathon.",
    "Hello AURA, how are you?",
]

for message in test_messages:
    result = detect_memory_request(message)
    print(f"Message: {message}")
    print(f"Detected: {result}")
    print("-" * 40)
