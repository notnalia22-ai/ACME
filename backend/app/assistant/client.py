import json
import httpx
from app.assistant.tools import TOOL_SCHEMAS, execute_tool

MAX_ITERATIONS = 5


class GroqClient:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self._api_key = api_key
        self._model = model
        self._base_url = "https://api.groq.com/openai/v1/chat/completions"

    def chat(self, question: str, session) -> tuple[str, list[str]]:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are ACME's financial warehouse assistant.\n\n"
                    "Always use tools when answering questions about assets,\n"
                    "prices, analytics, recommendations, or sources.\n\n"
                    "Do not invent data."
                )
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        tool_calls_used: list[str] = []

        for _ in range(MAX_ITERATIONS):
            response = httpx.post(
                self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": messages,
                    "tools": TOOL_SCHEMAS,
                    "tool_choice": "auto",
                },
                timeout=30,
            )

            if response.status_code != 200:
                print(response.text)
                response.raise_for_status()

            body = response.json()
            choices = body.get("choices")
            if not choices:
                raise ValueError(f"Unexpected Groq response shape: {body}")

            msg = choices[0]["message"]
            tool_calls = msg.get("tool_calls")

            # If the model didn't ask to call any tools, return its text answer
            if not tool_calls:
                return msg.get("content", ""), tool_calls_used

            # If the model requested tool execution, keep track of its choice
            messages.append(msg)

            # Execute each requested tool and feed the result back
            for tc in tool_calls:
                call_id = tc.get("id", "")
                name = tc["function"]["name"]
                args = tc["function"].get("arguments", {})
                if isinstance(args, str):
                    args = json.loads(args)

                result = execute_tool(name, args, session)
                tool_calls_used.append(name)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": result
                })

        return "I could not determine an answer.", tool_calls_used
