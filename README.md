# NX Matrix AI — Microsoft Teams Bot

NX Matrix AI is a Python Microsoft Teams bot that sends messages to an OpenAI-compatible Chat Completions API. It supports local Ollama models as well as compatible hosted LLM providers.

> **Current status:** The bot can be tested with Microsoft 365 Agents Playground. Installing it in the real Microsoft Teams client additionally requires a registered Teams bot/app identity, the correct messaging endpoint, and a Microsoft 365 work or school tenant with the necessary app permissions. A personal Microsoft account alone may not provide the developer tenant features required for registration.

## Features

- Microsoft Teams message handler built with `microsoft-teams-apps`.
- Configurable OpenAI-compatible LLM endpoint, API key, model, timeout, and system prompt.
- Local Ollama example configuration.
- Windows setup and launch scripts.
- API connectivity test utility.
- Optional Microsoft Dev Tunnels workflow for temporary HTTPS access.
- Secrets are kept in a local `.env` file, which should never be committed.

## Requirements

- Windows 10/11 (instructions below use Command Prompt).
- Python 3.12 or later.
- Git (to clone the repository).
- A running LLM endpoint:
  - **Local:** Ollama installed, running, and with the selected model downloaded; or
  - **Hosted:** an OpenAI-compatible provider base URL, API key, and model name.
- For tunnel testing: Microsoft Dev Tunnels CLI.
- For real Teams installation: a Teams app registration and a Microsoft 365 work/school tenant that permits custom app development/upload.

## Quick start on Windows

### 1. Download the project

Using Git:

```bat
git clone https://github.com/ns-matrix/nxmatrix-teams-ai.git
cd nxmatrix-teams-ai
```

Alternatively, download the repository ZIP from GitHub and extract it.

### 2. Run the setup script

Double-click `setup.bat`, or run it from Command Prompt:

```bat
setup.bat
```

The script creates a `.venv`, installs dependencies, and creates `.env` from `.env.example` if `.env` does not already exist. It preserves an existing `.env`.

### 3. Configure the LLM

Open `.env` in a text editor. The default local Ollama configuration is:

```dotenv
API_BASE_URL=http://127.0.0.1:11434/v1
API_KEY=ollama
API_MODEL=qwen2.5:3b
API_TIMEOUT_SECONDS=120
BOT_PORT=3978
SYSTEM_PROMPT=You are NX Matrix AI, a professional business assistant. Give clear, accurate, concise and useful answers.
```

Make sure Ollama is running and the selected model is available. For example, in a separate terminal:

```bat
ollama list
ollama pull qwen2.5:3b
```

If using a hosted provider, set its compatible API base URL, API key, and model. Example for OpenAI:

```dotenv
API_BASE_URL=https://api.openai.com/v1
API_KEY=your_real_api_key
API_MODEL=gpt-4o-mini
API_TIMEOUT_SECONDS=120
```

Use the exact model ID supported by your provider. Do not put a real API key in `.env.example`, source code, screenshots, issue reports, or Git commits.

### 4. Test the LLM connection

From the project folder, run:

```bat
check_config.bat
```

or run the check directly:

```bat
.venv\Scripts\python.exe check_api.py
```

A successful check prints the provider response. If it fails, verify the endpoint, key, model name, network access, and that the local Ollama service is running when using Ollama.

### 5. Start the bot

Use the setup menu and select **Run bot locally**, or launch:

```bat
run_local.bat
```

Keep the terminal open. The server should report that it is running. The default local service port is `3978`, but confirm the port actually bound by your installed version of the Teams SDK.

### 6. Test with Agents Playground

Open Microsoft 365 Agents Playground and configure the local endpoint:

```text
http://localhost:3978/api/messages
```

Select the emulator/local test connection when appropriate and send a message. The local test channel is not the same as a real Teams conversation. If Playground's emulator requires a specific authentication setting, follow the SDK/Playground instructions for local testing; do not disable authentication on an internet-exposed production endpoint.

## Configuration reference

| Variable | Meaning | Example |
|---|---|---|
| `API_BASE_URL` | Base URL of the OpenAI-compatible API | `http://127.0.0.1:11434/v1` |
| `API_KEY` | Provider key or placeholder for local Ollama | `ollama` |
| `API_MODEL` | Model identifier known to the provider | `qwen2.5:3b` |
| `API_TIMEOUT_SECONDS` | HTTP timeout in seconds | `120` |
| `BOT_PORT` | Desired bot server port for script/deployment configuration | `3978` |
| `SYSTEM_PROMPT` | Instructions sent before the user's message | A professional assistant prompt |

The `API_BASE_URL` may be provided with or without the trailing `/chat/completions` path. The bot adds that path when needed.

## Temporary HTTPS tunnel

A tunnel is useful when a remote service needs to reach your local bot. It does not register or install a Teams app.

1. Start the bot and keep its terminal open.
2. Open a **second** Command Prompt.
3. Run `run_tunnel.bat`, or use the Dev Tunnels CLI commands shown by the script.
4. Copy the generated HTTPS hostname and configure the remote bot messaging endpoint as:

   `https://YOUR-TUNNEL-HOST/api/messages`

5. Keep both the local server and tunnel running while testing.

The tunnel script uses anonymous access for development convenience. Treat its URL as public, use it only for temporary testing, do not expose Ollama's port 11434, and stop the tunnel when finished. Use authenticated and appropriately hosted infrastructure for production. Tunnel URLs may change when a new tunnel is created.

## Connecting to the real Microsoft Teams client

A working Agents Playground conversation does not automatically make the bot appear in Teams. For a real Teams installation you still need:

1. An eligible Microsoft 365 work or school tenant and appropriate permissions.
2. A registered bot/app identity with the required messaging endpoint.
3. A valid Teams app manifest/package with personal scope configured.
4. Custom app upload or admin deployment enabled in that tenant.
5. A publicly reachable HTTPS endpoint while the bot is running.

The endpoint for local tunnel testing is the current Dev Tunnel URL plus `/api/messages`; do not permanently hardcode an expired tunnel URL in the repository. A personal Microsoft account may be insufficient for tenant-based Teams app registration. If the CLI cannot obtain its developer/tenant token, resolve the tenant-access prerequisite rather than repeatedly changing the Python code.

See Microsoft's [Teams developer documentation](https://learn.microsoft.com/microsoftteams/platform/) and [Teams Developer Portal](https://dev.teams.microsoft.com/).

## Troubleshooting

### `NX Matrix AI cannot connect to the configured LLM provider`

- For Ollama, confirm the app is running and `http://127.0.0.1:11434` is reachable.
- Check that `API_BASE_URL` is correct and includes `/v1` when required.
- Run `check_config.bat` and inspect the resulting error.

### HTTP 401 or 403 from the LLM provider

Check `API_KEY`, provider account access, and whether the selected model is available to that key.

### HTTP 404 from the LLM provider

Check `API_BASE_URL` and the exact `API_MODEL` identifier.

### Browser shows `404 Not Found` at the tunnel root

The bot messaging route is `/api/messages`; the root route `/` is not a website and may return 404. A browser GET request is also not the same as an authenticated Teams messaging POST.

### Tunnel reports it cannot connect to localhost

Start the Python bot first and verify the server is listening on port 3978, then start the tunnel in a second terminal. Do not stop the bot terminal while testing.

### Bot fails to start after updating dependencies

From the project directory, run:

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If necessary, delete the local `.venv` and run `setup.bat` again. Keep your existing `.env` backed up locally.

## Security

- Never commit `.env`, provider keys, client secrets, certificates, or access tokens.
- `.gitignore` prevents normal additions but does not remove secrets already committed in Git history.
- If a secret has been pushed, revoke/rotate it with the provider and audit repository history.
- Do not disable Teams authentication for publicly reachable endpoints.
- Do not expose the Ollama API to the public internet.
- Development tunnels are temporary and should not be treated as production hosting.

## Project structure

```text
nxmatrix-teams-ai/
├── src/
│   └── main.py
├── .env.example
├── .gitignore
├── check_api.py
├── check_config.bat
├── requirements.txt
├── pyproject.toml
├── run_local.bat
├── run_tunnel.bat
├── setup.bat
└── README.md
```

## License

See [LICENSE](LICENSE).
