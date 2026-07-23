import json
import logging
import os
from typing import Any

from .config import (
    STATE_FILE,
    STREAK_TRIGGER,
)


logger = logging.getLogger(__name__)


class StreakTracker:

    def __init__(self):

        self.state = {
            "processed_markets": [],
            "coin_history": {},
            "alerted_streaks": {},
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

                for key in self.state:

                    if key in loaded:

                        self.state[
                            key
                        ] = loaded[
                            key
                        ]


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


        temporary = (
            STATE_FILE
            + ".tmp"
        )


        with open(
            temporary,
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
            temporary,
            STATE_FILE
        )


    def process_markets(
        self,
        markets: list[
            dict[str, Any]
        ]
    ) -> list[
        dict[str, Any]
    ]:

        alerts = []


        markets = sorted(
            markets,
            key=lambda item: (
                item.get(
                    "end_date"
                )
                or ""
            )
        )


        for market in markets:

            market_id = market[
                "market_id"
            ]


            if market_id in self.state[
                "processed_markets"
            ]:

                continue


            coin = market[
                "coin"
            ]


            outcome = market[
                "outcome"
            ]


            if coin not in self.state[
                "coin_history"
            ]:

                self.state[
                    "coin_history"
                ][
                    coin
                ] = []


            history = self.state[
                "coin_history"
            ][
                coin
            ]


            history.append(
                {
                    "market_id": market_id,

                    "outcome": outcome,

                    "end_date": market.get(
                        "end_date"
                    ),
                }
            )


            # Оставляем последние 20
            self.state[
                "coin_history"
            ][
                coin
            ] = history[
                -20:
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
            ][
                -3000:
            ]


            history = self.state[
                "coin_history"
            ][
                coin
            ]


            if len(
                history
            ) < STREAK_TRIGGER:

                continue


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
            ) != 1:

                continue


            streak_outcome = outcomes[
                0
            ]


            last_market_id = (
                last_items[
                    -1
                ][
                    "market_id"
                ]
            )


            signature = (
                coin
                + ":"
                + streak_outcome
                + ":"
                + last_market_id
            )


            previous_signature = (
                self.state[
                    "alerted_streaks"
                ].get(
                    coin
                )
            )


            if (
                signature
                == previous_signature
            ):

                continue


            self.state[
                "alerted_streaks"
            ][
                coin
            ] = signature


            alerts.append(
                {
                    "coin": coin,

                    "outcome": streak_outcome,

                    "history": outcomes,

                    "market": market,
                }
            )


        self.save()


        return alerts


    def reset_history(
        self
    ):

        self.state[
            "processed_markets"
        ] = []

        self.state[
            "coin_history"
        ] = {}

        self.state[
            "alerted_streaks"
        ] = {}

        self.save()
