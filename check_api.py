"""Connectivity test for the configured OpenAI-compatible Chat Completions API."""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
API_KEY = os.getenv("API_KEY", "ollama").strip()
MODEL = os.getenv("API_MODEL", "qwen2.5:3b").strip()
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "120"))

endpoint = BASE_URL if BASE_URL.endswith("/chat/completions") else f"{BASE_URL}/chat/completions"
headers = {"Content-Type": "application/json"}
if API_KEY:
    headers["Authorization"] = f"Bearer {API_KEY}"


async def main() -> int:
    """Send a minimal request to verify the configured LLM endpoint."""
    if not BASE_URL or not MODEL:
        print("API_BASE_URL and API_MODEL must be non-empty.")
        return 1

    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    print("Sending test request...")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": "Reply with exactly: NX Matrix API connection works"}],
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            choices = data["choices"]
            if not isinstance(choices, list) or not choices:
                raise ValueError("The API response contained no choices.")
            content = choices[0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("The API response contained empty or non-text content.")
            print("\nAPI test succeeded:")
            print(content.strip())
            return 0
    except httpx.HTTPStatusError as exc:
        print(f"API returned HTTP {exc.response.status_code}. Check API key, model, and endpoint.")
    except httpx.TimeoutException:
        print("API test timed out. Increase API_TIMEOUT_SECONDS or check provider availability.")
    except httpx.RequestError as exc:
        print(f"API request failed ({type(exc).__name__}). Check API_BASE_URL and network/service status.")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"API returned an unexpected response ({type(exc).__name__}): {exc}")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
