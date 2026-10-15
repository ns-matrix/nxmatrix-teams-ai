# NX Matrix AI — Microsoft Teams Bot

NX Matrix AI is a Python Microsoft Teams bot that sends incoming messages to an OpenAI-compatible Chat Completions API. It supports local Ollama models and compatible hosted LLM providers.

> **Current status:** Local conversation testing works with Microsoft 365 Agents Playground when its authentication setup is configured appropriately. Installing the bot in the real Teams client additionally requires a registered bot/app identity, a valid Teams app package, a publicly reachable HTTPS messaging endpoint, and a Microsoft 365 work or school tenant with the required permissions. A personal Microsoft account alone may not provide the tenant features required for custom app registration.

## Features

- Microsoft Teams message handling using `microsoft-teams-apps`.
- Configurable LLM base URL, API key, model, timeout, and system prompt.
- Ollama and hosted OpenAI-compatible provider support.
- Windows setup menu and launch scripts.
- API connectivity checker.
- Optional Microsoft Dev Tunnels workflow for temporary HTTPS access.
- Local `.env` secrets excluded from ordinary Git additions.

## Requirements

- Windows 10 or 11; the commands below use Command Prompt (CMD).
- Python 3.12 or later, installed and available as `python`.
- Git, if cloning the repository.
- Ollama with a model downloaded, or an OpenAI-compatible hosted API URL, API key, and model.
- Microsoft Dev Tunnels CLI only if you need a temporary public HTTPS endpoint.
- Real Teams installation requires a suitable Microsoft 365 work/school tenant and custom app permissions.

## Quick start (Windows)

### 1. Clone the project

Open Command Prompt and run:

```bat
git clone https://github.com/ns-matrix/nxmatrix-teams-ai.git
cd nxmatrix-teams-ai
```

Or download the ZIP from GitHub and extract it.

### 2. Run setup

```bat
setup.bat
```

The setup script creates a local `.venv`, updates pip, installs the dependencies, and creates `.env` from `.env.example` if it does not already exist. Existing `.env` settings are preserved.

### 3. Configure the LLM

Open `.env` in Notepad. The default configuration uses local Ollama:

```dotenv
API_BASE_URL=http://127.0.0.1:11434/v1
API_KEY=ollama
API_MODEL=qwen2.5:3b
API_TIMEOUT_SECONDS=120
BOT_PORT=3978
SYSTEM_PROMPT=You are NX Matrix AI, a professional business assistant. Give clear, accurate, concise and useful answers.
```

Ensure Ollama is installed and running. To inspect models or download the default:

```bat
ollama list
ollama pull qwen2.5:3b
```

For a hosted OpenAI-compatible provider, replace the values locally in `.env`. Example:

```dotenv
API_BASE_URL=https://api.openai.com/v1
API_KEY=your_real_api_key
API_MODEL=gpt-4o-mini
API_TIMEOUT_SECONDS=120
BOT_PORT=3978
```

Use the model identifier supported by your provider. Never put a real key in `.env.example`, source files, screenshots, public issue reports, or commits.

### 4. Test the API settings

In the project folder, choose **Test LLM API configuration** in the setup menu, or run:

```bat
.venv\Scripts\python.exe check_api.py
```

The check sends a small Chat Completions request and prints the provider response. It validates API connectivity; it does not test Teams authentication.

### 5. Start the bot locally

Run `setup.bat` and select **Run bot locally**, or run:

```bat
run_local.bat
```

Keep the terminal open. By default the service listens on port 3978 and exposes the SDK's messaging route at:

```text
http://localhost:3978/api/messages
```

### 6. Test with Agents Playground

Open Microsoft 365 Agents Playground and configure the local endpoint above. Select the local/emulator connection supported by your Playground version and send a text message.

If the Playground cannot authenticate to your local bot, it may require an explicit emulator-only unauthenticated setting. In `.env`, uncomment:

```dotenv
DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true
```

Use this only for local emulator testing. Restart the bot after changing it. **Do not start a public tunnel or expose the bot while this setting is enabled.** Re-comment/remove the setting before testing through a public endpoint or using production credentials. SDK authentication is enabled by default.

## Configuration reference

| Variable | Purpose | Example |
|---|---|---|
| `API_BASE_URL` | OpenAI-compatible API base URL | `http://127.0.0.1:11434/v1` |
| `API_KEY` | Provider key; local Ollama commonly uses a placeholder | `ollama` |
| `API_MODEL` | Model identifier | `qwen2.5:3b` |
| `API_TIMEOUT_SECONDS` | API request timeout | `120` |
| `BOT_PORT` | Local HTTP port | `3978` |
| `SYSTEM_PROMPT` | System instruction sent with each user request | Professional assistant prompt |
| `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` | SDK auth bypass for isolated local emulator testing only | `true` (do not use with a tunnel) |

The code appends `/chat/completions` to `API_BASE_URL` unless that path is already present.

## Temporary HTTPS tunnel (development only)

A tunnel lets a remote service reach your local bot; it does not register or install the Teams app.

1. Make sure the bot is running in a separate terminal.
2. Ensure `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` is **not** set to `true`.
3. Open another Command Prompt and run `run_tunnel.bat`.
4. Copy the generated HTTPS address.
5. Configure the registered bot endpoint as `https://YOUR-TUNNEL-HOST/api/messages`.
6. Keep the bot and tunnel terminals open during the test.

The tunnel helper uses anonymous tunnel access for development convenience; treat its URL as public, stop it when finished, and never expose Ollama's port 11434. Do not use the local emulator's unauthenticated mode through a public tunnel. Use properly authenticated and hosted infrastructure for production.

## Connect to the real Microsoft Teams client

A working Agents Playground chat does not automatically add the bot to Teams. A real Teams deployment requires:

1. An eligible Microsoft 365 work or school tenant and permission to register/deploy Teams apps.
2. A registered bot/app identity and correct HTTPS messaging endpoint.
3. A valid Teams app manifest/package with personal scope configured.
4. Custom app upload or administrator deployment enabled.
5. SDK authentication configured with the registered app credentials/tenant.

A personal Microsoft account may not provide the necessary tenant developer features. If Teams CLI reports that its developer/tenant token is unavailable, resolve the tenant and permission requirement rather than repeatedly changing this Python application.

Microsoft resources: [Teams developer documentation](https://learn.microsoft.com/microsoftteams/platform/) · [Teams Developer Portal](https://dev.teams.microsoft.com/).

## Troubleshooting

### API connection fails

- For Ollama, confirm it is running and that the selected model appears in `ollama list`.
- Verify `API_BASE_URL`, `API_MODEL`, and the hosted provider's `API_KEY`.
- Run `check_api.py` from the project's virtual environment.

### LLM API returns HTTP 401/403

Check the API key, account permission, and model access.

### LLM API returns HTTP 404

Check the base URL and exact model ID. Confirm the provider supports an OpenAI-compatible Chat Completions endpoint.

### Browser shows 404 at the tunnel root

The bot route is `/api/messages`; the root path `/` is not a user-facing web page. A browser GET request is not the same as an authenticated Teams POST request.

### Tunnel cannot connect to localhost

Start the bot first and make sure it remains running. Then start the tunnel in a second terminal. The configured tunnel port must match `BOT_PORT`.

### Python dependency or startup errors

Run:

```bat
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the environment is corrupted, close the bot, delete `.venv`, and run `setup.bat` again. Keep your local `.env` before removing anything.

## Security notes

- Never commit `.env`, keys, client secrets, certificates, or access tokens.
- `.gitignore` does not remove a secret already present in Git history. Revoke/rotate exposed credentials and audit the full history if a secret was pushed.
- Do not disable Teams authentication on an internet-exposed endpoint.
- Do not expose Ollama's port 11434 publicly.
- Temporary tunnels are not production hosting.

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
