import os
import time
from collections import defaultdict, deque

import requests
from flask import Flask, jsonify, make_response, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "ALLOWED_ORIGINS", "https://yuuki0405.github.io"
    ).split(",")
    if origin.strip()
}
REQUESTS_PER_MINUTE = 6
REQUESTS_PER_DAY = 40
GLOBAL_REQUESTS_PER_DAY = 100
request_times = defaultdict(deque)
global_request_times = deque()


def json_error(message, status):
    return jsonify({"error": message}), status


def origin_is_allowed(origin):
    return bool(origin) and origin.rstrip("/") in ALLOWED_ORIGINS


def apply_cors(response):
    origin = request.headers.get("Origin")
    if origin_is_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "600"
    return response


@app.after_request
def add_cors_headers(response):
    return apply_cors(response)


def is_rate_limited(client_id, now):
    while global_request_times and now - global_request_times[0] >= 24 * 60 * 60:
        global_request_times.popleft()
    if len(global_request_times) >= GLOBAL_REQUESTS_PER_DAY:
        return True

    timestamps = request_times[client_id]
    while timestamps and now - timestamps[0] >= 24 * 60 * 60:
        timestamps.popleft()
    if len(timestamps) >= REQUESTS_PER_DAY:
        return True
    minute_count = sum(now - timestamp < 60 for timestamp in timestamps)
    if minute_count >= REQUESTS_PER_MINUTE:
        return True
    timestamps.append(now)
    global_request_times.append(now)
    return False


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "api_key_configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
    })


@app.route("/v1/messages", methods=["POST", "OPTIONS"])
def messages():
    origin = request.headers.get("Origin")
    if not origin_is_allowed(origin):
        return json_error("This origin is not allowed.", 403)

    if request.method == "OPTIONS":
        return make_response("", 204)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        app.logger.error("ANTHROPIC_API_KEY is not configured.")
        return json_error(
            "AI service is not configured. Please contact the site owner.", 503
        )

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return json_error("Request body must be a JSON object.", 400)

    system = payload.get("system")
    messages = payload.get("messages")
    if not isinstance(system, str) or not system.strip() or len(system) > 6000:
        return json_error("Invalid system prompt.", 400)
    if not isinstance(messages, list) or not 1 <= len(messages) <= 12:
        return json_error("Expected between 1 and 12 messages.", 400)
    for message in messages:
        if (
            not isinstance(message, dict)
            or message.get("role") not in ("user", "assistant")
            or not isinstance(message.get("content"), str)
            or not message["content"].strip()
            or len(message["content"]) > 6000
        ):
            return json_error("Invalid message format.", 400)

    client_id = request.remote_addr or "unknown"
    if is_rate_limited(client_id, time.time()):
        return json_error("Request limit reached. Please try again later.", 429)

    upstream_payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1000,
        "system": system,
        "messages": messages,
    }
    try:
        upstream = requests.post(
            ANTHROPIC_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json=upstream_payload,
            timeout=(5, 60),
            allow_redirects=False,
        )
    except requests.RequestException:
        app.logger.exception("Anthropic request failed.")
        return json_error("AI service could not be reached. Please try again.", 502)

    if not upstream.ok:
        app.logger.warning("Anthropic API returned HTTP %s.", upstream.status_code)
        if upstream.status_code in (400, 401, 403, 429):
            return json_error(
                "AI service rejected the request. Check the API key, account limits, and input.",
                502,
            )
        return json_error("AI service is temporarily unavailable. Please try again.", 502)

    try:
        result = upstream.json()
    except requests.exceptions.JSONDecodeError:
        app.logger.error("Anthropic API returned invalid JSON.")
        return json_error("AI service returned an invalid response.", 502)

    if not isinstance(result, dict) or not isinstance(result.get("content"), list):
        app.logger.error("Anthropic API response is missing content.")
        return json_error("AI service returned an invalid response.", 502)
    return jsonify(result)


@app.errorhandler(413)
def request_too_large(_error):
    return apply_cors(json_error("Request body is too large.", 413))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
