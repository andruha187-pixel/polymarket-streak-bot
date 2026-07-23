import json
import logging
import os
from typing import Any

from .config import (
    HISTORY_LENGTH,
    STATE_FILE,
    STREAK_TRIGGER,
)


logger = logging.getLogger(
    __name__
)


class StreakTracker:

    def __init__(self):

        self.state = {
            "processed_markets": [],
            "coins": {},
        }


        self.load()


    def load(self):

        if not os.path.exists(
            STATE_FILE
        ):

            return


        try:

            with open(
                STATE_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                loaded = json.load(
                    file
                )


                if isinstance(
                    loaded,
                    dict
                ):

                    self.state.update(
                        loaded
                    )


        except Exception:

            logger.exception(
                "Could not load state"
            )


    def save(self):

        directory = os.path.dirname(
            STATE_FILE
        )


        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )


        temporary_file = (
            f"{STATE_FILE}.tmp"
        )


        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.state,
                file,
                ensure_ascii=False,
                indent=2
            )


        os.replace(
            temporary_file,
            STATE_FILE
        )


    def process_market(
        self,
        market: dict[str, Any]
    ) -> dict[str, Any] | None:

        market_id = market[
            "market_id"
        ]


        if market_id in self.state[
            "processed_markets"
        ]:

            return None


        coin = market[
            "coin"
        ]


        outcome = market[
            "outcome"
        ]


        coins = self.state[
            "coins"
        ]


        if coin not in coins:

            coins[coin] = {
                "history": [],
                "last_alert_signature": None,
            }


        coin_state = coins[
            coin
        ]


        history = coin_state[
            "history"
        ]


        history.append(
            {
                "outcome": outcome,

                "market_id": market_id,

                "end_date": market.get(
                    "end_date"
                ),
            }
        )


        coin_state[
            "history"
        ] = history[
            -HISTORY_LENGTH:
        ]


        self.state[
            "processed_markets"
        ].append(
            market_id
        )


        self.state[
            "processed_markets"
        ] = self.state[
            "processed_markets"
        ][-3000:]


        alert = None


        if len(
            history
        ) >= STREAK_TRIGGER:


            last_items = history[
                -STREAK_TRIGGER:
            ]


            outcomes = [
                item[
                    "outcome"
                ]

                for item in last_items
            ]


            if len(
                set(
                    outcomes
                )
            ) == 1:


                outcome = outcomes[
                    0
                ]


                signature = (
                    f"{coin}:"
                    f"{outcome}:"
                    f"{last_items[-1]['market_id']}"
                )


                previous_signature = (
                    coin_state.get(
                        "last_alert_signature"
                    )
                )


                if (
                    signature
                    != previous_signature
                ):


                    coin_state[
                        "last_alert_signature"
                    ] = signature


                    alert = {
                        "coin": coin,

                        "outcome": outcome,

                        "history": outcomes,

                        "market": market,
                    }


        self.save()


        return alert


    def process_markets(
        self,
        markets: list[
            dict[str, Any]
        ]
    ) -> list[
        dict[str, Any]
    ]:

        alerts = []


        sorted_markets = sorted(
            markets,

            key=lambda item: (
                item.get(
                    "end_date"
                )
                or ""
            )
        )


        for market in sorted_markets:

            alert = self.process_market(
                market
            )


            if alert:

                alerts.append(
                    alert
                )


        return alerts


    def get_history(
        self,
        coin: str
    ) -> list[dict]:

        return self.state[
            "coins"
        ].get(
            coin,
            {}
        ).get(
            "history",
            []
        )