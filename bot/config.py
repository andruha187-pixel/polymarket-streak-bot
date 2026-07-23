import os


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Environment variable {name} is not set"
        )

    return value


TELEGRAM_BOT_TOKEN = get_required_env(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = get_required_env(
    "TELEGRAM_CHAT_ID"
)


# =========================
# POLYMARKET
# =========================

GAMMA_API_URL = os.getenv(
    "GAMMA_API_URL",
    "https://gamma-api.polymarket.com"
)


# =========================
# BOT SETTINGS
# =========================

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


HISTORY_LENGTH = int(
    os.getenv(
        "HISTORY_LENGTH",
        "20"
    )
)


# =========================
# PAPER TRADING
# =========================

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
        "32"
    )
)


MAX_LOSS_STREAK = int(
    os.getenv(
        "MAX_LOSS_STREAK",
        "10"
    )
)


PAPER_TRADING_ENABLED = (
    os.getenv(
        "PAPER_TRADING_ENABLED",
        "true"
    ).lower()
    == "true"
)


# =========================
# STORAGE
# =========================

STATE_FILE = os.getenv(
    "STATE_FILE",
    "data/state.json"
)


# =========================
# TELEGRAM
# =========================

TELEGRAM_API_URL = (
    "https://api.telegram.org/bot"
    f"{TELEGRAM_BOT_TOKEN}"
)