# AI Multi-Mode Response Engine

A CLI assistant that supports multiple response styles (`concise`, `detailed`, `creative`, `technical`) with:
- `auto` mode selection based on prompt content
- provider routing (`ollama` local/free by default, optional `openai`)
- startup health checks
- interactive chat commands

## Features

- Multi-mode responses:
  - `concise`
  - `detailed`
  - `creative`
  - `technical`
- `auto` mode selection using keyword-based evaluator
- Providers:
  - `ollama` (default)
  - `openai`
- Reliability:
  - retry handling
  - timeout handling
  - clear error messages
- Interactive commands:
  - `/mode` change active mode
  - `/clear` clear terminal
  - `/exit` or `/quit` end session

## Project Files

- `main.py`: CLI app, provider routing, startup checks, retries, commands
- `config.py`: environment-based configuration
- `prompts.py`: system prompts for each mode
- `evaluator.py`: auto mode selection logic

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`
- For local/free usage: Ollama installed (`https://ollama.com/download`)

## Installation

```powershell
cd C:\Users\FIROS\ai-multi-mode-engine
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run (Ollama - recommended/free)

1. Pull a model once:

```powershell
ollama pull phi3:mini
```

2. Run app:

```powershell
cd C:\Users\FIROS\ai-multi-mode-engine
$env:AI_PROVIDER="ollama"
$env:OLLAMA_MODEL="phi3:mini"
.\venv\Scripts\python.exe .\main.py
```

Or run with helper script:

```powershell
.\run.ps1
```

## Run (OpenAI - optional)

```powershell
cd C:\Users\FIROS\ai-multi-mode-engine
$env:AI_PROVIDER="openai"
$env:OPENAI_API_KEY="your_key_here"
$env:OPENAI_MODEL="gpt-4o-mini"
.\venv\Scripts\python.exe .\main.py
```

Or run with helper script:

```powershell
.\run.ps1 -Provider openai -OpenAIApiKey "your_key_here" -Model "gpt-4o-mini"
```

## Run Website (Browser UI)

```powershell
cd C:\Users\FIROS\ai-multi-mode-engine
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe .\web_app.py
```

Open:

```text
http://127.0.0.1:5000
```

Website includes:
- mode selection
- chat history panel
- `Clear Chat` button
- context-aware replies using recent conversation history

## Screenshots and Demo

Add your media files to `assets/screenshots/` and `assets/demo/` using the names below.
Once added, they will render automatically on GitHub.

### Web UI

![Web UI Main](assets/screenshots/web-ui-main.png)
![Web UI Login](assets/screenshots/web-ui-login.png)

### CLI Demo

![CLI Demo](assets/screenshots/cli-demo.png)

### App Walkthrough (GIF)

![App Walkthrough](assets/demo/app-walkthrough.gif)

## Website Authentication

Enable login protection by setting:

```powershell
$env:WEB_AUTH_ENABLED="true"
$env:WEB_USERNAME="admin"
$env:WEB_PASSWORD="your_strong_password"
$env:WEB_SECRET_KEY="your_random_secret"
```

Then start website:

```powershell
.\venv\Scripts\python.exe .\web_app.py
```

Open `http://127.0.0.1:5000` and sign in.

## Startup Checks

At launch, the app verifies configuration before prompting:

- `AI_PROVIDER` is valid (`ollama` or `openai`)
- OpenAI mode:
  - `OPENAI_API_KEY` is set
- Ollama mode:
  - Ollama server reachable at `OLLAMA_BASE_URL`
  - configured model (`OLLAMA_MODEL`) is installed locally

If a check fails, the app exits with a clear fix command.

## Usage

1. Start app
2. Select mode: `auto`, `concise`, `detailed`, `creative`, `technical`
3. Enter prompts continuously
4. Use commands:
   - `/mode`
   - `/clear`
   - `/exit`

## Demo Session

```text
PS C:\Users\FIROS\ai-multi-mode-engine> .\venv\Scripts\python.exe .\main.py
AI Multi-Mode Response Engine
Provider: ollama
Available modes: auto, concise, detailed, creative, technical
Select mode: auto

Type your prompt and press Enter.
Commands: /exit or /quit to stop, /clear to clear screen, /mode to change mode.

Enter your prompt: what is ai

Generating response... (press Ctrl+C to cancel)

Mode used: detailed

Response:
Artificial Intelligence (AI) is the ability of computer systems to perform tasks
that usually require human intelligence, such as understanding language,
recognizing patterns, and making decisions.

Enter your prompt: /mode
Select mode: concise
Mode updated to: concise

Enter your prompt: blockchain in 2 lines

Generating response... (press Ctrl+C to cancel)

Mode used: concise

Response:
Blockchain is a shared digital ledger where records are grouped into linked blocks.
It is tamper-resistant and useful for secure, transparent transactions.

Enter your prompt: /exit
Goodbye.
```

## Environment Variables

- `AI_PROVIDER` (default: `ollama`)
- `OLLAMA_MODEL` (default: `llama3.2`)
- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `OPENAI_API_KEY` (required only for `openai`)
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `WEB_AUTH_ENABLED` (default: `false`)
- `WEB_USERNAME` (default: `admin`)
- `WEB_PASSWORD` (default: `admin123`)
- `WEB_SECRET_KEY` (default: `change-this-secret-key`)

## Troubleshooting

- Startup check says Ollama not reachable:
  - run `ollama serve`
- Startup check says model missing:
  - run `ollama pull <model_name>`
- Slow technical answers:
  - use `phi3:mini`
  - shorten prompt
  - use `concise` or `detailed` mode for faster responses

## Quick Start (PowerShell)

Use these exact commands in order:

```powershell
cd C:\Users\FIROS\ai-multi-mode-engine
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

If PowerShell blocks scripts (`run.ps1 cannot be loaded`), use a one-time bypass for the current shell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Run CLI with Ollama:

```powershell
.\run.ps1
```

Run Web UI without login:

```powershell
$env:WEB_AUTH_ENABLED="false"
.\venv\Scripts\python.exe .\web_app.py
```

Run Web UI with login:

```powershell
$env:WEB_AUTH_ENABLED="true"
$env:WEB_USERNAME="admin"
$env:WEB_PASSWORD="admin123"
$env:WEB_SECRET_KEY="replace-with-random-secret"
.\venv\Scripts\python.exe .\web_app.py
```

Open in browser:

```text
http://localhost:5000
```

`.env.example` is included as a variable reference template.
