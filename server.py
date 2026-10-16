"""Mahim AI preview server.

This server contains small, explicit BYOK adapters for common providers.
API keys are accepted per request, held in memory, never written to disk, and
never included in the server's request logs. This is a starter, not a hardened
multi-tenant production backend.
"""
from __future__ import annotations

import json
import os
import re
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
MAX_BODY = 1_000_000
UPSTREAM_TIMEOUT = 120
MAX_PROMPT_CHARS = 16_000
MAX_HISTORY = 24

OPENAI_COMPATIBLE = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "together": "https://api.together.xyz/v1/chat/completions",
}

# Simple in-memory guardrail for the preview. Production needs a distributed,
# account-aware limiter and authenticated sessions.
_REQUEST_TIMES: dict[str, list[float]] = {}


class RequestProblem(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def _safe_model(model: object) -> str:
    value = str(model or "").strip()
    if not value or len(value) > 160 or not re.fullmatch(r"[A-Za-z0-9._:/-]+", value):
        raise RequestProblem("একটি বৈধ provider model ID দিন।")
    return value


def _safe_secret(secret: object) -> str:
    value = str(secret or "").strip()
    if len(value) < 8 or len(value) > 500:
        raise RequestProblem("API key খালি বা অকার্যকর।")
    return value


def _safe_text(value: object, field: str, limit: int = MAX_PROMPT_CHARS) -> str:
    if not isinstance(value, str):
        raise RequestProblem(f"{field} text হতে হবে।")
    value = value.strip()
    if len(value) > limit:
        raise RequestProblem(f"{field} খুব বড়; সর্বোচ্চ {limit} অক্ষর পাঠান।")
    return value


def _safe_messages(raw: object) -> list[dict[str, str]]:
    if not isinstance(raw, list):
        raise RequestProblem("messages তালিকা সঠিক নয়।")
    messages: list[dict[str, str]] = []
    for item in raw[-MAX_HISTORY:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        if role not in ("user", "assistant"):
            continue
        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        if len(content) > 30_000:
            content = content[:30_000]
        messages.append({"role": role, "content": content})
    if not messages:
        raise RequestProblem("একটি user message পাঠান।")
    return messages


def _extract_openai_text(payload: dict) -> str:
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict) and part.get("text"))
    return ""


def _upstream_json(url: str, body: dict, headers: dict[str, str], api_key: str) -> dict:
    request = Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=UPSTREAM_TIMEOUT) as response:
            raw = response.read(12_000_000)
            return json.loads(raw.decode("utf-8"))
    except HTTPError as error:
        # Return a short provider message if safe, but never return the URL or key.
        raw = error.read(16_000).decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
            provider_message = (
                parsed.get("error", {}).get("message")
                if isinstance(parsed.get("error"), dict)
                else parsed.get("message")
            )
        except (ValueError, AttributeError):
            provider_message = None
        if isinstance(provider_message, str) and provider_message.strip():
            lowered = provider_message.lower()
            if any(term in lowered for term in ("api key", "apikey", "credential", "token")):
                raise RequestProblem("Provider rejected the supplied credentials. Check the provider and key, then try again.", 502) from None
            safe_message = provider_message.replace(api_key, "[redacted]")[:280]
            raise RequestProblem(f"Provider error: {safe_message}", 502) from None
        raise RequestProblem(f"AI provider request ব্যর্থ হয়েছে (HTTP {error.code})। Model, quota ও key যাচাই করুন।", 502) from None
    except URLError:
        raise RequestProblem("AI provider-এ সংযোগ করা যায়নি। Network ও provider status যাচাই করুন।", 502) from None
    except TimeoutError:
        raise RequestProblem("AI provider উত্তর দিতে সময় নিয়েছে। পরে আবার চেষ্টা করুন।", 504) from None
    except json.JSONDecodeError:
        raise RequestProblem("AI provider থেকে বোঝা যায়নি এমন response এসেছে।", 502) from None


def _chat_openai_compatible(provider: str, api_key: str, model: str, system: str, messages: list[dict[str, str]]) -> str:
    request_messages = [{"role": "system", "content": system}] if system else []
    request_messages.extend(messages)
    response = _upstream_json(
        OPENAI_COMPATIBLE[provider],
        {"model": model, "messages": request_messages, "temperature": 0.65, "max_tokens": 1400},
        {"Authorization": f"Bearer {api_key}"},
        api_key,
    )
    text = _extract_openai_text(response)
    if not text.strip():
        raise RequestProblem("Provider একটি খালি উত্তর দিয়েছে; model ID বা request support যাচাই করুন।", 502)
    return text


def _chat_gemini(api_key: str, model: str, system: str, messages: list[dict[str, str]]) -> str:
    contents = []
    for message in messages:
        contents.append({
            "role": "model" if message["role"] == "assistant" else "user",
            "parts": [{"text": message["content"]}],
        })
    body: dict = {"contents": contents, "generationConfig": {"temperature": 0.65, "maxOutputTokens": 1400}}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    model_path = quote(model, safe="-._")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_path}:generateContent?key={quote(api_key, safe='')}"
    response = _upstream_json(url, body, {}, api_key)
    try:
        parts = response["candidates"][0]["content"]["parts"]
        text = "\n".join(str(part.get("text", "")) for part in parts if isinstance(part, dict) and part.get("text"))
    except (KeyError, IndexError, TypeError):
        text = ""
    if not text.strip():
        raise RequestProblem("Gemini একটি text উত্তর দেয়নি; model access বা safety response যাচাই করুন।", 502)
    return text


def _chat_anthropic(api_key: str, model: str, system: str, messages: list[dict[str, str]]) -> str:
    body = {"model": model, "max_tokens": 1400, "messages": messages}
    if system:
        body["system"] = system
    response = _upstream_json(
        "https://api.anthropic.com/v1/messages",
        body,
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        api_key,
    )
    try:
        text = "\n".join(str(part.get("text", "")) for part in response["content"] if isinstance(part, dict) and part.get("type") == "text")
    except (KeyError, TypeError):
        text = ""
    if not text.strip():
        raise RequestProblem("Anthropic একটি text উত্তর দেয়নি; model ID বা account access যাচাই করুন।", 502)
    return text


def verify_firebase_token(handler: "MahimHandler") -> str | None:
    require_auth = os.environ.get("REQUIRE_AUTH", "false").strip().lower() in {"1", "true", "yes"}
    if not require_auth:
        return None
    web_api_key = os.environ.get("FIREBASE_WEB_API_KEY", "").strip()
    if not web_api_key:
        raise RequestProblem("Server auth is required, but FIREBASE_WEB_API_KEY is not configured in Render.", 503)
    authorization = handler.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise RequestProblem("Sign in to Mahim AI before using this service.", 401)
    id_token = authorization[7:].strip()
    if not id_token or len(id_token) > 12_000:
        raise RequestProblem("Firebase sign-in token is missing or invalid.", 401)
    url = "https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=" + quote(web_api_key, safe="")
    request = Request(
        url,
        data=json.dumps({"idToken": id_token}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read(512_000).decode("utf-8"))
    except HTTPError:
        raise RequestProblem("Firebase sign-in could not be verified. Please sign in again.", 401) from None
    except (URLError, TimeoutError):
        raise RequestProblem("Could not reach Firebase to verify sign-in. Try again shortly.", 503) from None
    except (ValueError, UnicodeDecodeError):
        raise RequestProblem("Firebase returned an invalid sign-in response.", 503) from None
    try:
        uid = payload["users"][0]["localId"]
    except (KeyError, IndexError, TypeError):
        raise RequestProblem("Firebase sign-in could not be verified. Please sign in again.", 401) from None
    return str(uid)


def make_chat_response(data: dict) -> dict:
    provider = str(data.get("provider") or "").strip().lower()
    if provider not in (*OPENAI_COMPATIBLE.keys(), "gemini", "anthropic"):
        raise RequestProblem("এই prototype-এ provider adapter নেই। OpenAI, Gemini, Anthropic, OpenRouter, Groq বা Together বেছে নিন।")
    api_key = _safe_secret(data.get("apiKey"))
    model = _safe_model(data.get("model"))
    system = _safe_text(data.get("system", ""), "system", 12_000)
    messages = _safe_messages(data.get("messages"))
    if provider == "gemini":
        text = _chat_gemini(api_key, model, system, messages)
    elif provider == "anthropic":
        text = _chat_anthropic(api_key, model, system, messages)
    else:
        text = _chat_openai_compatible(provider, api_key, model, system, messages)
    return {"text": text}


def make_image_response(data: dict) -> dict:
    provider = str(data.get("provider") or "").strip().lower()
    if provider != "openai":
        raise RequestProblem("এই starter-এর image API adapter শুধু OpenAI provider-এ আছে।")
    api_key = _safe_secret(data.get("apiKey"))
    model = _safe_model(data.get("model"))
    prompt = _safe_text(data.get("prompt"), "prompt", 6_000)
    size = str(data.get("size") or "1024x1024")
    if size not in {"1024x1024", "1536x1024", "1024x1536"}:
        raise RequestProblem("সমর্থিত image size বেছে নিন।")
    response = _upstream_json(
        "https://api.openai.com/v1/images/generations",
        {"model": model, "prompt": prompt, "size": size, "n": 1},
        {"Authorization": f"Bearer {api_key}"},
        api_key,
    )
    try:
        item = response["data"][0]
    except (KeyError, IndexError, TypeError):
        raise RequestProblem("Image provider কোনো ফলাফল দেয়নি।", 502) from None
    if isinstance(item.get("b64_json"), str):
        return {"image": "data:image/png;base64," + item["b64_json"]}
    if isinstance(item.get("url"), str) and item["url"].startswith("https://"):
        return {"image": item["url"]}
    raise RequestProblem("Provider response-এ image data পাওয়া যায়নি।", 502)


class MahimHandler(SimpleHTTPRequestHandler):
    server_version = "MahimAIPreview/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        # Intentionally suppress request logs for this demo. Never log bodies or keys.
        return

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        super().end_headers()

    def _send_json(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise RequestProblem("Content-Length সঠিক নয়।") from None
        if length <= 0 or length > MAX_BODY:
            raise RequestProblem("Request খালি বা অতিরিক্ত বড়।")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RequestProblem("JSON request সঠিক নয়।") from None
        if not isinstance(payload, dict):
            raise RequestProblem("JSON object পাঠান।")
        return payload

    def _allow_request(self, identity: str | None = None) -> bool:
        now = time.time()
        # Behind a reverse proxy the address may be shared; production should
        # replace this with a distributed account-aware limiter.
        client = identity or self.client_address[0]
        times = [stamp for stamp in _REQUEST_TIMES.get(client, []) if now - stamp < 60]
        if len(times) >= 24:
            _REQUEST_TIMES[client] = times
            return False
        times.append(now)
        _REQUEST_TIMES[client] = times
        return True

    def do_GET(self) -> None:
        if self.path == "/api/health":
            require_auth = os.environ.get("REQUIRE_AUTH", "false").strip().lower() in {"1", "true", "yes"}
            self._send_json(200, {
                "ok": True,
                "service": "Mahim AI",
                "auth": "required" if require_auth else "optional-preview",
                "firebaseVerifierConfigured": bool(os.environ.get("FIREBASE_WEB_API_KEY")),
            })
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path not in {"/api/chat", "/api/image"}:
            self._send_json(404, {"error": "এই API route পাওয়া যায়নি।"})
            return
        try:
            uid = verify_firebase_token(self)
            if not self._allow_request(uid):
                self._send_json(429, {"error": "এই account-এর request limit সাময়িকভাবে পূর্ণ। এক মিনিট পরে আবার চেষ্টা করুন।"})
                return
            data = self._read_json()
            result = make_chat_response(data) if self.path == "/api/chat" else make_image_response(data)
            self._send_json(200, result)
        except RequestProblem as error:
            self._send_json(error.status, {"error": str(error)})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            # Fail closed with a generic error; upstream credentials are never
            # reflected in an unhandled exception or sent to the browser.
            self._send_json(500, {"error": "Server-এর ভেতরে সমস্যা হয়েছে। Key আবার দিন, model ID যাচাই করুন, অথবা পরে চেষ্টা করুন।"})


def main() -> None:
    port = int(os.environ.get("PORT", "4173"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), MahimHandler)
    httpd.daemon_threads = True
    print(f"Mahim AI preview server listening on 0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
