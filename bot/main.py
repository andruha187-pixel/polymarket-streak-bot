import logging
import time

from .config import (
    PAPER_TRADING_ENABLED,
    POLL_INTERVAL_SECONDS,
)
from .paper_trading import (
    PaperTrader,
)
from .polymarket import (
    get_recent_closed_markets,
)
from .telegram import (
    format_stats,
    format_status,
    format_streak_alert,
    format_trade_result,
    get_updates,
    send_message,
)
from .tracker import (
    StreakTracker,
)


logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    ),
)


logger = logging.getLogger(
    __name__
)


def main():

    logger.info(
        "Polymarket Paper Trading Bot started"
    )


    tracker = StreakTracker()


    trader = PaperTrader()


    telegram_offset = None


    last_market_check = 0


    while True:

        try:

            # =========================
            # TELEGRAM COMMANDS
            # =========================

            updates = get_updates(
                telegram_offset
            )


            for update in updates:

                telegram_offset = (
                    update[
                        "update_id"
                    ]
                    + 1
                )


                message = update.get(
                    "message"
                )


                if not message:

                    continue


                text = message.get(
                    "text",
                    ""
                ).strip().lower()


                chat_id = str(
                    message[
                        "chat"
                    ][
                        "id"
                    ]
                )


                if chat_id != str(
                    __import__(
                        "os"
                    ).getenv(
                        "TELEGRAM_CHAT_ID"
                    )
                ):

                    continue


                if text == "/stats":

                    stats = (
                        trader.get_stats()
                    )


                    send_message(
                        format_stats(
                            stats
                        )
                    )


                elif text == "/status":

                    stats = (
                        trader.get_stats()
                    )


                    active = (
                        trader.get_active_trades()
                    )


                    send_message(
                        format_status(
                            stats,
                            active
                        )
                    )


                elif text == "/reset":

                    full_state = (
                        tracker.state
                    )


                    trader.reset(
                        full_state
                    )


                    send_message(

                        "♻️ <b>PAPER TRADING "
                        "СБРОШЕН</b>\n\n"

                        "💰 Баланс: "
                        "<b>100 USDC</b>"
                    )


                elif text == "/start":

                    send_message(

                        "🤖 <b>Polymarket "
                        "Paper Trading Bot</b>\n\n"

                        "Команды:\n"

                        "/stats — статистика\n"

                        "/status — активные сделки\n"

                        "/reset — сбросить виртуальный "
                        "баланс\n\n"

                        "Стратегия:\n"

                        "5 одинаковых результатов → "
                        "ставка против серии\n"

                        "LOSS → ставка ×2"
                    )


                elif text == "/help":

                    send_message(

                        "📚 <b>КОМАНДЫ</b>\n\n"

                        "/start\n"

                        "/stats\n"

                        "/status\n"

                        "/reset\n"

                        "/help"
                    )


            # =========================
            # MARKET DATA
            # =========================

            now = time.time()


            if (
                now
                - last_market_check
                >= POLL_INTERVAL_SECONDS
            ):


                last_market_check = now


                markets = (
                    get_recent_closed_markets()
                )


                logger.info(

                    "Received %s markets",

                    len(
                        markets
                    )
                )


                # Сначала разрешаем
                # уже открытые paper trades

                for market in markets:

                    result = (
                        trader.resolve_trade(
                            market,
                            tracker.state
                        )
                    )


                    if result:

                        send_message(
                            format_trade_result(
                                result
                            )
                        )


                # Потом добавляем новые рынки
                # в историю серий

                alerts = (
                    tracker.process_markets(
                        markets
                    )
                )


                for alert in alerts:

                    send_message(
                        format_streak_alert(
                            alert
                        )
                    )


                    if PAPER_TRADING_ENABLED:

                        trade = (
                            trader.open_trade(
                                alert,
                                tracker.state
                            )
                        )


                        if trade:

                            send_message(

                                "🎯 <b>PAPER TRADE "
                                "OPENED</b>\n\n"

                                f"🪙 "
                                f"<b>{trade['coin']}</b>\n"

                                f"📊 После серии: "
                                f"<b>{trade['signal_outcome']}</b>\n"

                                f"🎯 Ставка против: "
                                f"<b>{trade['bet_outcome']}</b>\n"

                                f"💵 Размер: "
                                f"<b>{trade['bet_size']:.2f}</b> USDC"
                            )


        except Exception:

            logger.exception(
                "Main loop error"
            )


        time.sleep(
            2
        )


if __name__ == "__main__":

    main()