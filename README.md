# Polymarket Streak Paper Trading Bot

Telegram bot for monitoring Polymarket 5-minute crypto markets.

## Strategy

1. Detect 5 identical YES/NO results in a row.
2. Open a virtual trade in the opposite direction.
3. Initial bet: 1 USDC.
4. After LOSS:
   1 → 2 → 4 → 8 → 16 → 32
5. After WIN:
   return to 1 USDC.

## Commands

/start
/stats
/status
/reset
/help

## Environment Variables

TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
POLL_INTERVAL_SECONDS
STREAK_TRIGGER
INITIAL_BALANCE
BASE_BET
MAX_BET
MAX_LOSS_STREAK
PAPER_TRADING_ENABLED
STATE_FILE
