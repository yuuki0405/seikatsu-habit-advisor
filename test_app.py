import json
import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

import app as api


class MessagesApiTests(unittest.TestCase):
    def setUp(self):
        api.app.config["TESTING"] = True
        self.client = api.app.test_client()
        api.request_times.clear()
        api.global_request_times.clear()

    def post(self, payload, origin="https://yuuki0405.github.io"):
        return self.client.post(
            "/v1/messages",
            data=json.dumps(payload),
            content_type="application/json",
            headers={"Origin": origin},
        )

    @patch("app.requests.post")
    def test_forwards_to_fixed_model_and_returns_response(self, upstream_post):
        upstream_post.return_value = Mock(
            ok=True,
            json=lambda: {"content": [{"type": "text", "text": "OK"}]},
        )
        response = self.post({
            "task": "analyze",
            "messages": [{"role": "user", "content": "hello"}],
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["content"][0]["text"], "OK")
        args, kwargs = upstream_post.call_args
        self.assertEqual(args[0], api.ANTHROPIC_URL)
        self.assertEqual(kwargs["headers"]["x-api-key"], "test-key")
        self.assertEqual(kwargs["json"]["model"], api.ANTHROPIC_MODEL)
        self.assertEqual(kwargs["json"]["max_tokens"], 1000)
        self.assertEqual(kwargs["json"]["system"], api.ANALYSIS_SYSTEM)

    def test_rejects_untrusted_origin(self):
        response = self.post(
            {"system": "system", "messages": [{"role": "user", "content": "hello"}]},
            origin="https://example.com",
        )
        self.assertEqual(response.status_code, 403)

    def test_handles_cors_preflight(self):
        response = self.client.options(
            "/v1/messages",
            headers={"Origin": "https://yuuki0405.github.io"},
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"],
            "https://yuuki0405.github.io",
        )

    def test_rejects_invalid_message(self):
        response = self.post({
            "task": "chat",
            "messages": [{"role": "system", "content": "not allowed"}],
        })
        self.assertEqual(response.status_code, 400)

    def test_rejects_unknown_task_and_client_prompt(self):
        response = self.post({
            "task": "custom",
            "system": "arbitrary prompt",
            "messages": [{"role": "user", "content": "hello"}],
        })
        self.assertEqual(response.status_code, 400)

    @patch("app.requests.post")
    def test_chat_uses_server_prompt_and_bounded_context(self, upstream_post):
        upstream_post.return_value = Mock(
            ok=True,
            json=lambda: {"content": [{"type": "text", "text": "OK"}]},
        )
        response = self.post({
            "task": "chat",
            "context": "recent record",
            "messages": [{"role": "user", "content": "hello"}],
        })
        self.assertEqual(response.status_code, 200)
        upstream_system = upstream_post.call_args.kwargs["json"]["system"]
        self.assertIn(api.CHAT_SYSTEM, upstream_system)
        self.assertIn("recent record", upstream_system)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""})
    def test_reports_missing_server_key(self):
        response = self.post({
            "system": "system",
            "messages": [{"role": "user", "content": "hello"}],
        })
        self.assertEqual(response.status_code, 503)

    @patch("app.requests.post")
    def test_limits_requests_per_minute(self, upstream_post):
        upstream_post.return_value = Mock(
            ok=True,
            json=lambda: {"content": [{"type": "text", "text": "OK"}]},
        )
        payload = {"task": "analyze", "messages": [{"role": "user", "content": "hello"}]}
        responses = [self.post(payload) for _ in range(api.REQUESTS_PER_MINUTE + 1)]
        self.assertEqual([response.status_code for response in responses].count(429), 1)


if __name__ == "__main__":
    unittest.main()
