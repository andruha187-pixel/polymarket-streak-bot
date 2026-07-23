import os


def env_str(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)

    if value is None or value == "":
        raise RuntimeError(
            f"Environment variable {name} is not set"
        )

    return value


TELEGRAM_BOT_TOKEN = env_str(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = env_str(
    "TELEGRAM_CHAT_ID"
)


GAMMA_API_URL = os.getenv(
    "GAMMA_API_URL",
    "https://gamma-api.polymarket.com"
)


POLL_INTERVAL_SECONDS = int(
    os.getenv(
        "POLL_INTERVAL_SECONDS",
        "20"
    )
)


STREAK_TRIGGER = int(
    os.getenv(
        "STREAK_TRIGGER",
        "5"
    )
)


INITIAL_BALANCE = float(
    os.getenv(
        "INITIAL_BALANCE",
        "100"
    )
)


BASE_BET = float(
    os.getenv(
        "BASE_BET",
        "1"
    )
)


MAX_BET = float(
    os.getenv(
        "MAX_BET",
        "16"
    )
)


MAX_LOSS_STREAK = int(
    os.getenv(
        "MAX_LOSS_STREAK",
        "4"
    )
)


PAPER_TRADING_ENABLED = (
    os.getenv(
        "PAPER_TRADING_ENABLED",
        "true"
    ).lower()
    == "true"
)


STATE_FILE = os.getenv(
    "STATE_FILE",
    "/tmp/state.json"
)
)


TELEGRAM_API_URL = (
    "https://api.telegram.org/bot"
    + TELEGRAM_BOT_TOKEN
)
