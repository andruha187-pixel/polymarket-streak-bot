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

            logger.info(
                "State file does not exist yet: %s",
                STATE_FILE
            )

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


            if not isinstance(
                loaded,
                dict
            ):

                logger.warning(
                    "Invalid state format"
                )

                return


            for key in self.state:

                if key in loaded:

                    self.state[
                        key
                    ] = loaded[
                        key
                    ]


            logger.info(
                "State loaded from %s",
                STATE_FILE
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
            STATE_FILE
            + ".tmp"
        )


        try:

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


        except Exception:

            logger.exception(
                "Could not save state"
            )


            if os.path.exists(
                temporary_file
            ):

                try:

                    os.remove(
                        temporary_file
                    )

                except Exception:

                    pass


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

            market_id = market.get(
                "market_id"
            )


            if not market_id:

                continue


            if market_id in self.state[
                "processed_markets"
            ]:

                continue


            coin = market.get(
                "coin"
            )


            outcome = market.get(
                "outcome"
            )


            if not coin or not outcome:

                continue


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
                f"{coin}:"
                f"{streak_outcome}:"
                f"{last_market_id}"
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


        logger.info(
            "Tracker history reset"
        )
