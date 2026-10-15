# NX Matrix AI — Microsoft Teams Bot

NX Matrix AI is a Python Microsoft Teams bot that sends incoming messages to an OpenAI-compatible Chat Completions API. It supports local Ollama models and compatible hosted LLM providers.

> **Current status:** Local conversation testing is intended for Microsoft 365 Agents Playground with the explicit local-only emulator mode below. Installing the bot in the real Teams client additionally requires registered bot credentials, a valid Teams app package, a publicly reachable HTTPS messaging endpoint, and a Microsoft 365 work or school tenant with the required permissions. A personal Microsoft account alone may not provide the tenant features required for custom app registration.

## Features

- Microsoft Teams message handling using `microsoft-teams-apps`.
- Configurable LLM base URL, API key, model, timeout, and system prompt.
- Ollama and hosted OpenAI-compatible provider support.
- Windows setup menu and launch scripts.
- API connectivity checker and automated Python tests.
- Optional Microsoft Dev Tunnels workflow for temporary HTTPS access.
- Local `.env` secrets excluded from ordinary Git additions.

## Requirements

- Windows 10 or 11; commands below use Command Prompt (CMD).
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

The setup script creates a local `.venv`, upgrades pip, installs dependencies, and creates `.env` from `.env.example` if it does not already exist. Existing `.env` settings are preserved. The menu lets you run the bot, test the LLM API, check dependencies/configuration, start a tunnel, edit `.env`, or exit.

### 3. Configure the LLM

Open `.env` in Notepad. The default configuration uses local Ollama:

```dotenv
API_BASE_URL=http://127.0.0.1:11434/v1
API_KEY=ollama
API_MODEL=qwen2.5:3b
API_TIMEOUT_SECONDS=120
BOT_PORT=3978
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

### 4. Choose a Teams authentication mode

**Local Agents Playground only:** leave `CLIENT_ID`, `CLIENT_SECRET`, and `TENANT_ID` empty, and explicitly uncomment this line in `.env`:

```dotenv
DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true
```

This bypasses Teams request authentication. Use it only when the bot is bound to your local machine for emulator testing. Never enable it while using a public tunnel or deploying to Teams.

**Authenticated Teams deployment:** configure valid `CLIENT_ID`, `CLIENT_SECRET`, and `TENANT_ID` values for your registered bot. Keep the unauthenticated setting absent or commented out. The tunnel script refuses to start unless all three credential values are present.

### 5. Test the LLM API settings

In `setup.bat`, choose **Test LLM API configuration**, or run:

```bat
.venv\Scripts\python.exe check_api.py
```

The check sends a small Chat Completions request and prints the provider response. It validates API connectivity; it does not test Teams authentication.

### 6. Start the bot locally

Run `setup.bat` and select **Run bot locally**, or run:

```bat
run_local.bat
```

Keep the terminal open. By default, the service listens on port 3978 and exposes the SDK messaging route at:

```text
http://localhost:3978/api/messages
```

### 7. Test with Agents Playground

1. Enable the local-only authentication bypass as described in step 4.
2. Start the bot with `run_local.bat` or setup menu option 1.
3. Open Microsoft 365 Agents Playground and configure the local endpoint above.
4. Select the local/emulator connection supported by your Playground version and send a text message.
5. When finished, stop the bot with Ctrl+C and remove/comment the local-only bypass before any tunnel or deployment use.

## Configuration reference

| Variable | Purpose | Example |
|---|---|---|
| `API_BASE_URL` | OpenAI-compatible API base URL | `http://127.0.0.1:11434/v1` |
| `API_KEY` | Provider key; local Ollama commonly uses a placeholder | `ollama` |
| `API_MODEL` | Model identifier | `qwen2.5:3b` |
| `API_TIMEOUT_SECONDS` | API request timeout | `120` |
| `BOT_PORT` | Local HTTP port used by bot and tunnel | `3978` |
| `SYSTEM_PROMPT` | System instruction sent with each user request | Professional assistant prompt |
| `CLIENT_ID` | Registered Teams bot/application ID | Supplied by your bot registration |
| `CLIENT_SECRET` | Registered bot secret | Keep private |
| `TENANT_ID` | Microsoft Entra tenant ID | Supplied by your tenant |
| `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` | Auth bypass for local emulator testing only | `true` only on localhost |

The code appends `/chat/completions` to `API_BASE_URL` unless that path is already present.

## Temporary HTTPS tunnel (development only)

A tunnel lets a remote service reach your local bot; it does not register or install the Teams app.

1. Configure valid `CLIENT_ID`, `CLIENT_SECRET`, and `TENANT_ID` values in `.env`.
2. Ensure `DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS` is absent or commented out.
3. Start the bot in one terminal and keep it running.
4. Open another Command Prompt and run `run_tunnel.bat` (or choose setup menu option 4).
5. Copy the generated HTTPS address and configure the registered bot endpoint as `https://YOUR-TUNNEL-HOST/api/messages`.
6. Keep both terminals open. Stop the tunnel when finished.

The helper creates an anonymous tunnel for development convenience; treat its URL as public. It blocks tunnel startup when bot credentials are missing or local unauthenticated mode is enabled. A newly created tunnel may receive a different URL, so update the registered messaging endpoint when it changes. Never expose Ollama's port 11434. Use properly secured hosted infrastructure for production.

## Connect to the real Microsoft Teams client

A working Agents Playground chat does not automatically add the bot to Teams. A real Teams deployment requires:

1. An eligible Microsoft 365 work or school tenant and permission to register/deploy Teams apps.
2. A registered bot/application identity with valid credentials and a correctly configured HTTPS messaging endpoint.
3. A valid Teams app manifest/package with the intended scopes configured.
4. Custom app upload or administrator deployment enabled.
5. SDK authentication configured with the registered app credentials and tenant.

A personal Microsoft account may not provide the necessary tenant developer features. If Teams CLI reports that its developer/tenant token is unavailable, resolve the tenant and permission requirement rather than repeatedly changing this Python application.

Microsoft resources: [Teams developer documentation](https://learn.microsoft.com/microsoftteams/platform/) · [Teams Developer Portal](https://dev.teams.microsoft.com/).

## Run tests

Install dependencies, then run:

```bat
.venv\Scripts\python.exe -m compileall -q src check_api.py tests
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m pip check
```

The unit tests mock LLM responses and do not require a live provider. Run `check_api.py` separately for a live local/hosted API connectivity test.

## Troubleshooting

### API connection fails

- For Ollama, confirm it is running and that the selected model appears in `ollama list`.
- Verify `API_BASE_URL`, `API_MODEL`, and the hosted provider's `API_KEY`.
- Run `check_api.py` from the project's virtual environment.

### LLM API returns HTTP 401/403

Check the API key, account permission, and model access.

### LLM API returns HTTP 404

Check the base URL and exact model ID. Confirm the provider supports an OpenAI-compatible Chat Completions endpoint.

### Bot says Teams credentials are missing

For local Playground testing, explicitly enable the local-only setting. For a public endpoint or real Teams, configure the registered bot credentials instead.

### Browser shows 404 at the tunnel root

The bot route is `/api/messages`; the root path `/` is not a user-facing web page. A browser GET request is not the same as an authenticated Teams POST request.

### Tunnel cannot connect to localhost

Start the bot first and keep it running. Then start the tunnel in a second terminal. The configured tunnel port must match `BOT_PORT`.

### Python dependency or startup errors

Run:

```bat
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the environment is corrupted, close the bot, delete `.venv`, and run `setup.bat` again. Preserve your local `.env` before removing anything.

## Security notes

- Never commit `.env`, keys, client secrets, certificates, or access tokens.
- `.gitignore` does not remove a secret already present in Git history. Revoke/rotate exposed credentials and audit the full history if a secret was pushed.
- Do not disable Teams authentication on an internet-exposed endpoint.
- Do not expose Ollama's port 11434 publicly.
- Temporary tunnels are not production hosting.

## Project structure

```text
nxmatrix-teams-ai/
├── .github/workflows/python-validation.yml
├── src/
│   └── main.py
├── tests/
│   └── test_main.py
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
