
import asyncio
import os

import httpx
from dotenv import load_dotenv
from microsoft_teams.api import MessageActivity
from microsoft_teams.apps import ActivityContext, App

load_dotenv()

app = App(dangerously_allow_unauthenticated_requests=True)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "deepseek-r1:7b-fast",
)

SYSTEM_PROMPT = """
You are NX Matrix AI, a professional business assistant.
Give clear, accurate, concise and useful answers.
If you are uncertain, say so.
Do not claim to have performed actions you have not performed.
"""


async def ask_ollama(message: str) -> str:
    """Send a message to the locally running Ollama model."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"].strip()


@app.on_message
async def handle_message(
    ctx: ActivityContext[MessageActivity],
) -> None:
    """Respond to Teams messages using Ollama."""
    message = (ctx.activity.text or "").strip()

    if not message:
        await ctx.send("Please send a text message.")
        return

    try:
        answer = await ask_ollama(message)
        await ctx.send(answer or "The AI returned an empty response.")
    except httpx.TimeoutException:
        await ctx.send(
            "NX Matrix AI timed out. Please try again shortly."
        )
    except httpx.HTTPStatusError:
        await ctx.send(
            "NX Matrix AI encountered an inference error. "
            "Please try again later."
        )
    except httpx.RequestError:
        await ctx.send(
            "NX Matrix AI cannot connect to Ollama. "
            "Check that Ollama is running."
        )
    except (KeyError, ValueError):
        await ctx.send(
            "NX Matrix AI received an invalid response from Ollama."
        )


def main():
    asyncio.run(app.start())


if __name__ == "__main__":
    main()
