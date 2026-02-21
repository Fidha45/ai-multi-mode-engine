import json
from typing import Iterator

import httpx
from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    stream_with_context,
    url_for,
)
from openai import OpenAI

from config import (
    AI_PROVIDER,
    API_KEY,
    MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    WEB_AUTH_ENABLED,
    WEB_PASSWORD,
    WEB_SECRET_KEY,
    WEB_USERNAME,
)
from evaluator import choose_mode
from main import generate_response, startup_check
from prompts import MODES, get_system_prompt

app = Flask(__name__)
app.secret_key = WEB_SECRET_KEY


def is_authenticated() -> bool:
    if not WEB_AUTH_ENABLED:
        return True
    return bool(session.get("authenticated"))


def require_auth_page():
    if not is_authenticated():
        return redirect(url_for("login"))
    return None


def require_auth_api():
    if not is_authenticated():
        return jsonify({"ok": False, "error": "Authentication required."}), 401
    return None


def build_context_prompt(user_input: str, history: list[dict]) -> str:
    if not history:
        return user_input

    lines = []
    for item in history[-6:]:
        role = str(item.get("role", "")).strip().lower()
        text = str(item.get("content", "")).strip()
        if not text:
            continue
        if role == "user":
            lines.append(f"User: {text}")
        elif role == "assistant":
            lines.append(f"Assistant: {text}")

    if not lines:
        return user_input

    transcript = "\n".join(lines)
    return (
        "Use the recent conversation for context.\n"
        f"{transcript}\n"
        f"User: {user_input}"
    )


@app.get("/")
def index():
    auth_response = require_auth_page()
    if auth_response:
        return auth_response

    ok, message = startup_check()
    return render_template(
        "index.html",
        modes=["auto", *MODES.keys()],
        startup_ok=ok,
        startup_message=message,
        auth_enabled=WEB_AUTH_ENABLED,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if not WEB_AUTH_ENABLED:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html", error="")

    username = str(request.form.get("username", "")).strip()
    password = str(request.form.get("password", "")).strip()
    if username == WEB_USERNAME and password == WEB_PASSWORD:
        session["authenticated"] = True
        return redirect(url_for("index"))

    return render_template("login.html", error="Invalid username or password.")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login" if WEB_AUTH_ENABLED else "index"))


@app.post("/api/chat")
def chat():
    auth_response = require_auth_api()
    if auth_response:
        return auth_response

    payload = request.get_json(silent=True) or {}
    user_input = str(payload.get("prompt", "")).strip()
    mode = str(payload.get("mode", "auto")).strip().lower() or "auto"
    history = payload.get("history", [])

    if not user_input:
        return jsonify({"ok": False, "error": "Prompt is required."}), 400

    if mode != "auto" and mode not in MODES:
        valid = ", ".join(MODES.keys())
        return jsonify(
            {"ok": False, "error": f"Invalid mode: {mode}. Use auto or one of: {valid}"}
        ), 400

    ok, message = startup_check()
    if not ok:
        return jsonify({"ok": False, "error": f"Startup check failed: {message}"}), 503

    try:
        context_prompt = (
            build_context_prompt(user_input, history)
            if isinstance(history, list)
            else user_input
        )
        selected_mode, answer = generate_response(user_input=context_prompt, mode=mode)
        return jsonify({"ok": True, "mode_used": selected_mode, "response": answer})
    except Exception as error:
        return jsonify({"ok": False, "error": str(error)}), 500


def iter_openai_chunks(user_input: str, selected_mode: str) -> Iterator[str]:
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=API_KEY)
    system_prompt = get_system_prompt(selected_mode)
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0.7 if selected_mode == "creative" else 0.3,
        stream=True,
    )
    for event in stream:
        if not event.choices:
            continue
        delta = event.choices[0].delta
        if delta and delta.content:
            yield delta.content


def iter_ollama_chunks(user_input: str, selected_mode: str) -> Iterator[str]:
    system_prompt = get_system_prompt(selected_mode)
    num_predict = 400 if selected_mode == "technical" else 512
    with httpx.stream(
        "POST",
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            "stream": True,
            "options": {
                "temperature": 0.7 if selected_mode == "creative" else 0.3,
                "num_predict": num_predict,
            },
        },
        timeout=180.0,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = payload.get("message", {}).get("content", "")
            if text:
                yield text


@app.post("/api/chat-stream")
def chat_stream():
    auth_response = require_auth_api()
    if auth_response:
        return auth_response

    payload = request.get_json(silent=True) or {}
    user_input = str(payload.get("prompt", "")).strip()
    mode = str(payload.get("mode", "auto")).strip().lower() or "auto"
    history = payload.get("history", [])

    if not user_input:
        return jsonify({"ok": False, "error": "Prompt is required."}), 400
    if mode != "auto" and mode not in MODES:
        valid = ", ".join(MODES.keys())
        return jsonify(
            {"ok": False, "error": f"Invalid mode: {mode}. Use auto or one of: {valid}"}
        ), 400

    ok, message = startup_check()
    if not ok:
        return jsonify({"ok": False, "error": f"Startup check failed: {message}"}), 503

    context_prompt = (
        build_context_prompt(user_input, history) if isinstance(history, list) else user_input
    )
    selected_mode = choose_mode(context_prompt) if mode == "auto" else mode

    def generate():
        try:
            if AI_PROVIDER == "openai":
                for chunk in iter_openai_chunks(context_prompt, selected_mode):
                    yield chunk
            else:
                for chunk in iter_ollama_chunks(context_prompt, selected_mode):
                    yield chunk
        except Exception as error:
            yield f"\n[Error] {error}"

    response = Response(stream_with_context(generate()), mimetype="text/plain")
    response.headers["X-Mode-Used"] = selected_mode
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
