import logging
import time

from .config import (
    PAPER_TRADING_ENABLED,
    POLL_INTERVAL_SECONDS,
    TELEGRAM_CHAT_ID,
)
from .paper_trading import PaperTrader
from .polymarket import get_recent_closed_markets
from .telegram import (
    format_open_trade,
    format_stats,
    format_status,
    format_streak_alert,
    format_trade_result,
    get_updates,
    send_message,
)
from .tracker import StreakTracker


logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    )
)


logger = logging.getLogger(
    __name__
)


def process_command(
    text: str,
    tracker: StreakTracker,
    trader: PaperTrader
):

    command = text.strip().lower()


    if command == "/start":

        send_message(

            "🤖 <b>Polymarket Paper Bot</b>\n\n"

            "Стратегия:\n"

            "5 одинаковых YES/NO → "
            "ставка на противоположный исход.\n\n"

            "LOSS → ставка ×2.\n"

            "WIN → возврат к базовой ставке.\n\n"

            "/stats — статистика\n"

            "/status — активные ставки\n"

            "/reset — сбросить paper trading\n"

            "/help — помощь"
        )


    elif command == "/help":

        send_message(

            "📚 <b>КОМАНДЫ</b>\n\n"

            "/start\n"

            "/stats\n"

            "/status\n"

            "/reset\n"

            "/help"
        )


    elif command == "/stats":

        send_message(
            format_stats(
                trader.stats()
            )
        )


    elif command == "/status":

        send_message(

            format_status(

                trader.stats(),

                trader.state[
                    "active_trades"
                ]
            )
        )


    elif command == "/reset":

        trader.reset()

        tracker.reset_history()

        send_message(

            "♻️ <b>СБРОС ВЫПОЛНЕН</b>\n\n"

            f"💰 Баланс: "
            f"<b>{trader.state['balance']:.2f}</b> USDC"
        )


def main():

    logger.info(
        "Bot started"
    )


    tracker = StreakTracker()


    trader = PaperTrader(
        tracker.state
    )


    telegram_offset = None


    last_market_check = 0


    while True:

        try:

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


                chat_id = str(
                    message[
                        "chat"
                    ][
                        "id"
                    ]
                )


                if chat_id != str(
                    TELEGRAM_CHAT_ID
                ):

                    continue


                text = message.get(
                    "text",
                    ""
                )


                process_command(

                    text,

                    tracker,

                    trader
                )


            now = time.time()


            if (
                now
                - last_market_check
                >= POLL_INTERVAL_SECONDS
            ):

                last_market_check = now


                logger.info(
                    "Checking markets..."
                )


                markets = (
                    get_recent_closed_markets()
                )


                logger.info(

                    "Found %s suitable markets",

                    len(
                        markets
                    )
                )


                # 1. Сначала закрываем
                # активные paper-сделки

                for market in markets:

                    result = (
                        trader.resolve_trade(
                            market
                        )
                    )


                    if result:

                        send_message(

                            format_trade_result(
                                result
                            )
                        )


                # 2. Затем добавляем новые
                # рынки в историю

                alerts = (
                    tracker.process_markets(
                        markets
                    )
                )


                # 3. Открываем новые
                # виртуальные сделки

                for alert in alerts:

                    send_message(

                        format_streak_alert(
                            alert
                        )
                    )


                    if PAPER_TRADING_ENABLED:

                        trade = (
                            trader.open_trade(
                                alert
                            )
                        )


                        if trade:

                            send_message(

                                format_open_trade(
                                    trade
                                )
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
