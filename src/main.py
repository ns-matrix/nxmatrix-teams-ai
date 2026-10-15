"""NX Matrix AI: Microsoft Teams message handler backed by an OpenAI-compatible LLM API."""

import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv
from microsoft_teams.api import MessageActivity
from microsoft_teams.apps import ActivityContext, App

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "").strip()
TENANT_ID = os.getenv("TENANT_ID", "").strip()
ALLOW_UNAUTHENTICATED_LOCAL = (
    os.getenv("DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS", "").strip().lower()
    == "true"
)

# Never silently run an unauthenticated endpoint. For a real Teams deployment,
# configure all three bot credentials. The explicit bypass is only for a local
# Agents Playground/emulator and must never be used with a public tunnel.
if all((CLIENT_ID, CLIENT_SECRET, TENANT_ID)):
    app = App()
elif ALLOW_UNAUTHENTICATED_LOCAL:
    app = App(dangerously_allow_unauthenticated_requests=True)
else:
    raise RuntimeError(
        "Teams bot credentials are missing. Configure CLIENT_ID, CLIENT_SECRET, "
        "and TENANT_ID for authenticated use, or set "
        "DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true only for local "
        "Agents Playground testing. Do not expose local mode publicly."
    )

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
API_KEY = os.getenv("API_KEY", "ollama").strip()
API_MODEL = os.getenv("API_MODEL", "qwen2.5:3b").strip()
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "120"))
BOT_PORT = int(os.getenv("BOT_PORT", os.getenv("PORT", "3978")))
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are NX Matrix AI, a professional business assistant. "
    "Give clear, accurate, concise and useful answers. If uncertain, say so. "
    "Never claim to have performed actions you have not performed.",
)


async def ask_llm(message: str) -> str:
    """Send a user message to an OpenAI-compatible Chat Completions endpoint."""
    if not API_BASE_URL:
        raise ValueError("API_BASE_URL cannot be empty.")
    if not API_MODEL:
        raise ValueError("API_MODEL cannot be empty.")

    endpoint = (
        API_BASE_URL
        if API_BASE_URL.endswith("/chat/completions")
        else f"{API_BASE_URL}/chat/completions"
    )
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    async with httpx.AsyncClient(timeout=API_TIMEOUT_SECONDS) as client:
        response = await client.post(
            endpoint,
            headers=headers,
            json={
                "model": API_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        try:
            choices = payload["choices"]
            if not isinstance(choices, list) or not choices:
                raise ValueError("The LLM returned no choices.")
            content = choices[0]["message"]["content"]
        except (IndexError, KeyError, TypeError) as exc:
            raise ValueError("The LLM returned an unexpected Chat Completions response.") from exc
        if not isinstance(content, str):
            raise ValueError("The LLM returned non-text message content.")
        return content.strip()


@app.on_message
async def handle_message(ctx: ActivityContext[MessageActivity]) -> None:
    """Handle one incoming Teams message."""
    message = (ctx.activity.text or "").strip()
    if not message:
        await ctx.send("Please send a text message.")
        return

    try:
        answer = await ask_llm(message)
        await ctx.send(answer or "The AI returned an empty response.")
    except httpx.TimeoutException:
        await ctx.send("NX Matrix AI timed out. Please try again shortly.")
    except httpx.HTTPStatusError as exc:
        # Keep provider response bodies and credentials out of user-facing chat.
        status = exc.response.status_code
        if status in (401, 403):
            await ctx.send("NX Matrix AI could not authenticate with the configured LLM provider. Check API_KEY.")
        elif status == 404:
            await ctx.send("NX Matrix AI could not find the configured model or API endpoint. Check API_BASE_URL and API_MODEL.")
        else:
            await ctx.send(f"NX Matrix AI received an error from the LLM provider (HTTP {status}).")
    except httpx.RequestError:
        await ctx.send("NX Matrix AI cannot connect to the configured LLM provider. Check that the service is running and API_BASE_URL is correct.")
    except (KeyError, IndexError, TypeError, ValueError):
        await ctx.send("NX Matrix AI received an invalid response from the configured LLM provider.")


def main() -> None:
    """Start the Teams bot service on the configured port."""
    asyncio.run(app.start(port=BOT_PORT))


if __name__ == "__main__":
    main()
