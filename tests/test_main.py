"""Unit tests for the OpenAI-compatible LLM client."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src import main


class AskLlmTests(unittest.TestCase):
    def test_uses_chat_completions_and_returns_text(self) -> None:
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "choices": [{"message": {"content": "  Hello from mock  "}}]
        }

        client = MagicMock()
        client.post = AsyncMock(return_value=response)
        client_context = MagicMock()
        client_context.__aenter__.return_value = client
        client_context.__aexit__.return_value = False

        with patch("src.main.httpx.AsyncClient", return_value=client_context) as factory:
            answer = asyncio.run(main.ask_llm("Hello"))

        self.assertEqual(answer, "Hello from mock")
        factory.assert_called_once_with(timeout=main.API_TIMEOUT_SECONDS)
        called_url = client.post.call_args.args[0]
        self.assertEqual(
            called_url,
            f"{main.API_BASE_URL}/chat/completions",
        )
        payload = client.post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], main.API_MODEL)
        self.assertEqual(payload["messages"][-1], {"role": "user", "content": "Hello"})
        self.assertFalse(payload["stream"])
        response.raise_for_status.assert_called_once()

    def test_accepts_base_url_that_already_has_completion_path(self) -> None:
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}

        client = MagicMock()
        client.post = AsyncMock(return_value=response)
        client_context = MagicMock()
        client_context.__aenter__.return_value = client
        client_context.__aexit__.return_value = False

        with (
            patch("src.main.API_BASE_URL", "http://llm.example/v1/chat/completions"),
            patch("src.main.httpx.AsyncClient", return_value=client_context),
        ):
            self.assertEqual(asyncio.run(main.ask_llm("test")), "ok")

        self.assertEqual(
            client.post.call_args.args[0],
            "http://llm.example/v1/chat/completions",
        )


if __name__ == "__main__":
    unittest.main()
