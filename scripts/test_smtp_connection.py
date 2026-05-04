import os
import re
import smtplib
import socket
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "api" / ".env")


def normalize_smtp_password(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if re.fullmatch(r"(?:[A-Za-z0-9]{4}\s+){3}[A-Za-z0-9]{4}", normalized):
        return re.sub(r"\s+", "", normalized)

    return normalized


def mask(value: str | None) -> str:
    if not value:
        return "<missing>"
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * max(4, len(value) - 4)}{value[-2:]}"


def main() -> int:
    host = (os.getenv("SMTP_HOST") or "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    username = (os.getenv("SMTP_USERNAME") or "").strip()
    password = normalize_smtp_password(os.getenv("SMTP_PASSWORD"))
    use_tls = (os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"})
    use_ssl = (os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes", "on"})

    print("SMTP configuration")
    print(f"  host: {host or '<missing>'}")
    print(f"  port: {port}")
    print(f"  username: {mask(username)}")
    print(f"  password_present: {'yes' if password else 'no'}")
    print(f"  use_tls: {use_tls}")
    print(f"  use_ssl: {use_ssl}")

    if not host or not username or not password:
        print("Missing SMTP configuration. Check .env values.")
        return 1

    timeout = 20

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=timeout)
        else:
            server = smtplib.SMTP(host, port, timeout=timeout)

        with server:
            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()
            server.login(username, password)

        print("SMTP login succeeded.")
        return 0
    except (socket.gaierror, TimeoutError) as exc:
        print(f"Network/connectivity error: {exc}")
        return 2
    except smtplib.SMTPAuthenticationError as exc:
        print(f"SMTP authentication failed: {exc.smtp_code} {exc.smtp_error!r}")
        return 3
    except smtplib.SMTPException as exc:
        print(f"SMTP error: {exc}")
        return 4
    except Exception as exc:
        print(f"Unexpected error: {exc}")
        return 5


if __name__ == "__main__":
    sys.exit(main())
