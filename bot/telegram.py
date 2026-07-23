import logging

import requests

from .config import (
    TELEGRAM_API_URL,
    TELEGRAM_CHAT_ID,
)


logger = logging.getLogger(
    __name__
)


def send_message(
    text: str
) -> bool:

    url = (
        f"{TELEGRAM_API_URL}"
        "/sendMessage"
    )


    payload = {

        "chat_id": TELEGRAM_CHAT_ID,

        "text": text,

        "parse_mode": "HTML",

        "disable_web_page_preview": True,
    }


    try:

        response = requests.post(
            url,
            json=payload,
            timeout=30
        )


        response.raise_for_status()


        return True


    except Exception:

        logger.exception(
            "Telegram send error"
        )


        return False


def format_streak_alert(
    alert: dict
) -> str:

    coin = alert[
        "coin"
    ]


    outcome = alert[
        "outcome"
    ]


    history = alert[
        "history"
    ]


    opposite = (
        "NO"
        if outcome == "YES"
        else "YES"
    )


    sequence = " → ".join(
        history
    )


    question = alert[
        "market"
    ].get(
        "question",
        ""
    )


    return (

        "🚨 <b>СИГНАЛ: 5 ОДИНАКОВЫХ "
        "РЕЗУЛЬТАТОВ ПОДРЯД</b>\n\n"

        f"🪙 Монета: <b>{coin}</b>\n"

        f"📊 Серия: <b>{outcome}</b> × "
        f"<b>{len(history)}</b>\n\n"

        f"<code>{sequence}</code>\n\n"

        f"🎯 Виртуальная ставка против серии: "
        f"<b>{opposite}</b>\n"

        f"💵 Начальная ставка: <b>1 USDC</b>\n\n"

        f"❓ {question}"
    )


def format_trade_result(
    result: dict
) -> str:

    coin = result[
        "coin"
    ]


    result_type = result[
        "type"
    ]


    if result_type == "WIN":

        return (

            "✅ <b>PAPER TRADE WIN</b>\n\n"

            f"🪙 {coin}\n"

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


    if result_type == "LOSS":

        return (

            "❌ <b>PAPER TRADE LOSS</b>\n\n"

            f"🪙 {coin}\n"

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

        "🛑 <b>PAPER TRADE STOPPED</b>\n\n"

        f"🪙 {coin}\n"

        f"📌 Результат: "
        f"<b>{result['actual_outcome']}</b>\n\n"

        f"💸 Потеря: "
        f"<b>-{result['loss']:.2f}</b>\n"

        "⚠️ Лимит мартингейла достигнут.\n\n"

        f"💰 Баланс: "
        f"<b>{result['balance']:.2f}</b> USDC"
    )


def format_stats(
    stats: dict
) -> str:

    return (

        "📊 <b>PAPER TRADING СТАТИСТИКА</b>\n\n"

        f"💰 Начальный баланс: "
        f"<b>{stats['initial_balance']:.2f}</b>\n"

        f"💵 Текущий баланс: "
        f"<b>{stats['balance']:.2f}</b>\n\n"

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
    active_trades: dict
) -> str:

    text = (

        "📡 <b>STATUS</b>\n\n"

        f"💰 Баланс: "
        f"<b>{stats['balance']:.2f}</b> USDC\n"

        f"📈 P&L: "
        f"<b>{stats['total_profit']:+.2f}</b>\n\n"

        f"🎯 Всего ставок: "
        f"<b>{stats['total_bets']}</b>\n"

        f"🔄 Активных сделок: "
        f"<b>{len(active_trades)}</b>\n"
    )


    if active_trades:

        text += "\n<b>АКТИВНЫЕ СДЕЛКИ:</b>\n"


        for coin, trade in active_trades.items():

            text += (

                f"\n🪙 {coin}\n"

                f"🎯 Ставка: "
                f"{trade['bet_outcome']}\n"

                f"💵 Размер: "
                f"{trade['bet_size']}\n"

                f"🔥 Loss streak: "
                f"{trade['loss_streak']}\n"
            )


    return text


def get_updates(
    offset: int | None = None
) -> list:

    url = (
        f"{TELEGRAM_API_URL}"
        "/getUpdates"
    )


    params = {

        "timeout": 1,

        "allowed_updates": [
            "message"
        ],
    }


    if offset is not None:

        params[
            "offset"
        ] = offset


    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )


        response.raise_for_status()


        data = response.json()


        if data.get(
            "ok"
        ):

            return data.get(
                "result",
                []
            )


    except Exception:

        logger.exception(
            "Telegram getUpdates error"
        )


    return []