import logging

import requests

from .config import (
    TELEGRAM_API_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


logger = logging.getLogger(__name__)


def get_api_url(method: str) -> str:
    return (
        f"{TELEGRAM_API_URL.rstrip('/')}"
        f"/bot{TELEGRAM_BOT_TOKEN}"
        f"/{method}"
    )


def send_message(text: str) -> bool:
    try:
        response = requests.post(
            get_api_url("sendMessage"),
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )

        response.raise_for_status()

        return True

    except Exception:
        logger.exception(
            "Telegram send error"
        )

        return False


def get_updates(
    offset: int | None,
) -> list[dict]:

    params = {
        "timeout": 1,
        "allowed_updates": [
            "message"
        ],
    }

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(
            get_api_url("getUpdates"),
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("ok"):
            return data.get(
                "result",
                [],
            )

    except Exception:
        logger.exception(
            "Telegram update error"
        )

    return []


def format_streak_alert(
    alert: dict,
) -> str:

    coin = alert["coin"]

    outcome = alert["outcome"]

    opposite = (
        "NO"
        if outcome == "YES"
        else "YES"
    )

    sequence = " → ".join(
        alert["history"]
    )

    return (
        "🚨 <b>СЕРИЯ 5 ПОДРЯД</b>\n\n"

        f"🪙 Монета: <b>{coin}</b>\n"

        f"📊 Серия: "
        f"<b>{outcome}</b> × "
        f"<b>{len(alert['history'])}</b>\n\n"

        f"<code>{sequence}</code>\n\n"

        f"🎯 PAPER TRADE: "
        f"<b>{opposite}</b>\n"

        f"💵 Ставка: "
        f"<b>1 USDC</b>"
    )


def format_open_trade(
    trade: dict,
) -> str:

    return (
        "🎯 <b>ВИРТУАЛЬНАЯ СТАВКА ОТКРЫТА</b>\n\n"

        f"🪙 {trade['coin']}\n"

        f"📊 После серии: "
        f"<b>{trade['signal_outcome']}</b>\n"

        f"🎯 Ставка: "
        f"<b>{trade['bet_outcome']}</b>\n"

        f"💵 Размер: "
        f"<b>{trade['bet_size']:.2f}</b> USDC"
    )


def format_trade_result(
    result: dict,
) -> str:

    if result["type"] == "WIN":

        return (
            "✅ <b>PAPER TRADE WIN</b>\n\n"

            f"🪙 {result['coin']}\n"

            f"🎯 Ставка: "
            f"<b>{result['bet_outcome']}</b>\n"

            f"📌 Результат: "
            f"<b>{result['actual_outcome']}</b>\n\n"

            f"💵 Ставка: "
            f"<b>{result['bet_size']:.2f}</b>\n"

            f"📈 Прибыль: "
            f"<b>+{result['profit']:.2f}</b>\n\n"

            f"💰 Баланс: "
            f"<b>{result['balance']:.2f}</b> USDC"
        )

    if result["type"] == "LOSS":

        return (
            "❌ <b>PAPER TRADE LOSS</b>\n\n"

            f"🪙 {result['coin']}\n"

            f"🎯 Ставка: "
            f"<b>{result['bet_outcome']}</b>\n"

            f"📌 Результат: "
            f"<b>{result['actual_outcome']}</b>\n\n"

            f"💸 Потеря: "
            f"<b>-{result['loss']:.2f}</b>\n"

            f"🔁 Следующая ставка: "
            f"<b>{result['next_bet']:.2f}</b>\n"

            f"🔥 Проигрышей подряд: "
            f"<b>{result['loss_streak']}</b>\n\n"

            f"💰 Баланс: "
            f"<b>{result['balance']:.2f}</b> USDC"
        )

    return (
        "🛑 <b>МАРТИНГЕЙЛ ОСТАНОВЛЕН</b>\n\n"

        f"🪙 {result['coin']}\n"

        f"📌 Результат: "
        f"<b>{result['actual_outcome']}</b>\n\n"

        f"💸 Потеря: "
        f"<b>-{result['loss']:.2f}</b>\n"

        "⚠️ Достигнут установленный лимит.\n\n"

        f"💰 Баланс: "
        f"<b>{result['balance']:.2f}</b> USDC"
    )


def format_stats(
    stats: dict,
) -> str:

    return (
        "📊 <b>PAPER TRADING</b>\n\n"

        f"💰 Начальный баланс: "
        f"<b>{stats['initial_balance']:.2f}</b>\n"

        f"💵 Текущий баланс: "
        f"<b>{stats['balance']:.2f}</b>\n"

        f"📈 P&L: "
        f"<b>{stats['total_profit']:+.2f}</b>\n\n"

        f"🎯 Всего ставок: "
        f"<b>{stats['total_bets']}</b>\n"

        f"✅ Побед: "
        f"<b>{stats['wins']}</b>\n"

        f"❌ Проигрышей: "
        f"<b>{stats['losses']}</b>\n"

        f"📊 Win rate: "
        f"<b>{stats['win_rate']:.2f}%</b>\n\n"

        f"🔥 Макс. серия проигрышей: "
        f"<b>{stats['max_loss_streak']}</b>\n"

        f"💸 Макс. ставка: "
        f"<b>{stats['max_bet']:.2f}</b>\n"

        f"🔄 Активных сделок: "
        f"<b>{stats['active_trades']}</b>"
    )


def format_status(
    stats: dict,
    active_trades: dict,
) -> str:

    text = (
        "📡 <b>STATUS</b>\n\n"

        f"💰 Баланс: "
        f"<b>{stats['balance']:.2f}</b> USDC\n"

        f"📈 P&L: "
        f"<b>{stats['total_profit']:+.2f}</b>\n"

        f"🔄 Активных сделок: "
        f"<b>{len(active_trades)}</b>\n"
    )

    for coin, trade in active_trades.items():

        text += (
            f"\n🪙 <b>{coin}</b>\n"

            f"🎯 {trade['bet_outcome']}\n"

            f"💵 {trade['bet_size']:.2f} USDC\n"

            f"🔥 Loss streak: "
            f"{trade['loss_streak']}\n"
        )

    return text
