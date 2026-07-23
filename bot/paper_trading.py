import logging
from typing import Any

from .config import (
    BASE_BET,
    INITIAL_BALANCE,
    MAX_BET,
    MAX_LOSS_STREAK,
)


logger = logging.getLogger(__name__)


class PaperTrader:

    def __init__(
        self,
        state: dict[str, Any]
    ):

        if "paper_trading" not in state:

            state[
                "paper_trading"
            ] = {
                "balance": INITIAL_BALANCE,

                "initial_balance": (
                    INITIAL_BALANCE
                ),

                "total_bets": 0,

                "wins": 0,

                "losses": 0,

                "total_profit": 0.0,

                "current_loss_streak": 0,

                "max_loss_streak": 0,

                "max_bet": 0.0,

                "active_trades": {},

                "trade_history": [],
            }


        self.state = state[
            "paper_trading"
        ]


    @staticmethod
    def opposite(
        outcome: str
    ) -> str:

        if outcome == "YES":

            return "NO"

        return "YES"


    def open_trade(
        self,
        alert: dict[str, Any]
    ) -> dict[str, Any] | None:

        coin = alert[
            "coin"
        ]


        if coin in self.state[
            "active_trades"
        ]:

            return None


        bet_outcome = (
            self.opposite(
                alert[
                    "outcome"
                ]
            )
        )


        bet_size = BASE_BET


        if (
            self.state[
                "balance"
            ]
            < bet_size
        ):

            return None


        trade = {

            "coin": coin,

            "signal_outcome": alert[
                "outcome"
            ],

            "bet_outcome": bet_outcome,

            "bet_size": bet_size,

            "loss_streak": 0,

            "opened_market_id": alert[
                "market"
            ][
                "market_id"
            ],

            "opened_at": alert[
                "market"
            ].get(
                "end_date"
            ),
        }


        self.state[
            "active_trades"
        ][
            coin
        ] = trade


        self.state[
            "max_bet"
        ] = max(
            self.state[
                "max_bet"
            ],

            bet_size
        )


        return trade


    def resolve_trade(
        self,
        market: dict[str, Any]
    ) -> dict[str, Any] | None:

        coin = market[
            "coin"
        ]


        active = self.state[
            "active_trades"
        ]


        if coin not in active:

            return None


        trade = active[
            coin
        ]


        if market[
            "market_id"
        ] == trade[
            "opened_market_id"
        ]:

            return None


        actual = market[
            "outcome"
        ]


        bet_outcome = trade[
            "bet_outcome"
        ]


        bet_size = float(
            trade[
                "bet_size"
            ]
        )


        self.state[
            "total_bets"
        ] += 1


        if actual == bet_outcome:

            profit = bet_size


            self.state[
                "balance"
            ] += profit


            self.state[
                "total_profit"
            ] += profit


            self.state[
                "wins"
            ] += 1


            result = {

                "type": "WIN",

                "coin": coin,

                "bet_outcome": bet_outcome,

                "actual_outcome": actual,

                "bet_size": bet_size,

                "profit": profit,

                "balance": self.state[
                    "balance"
                ],
            }


            del active[
                coin
            ]


            self.state[
                "current_loss_streak"
            ] = 0


        else:

            loss = bet_size


            self.state[
                "balance"
            ] -= loss


            self.state[
                "total_profit"
            ] -= loss


            self.state[
                "losses"
            ] += 1


            trade[
                "loss_streak"
            ] += 1


            self.state[
                "current_loss_streak"
            ] = trade[
                "loss_streak"
            ]


            self.state[
                "max_loss_streak"
            ] = max(
                self.state[
                    "max_loss_streak"
                ],

                trade[
                    "loss_streak"
                ]
            )


            next_bet = (
                bet_size * 2
            )


            if (

                next_bet > MAX_BET

                or trade[
                    "loss_streak"
                ] >= MAX_LOSS_STREAK

                or next_bet > self.state[
                    "balance"
                ]
            ):


                result = {

                    "type": "LOSS_STOPPED",

                    "coin": coin,

                    "bet_outcome": bet_outcome,

                    "actual_outcome": actual,

                    "bet_size": bet_size,

                    "loss": loss,

                    "next_bet": None,

                    "balance": self.state[
                        "balance"
                    ],
                }


                del active[
                    coin
                ]


            else:

                trade[
                    "bet_size"
                ] = next_bet


                self.state[
                    "max_bet"
                ] = max(
                    self.state[
                        "max_bet"
                    ],

                    next_bet
                )


                result = {

                    "type": "LOSS",

                    "coin": coin,

                    "bet_outcome": bet_outcome,

                    "actual_outcome": actual,

                    "bet_size": bet_size,

                    "loss": loss,

                    "next_bet": next_bet,

                    "loss_streak": trade[
                        "loss_streak"
                    ],

                    "balance": self.state[
                        "balance"
                    ],
                }


        self.state[
            "trade_history"
        ].append(
            result
        )


        self.state[
            "trade_history"
        ] = self.state[
            "trade_history"
        ][
            -1000:
        ]


        return result


    def stats(
        self
    ) -> dict[str, Any]:

        total = self.state[
            "total_bets"
        ]


        wins = self.state[
            "wins"
        ]


        win_rate = (
            wins
            / total
            * 100
            if total > 0
            else 0
        )


        return {

            "balance": self.state[
                "balance"
            ],

            "initial_balance": self.state[
                "initial_balance"
            ],

            "total_profit": self.state[
                "total_profit"
            ],

            "total_bets": total,

            "wins": wins,

            "losses": self.state[
                "losses"
            ],

            "win_rate": win_rate,

            "max_loss_streak": self.state[
                "max_loss_streak"
            ],

            "max_bet": self.state[
                "max_bet"
            ],

            "active_trades": len(
                self.state[
                    "active_trades"
                ]
            ),
        }


    def reset(
        self
    ):

        self.state.clear()


        self.state.update(
            {
                "balance": INITIAL_BALANCE,

                "initial_balance": (
                    INITIAL_BALANCE
                ),

                "total_bets": 0,

                "wins": 0,

                "losses": 0,

                "total_profit": 0.0,

                "current_loss_streak": 0,

                "max_loss_streak": 0,

                "max_bet": 0.0,

                "active_trades": {},

                "trade_history": [],
            }
    )
