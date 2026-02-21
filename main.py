import os
import time

import httpx
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError

from config import AI_PROVIDER, API_KEY, MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL
from evaluator import choose_mode
from prompts import MODES, get_system_prompt


def startup_check() -> tuple[bool, str]:
    if AI_PROVIDER not in {"ollama", "openai"}:
        return False, "Invalid AI_PROVIDER. Use 'ollama' or 'openai'."

    if AI_PROVIDER == "openai":
        if not API_KEY:
            return (
                False,
                "OPENAI_API_KEY is not set. Set it in your environment before running.",
            )
        return True, ""

    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=8.0)
        response.raise_for_status()
    except httpx.ConnectError:
        return (
            False,
            f"Could not connect to Ollama at {OLLAMA_BASE_URL}. "
            "Start Ollama using: ollama serve",
        )
    except httpx.HTTPError as error:
        return False, f"Failed to check Ollama status: {error}"

    data = response.json()
    models = data.get("models", [])
    installed_names = {
        model.get("name", "") for model in models if isinstance(model, dict)
    }

    if OLLAMA_MODEL not in installed_names:
        return (
            False,
            f"Model '{OLLAMA_MODEL}' is not installed. Run: ollama pull {OLLAMA_MODEL}",
        )

    return True, ""


def generate_response_openai(
    user_input: str, selected_mode: str, system_prompt: str
) -> tuple[str, str]:
    if not API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it in your environment and run again."
        )

    client = OpenAI(api_key=API_KEY)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.7 if selected_mode == "creative" else 0.3,
            )
            break
        except APIConnectionError:
            if attempt == max_attempts:
                raise
            time.sleep(attempt)

    content = response.choices[0].message.content or ""
    return selected_mode, content.strip()


def generate_response_ollama(
    user_input: str, selected_mode: str, system_prompt: str
) -> tuple[str, str]:
    max_attempts = 3
    num_predict = 400 if selected_mode == "technical" else 512
    for attempt in range(1, max_attempts + 1):
        try:
            response = httpx.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7 if selected_mode == "creative" else 0.3,
                        "num_predict": num_predict,
                    },
                },
                timeout=180.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            return selected_mode, content.strip()
        except (httpx.ConnectError, httpx.ReadTimeout):
            if attempt == max_attempts:
                raise
            time.sleep(attempt)

    raise RuntimeError("Failed to get a response from Ollama.")


def generate_response(user_input: str, mode: str = "auto") -> tuple[str, str]:
    selected_mode = choose_mode(user_input) if mode == "auto" else mode
    system_prompt = get_system_prompt(selected_mode)

    if AI_PROVIDER == "ollama":
        return generate_response_ollama(user_input, selected_mode, system_prompt)
    if AI_PROVIDER == "openai":
        return generate_response_openai(user_input, selected_mode, system_prompt)

    raise ValueError("Invalid AI_PROVIDER. Use 'ollama' or 'openai'.")


def handle_prompt(user_input: str, mode: str) -> None:
    try:
        print("\nGenerating response... (press Ctrl+C to cancel)")
        selected_mode, answer = generate_response(user_input=user_input, mode=mode)
        print(f"\nMode used: {selected_mode}")
        print("\nResponse:\n")
        print(answer)
    except RuntimeError as error:
        print(f"\nConfiguration error: {error}")
    except ValueError as error:
        print(f"\nInput error: {error}")
    except AuthenticationError:
        print(
            "\nAuthentication failed: your OPENAI_API_KEY is invalid. "
            "Set a valid key and run again."
        )
    except RateLimitError:
        print("\nRate limit reached. Please wait and try again.")
    except APIConnectionError:
        print(
            "\nNetwork error: could not reach OpenAI after multiple retries. "
            "Check VPN/proxy/firewall and try again."
        )
    except httpx.ConnectError:
        print(
            "\nCould not connect to Ollama. Start Ollama app/service and ensure "
            f"it is reachable at {OLLAMA_BASE_URL}."
        )
    except httpx.HTTPStatusError as error:
        print(f"\nOllama HTTP error: {error}")
    except httpx.ReadTimeout:
        print("\nOllama request timed out. Try again or use a smaller model.")
    except APIError as error:
        print(f"\nOpenAI API error: {error}")
    except KeyboardInterrupt:
        print("\nRequest cancelled.")
    except Exception as error:
        print(f"\nUnexpected error: {error}")


def main() -> None:
    ok, message = startup_check()
    if not ok:
        print(f"Startup check failed: {message}")
        return

    print("AI Multi-Mode Response Engine")
    print(f"Provider: {AI_PROVIDER}")
    print(f"Available modes: auto, {', '.join(MODES.keys())}")
    mode = input("Select mode: ").strip().lower() or "auto"
    if mode != "auto" and mode not in MODES:
        valid_modes = ", ".join(MODES.keys())
        print(f"\nInput error: Invalid mode: {mode}. Use auto or one of: {valid_modes}")
        return

    print("\nType your prompt and press Enter.")
    print("Commands: /exit or /quit to stop, /clear to clear screen, /mode to change mode.\n")

    while True:
        try:
            user_input = input("Enter your prompt: ").strip()
        except KeyboardInterrupt:
            print("\nSession closed.")
            break

        if not user_input:
            print("Please enter a prompt.")
            continue

        command = user_input.lower()
        if command in {"/exit", "/quit"}:
            print("Goodbye.")
            break
        if command == "/clear":
            os.system("cls")
            continue
        if command == "/mode":
            new_mode = input("Select mode: ").strip().lower() or "auto"
            if new_mode != "auto" and new_mode not in MODES:
                valid_modes = ", ".join(MODES.keys())
                print(f"Input error: Invalid mode: {new_mode}. Use auto or one of: {valid_modes}")
                continue
            mode = new_mode
            print(f"Mode updated to: {mode}")
            continue

        handle_prompt(user_input=user_input, mode=mode)


if __name__ == "__main__":
    main()
