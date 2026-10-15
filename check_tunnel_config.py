"""Validate the environment before exposing the bot through a public tunnel."""

import sys
from dotenv import dotenv_values

config = dotenv_values(".env")
credentials = ("CLIENT_ID", "CLIENT_SECRET", "TENANT_ID")
missing = [name for name in credentials if not (config.get(name) or "").strip()]
if missing:
    print("ERROR: Public tunneling requires configured Teams bot credentials: " + ", ".join(missing))
    print("Register a Teams bot and configure these values in .env first.")
    sys.exit(1)

allow_unauthenticated = (config.get("DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS") or "").strip().strip('"').strip("'").lower()
if allow_unauthenticated in {"1", "true", "yes", "on"}:
    print("ERROR: Unauthenticated local emulator mode is enabled.")
    print("Remove or comment out DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS before tunneling.")
    sys.exit(1)

port = (config.get("BOT_PORT") or "3978").strip()
try:
    port_number = int(port)
    if not 1 <= port_number <= 65535:
        raise ValueError
except ValueError:
    print("ERROR: BOT_PORT must be an integer between 1 and 65535.")
    sys.exit(1)

print(f"Tunnel safety checks passed. Forwarding the authenticated bot on port {port_number}.")
