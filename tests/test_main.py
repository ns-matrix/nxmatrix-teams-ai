"""Unit tests for the LLM request builder and response handling."""

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Unit tests intentionally use the isolated local emulator mode. No public
# endpoint is started by these tests.
os.environ.setdefault("DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS", "true")

from src import main


class AskLlmTests(unittest.TestCase):
    """Verify request construction without requiring a live LLM provider."""

    def _mock_client(self, payload):
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = payload
        client = MagicMock()
        client.post = AsyncMock(return_value=response)
        client_context = MagicMock()
        client_context.__aenter__.return_value = client
        client_context.__aexit__.return_value = False
        return client, client_context, response

    def test_uses_chat_completions_and_returns_text(self) -> None:
        """The client should send the configured model and trim the response."""
        client, context, response = self._mock_client(
            {"choices": [{"message": {"content": "  Hello from mock  "}}]}
        )
        with patch("src.main.httpx.AsyncClient", return_value=context) as factory:
            answer = asyncio.run(main.ask_llm("Hello"))

        self.assertEqual(answer, "Hello from mock")
        factory.assert_called_once_with(timeout=main.API_TIMEOUT_SECONDS)
        self.assertEqual(
            client.post.call_args.args[0],
            f"{main.API_BASE_URL}/chat/completions",
        )
        payload = client.post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], main.API_MODEL)
        self.assertEqual(payload["messages"][-1], {"role": "user", "content": "Hello"})
        self.assertFalse(payload["stream"])
        response.raise_for_status.assert_called_once()

    def test_accepts_base_url_that_already_has_completion_path(self) -> None:
        """The client should not append the completion path twice."""
        client, context, _ = self._mock_client(
            {"choices": [{"message": {"content": "ok"}}]}
        )
        with (
            patch("src.main.API_BASE_URL", "http://llm.example/v1/chat/completions"),
            patch("src.main.httpx.AsyncClient", return_value=context),
        ):
            self.assertEqual(asyncio.run(main.ask_llm("test")), "ok")

        self.assertEqual(
            client.post.call_args.args[0],
            "http://llm.example/v1/chat/completions",
        )

    def test_rejects_empty_choices(self) -> None:
        """An empty provider choices array must be treated as an invalid response."""
        _, context, _ = self._mock_client({"choices": []})
        with patch("src.main.httpx.AsyncClient", return_value=context):
            with self.assertRaises(ValueError):
                asyncio.run(main.ask_llm("test"))

    def test_rejects_blank_content(self) -> None:
        """Whitespace-only model output is not a useful completion."""
        _, context, _ = self._mock_client(
            {"choices": [{"message": {"content": "   "}}]}
        )
        with patch("src.main.httpx.AsyncClient", return_value=context):
            self.assertEqual(asyncio.run(main.ask_llm("test")), "")


if __name__ == "__main__":
    unittest.main()
