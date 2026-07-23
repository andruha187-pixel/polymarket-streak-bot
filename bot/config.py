import os


GAMMA_API_URL = os.getenv(
    "GAMMA_API_URL",
    "https://gamma-api.polymarket.com"
)


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
)


TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
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
