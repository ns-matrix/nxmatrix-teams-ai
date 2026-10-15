import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()
base = os.getenv("API_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")
key = os.getenv("API_KEY", "ollama").strip()
model = os.getenv("API_MODEL", "qwen2.5:3b").strip()
url = base if base.endswith("/chat/completions") else f"{base}/chat/completions"
headers = {"Content-Type": "application/json"}
if key:
    headers["Authorization"] = f"Bearer {key}"

async def main():
    print(f"Base URL: {base}")
    print(f"Model: {model}")
    print("Sending test request...")
    try:
        async with httpx.AsyncClient(timeout=float(os.getenv("API_TIMEOUT_SECONDS", "120"))) as client:
            response = await client.post(url, headers=headers, json={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with exactly: NX Matrix API connection works"}],
                "stream": False,
            })
            response.raise_for_status()
            data = response.json()
            print("\nAPI test succeeded:")
            print(data["choices"][0]["message"]["content"])
    except httpx.HTTPStatusError as exc:
        print(f"API returned HTTP {exc.response.status_code}. Check API key, model, and endpoint.")
        sys.exit(1)
    except (httpx.RequestError, KeyError, ValueError) as exc:
        print(f"API test failed: {type(exc).__name__}: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
