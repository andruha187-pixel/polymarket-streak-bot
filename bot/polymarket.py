import json
import logging
from datetime import datetime, timezone
from typing import Any

import requests

from .config import GAMMA_API_URL


logger = logging.getLogger(__name__)


SESSION = requests.Session()

SESSION.headers.update(
    {
        "User-Agent": (
            "Polymarket-Streak-Bot/2.0"
        )
    }
)


def parse_json_value(
    value: Any
) -> Any:

    if isinstance(
        value,
        (
            list,
            dict
        )
    ):
        return value

    if not isinstance(
        value,
        str
    ):
        return []

    try:

        return json.loads(value)

    except json.JSONDecodeError:

        return []


def parse_datetime(
    value: Any
) -> datetime | None:

    if not value:

        return None

    try:

        text = str(value)

        if text.endswith("Z"):

            text = text[:-1] + "+00:00"

        result = datetime.fromisoformat(
            text
        )

        if result.tzinfo is None:

            result = result.replace(
                tzinfo=timezone.utc
            )

        return result

    except ValueError:

        return None


def request_json(
    endpoint: str,
    params: dict[str, Any]
) -> Any:

    url = (
        GAMMA_API_URL
        + endpoint
    )

    response = SESSION.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def is_five_minute_market(
    market: dict[str, Any]
) -> bool:

    start = parse_datetime(
        market.get(
            "startDate"
        )
    )

    end = parse_datetime(
        market.get(
            "endDate"
        )
    )

    if start is not None and end is not None:

        duration = (
            end - start
        ).total_seconds()

        if 240 <= duration <= 420:

            return True


    text = " ".join(
        [
            str(
                market.get(
                    "slug",
                    ""
                )
            ),

            str(
                market.get(
                    "question",
                    ""
                )
            ),

            str(
                market.get(
                    "title",
                    ""
                )
            ),
        ]
    ).lower()


    markers = [
        "5m",
        "5-min",
        "5 min",
        "5minute",
        "5-minute",
    ]


    return any(
        marker in text
        for marker in markers
    )


def get_winning_outcome(
    market: dict[str, Any]
) -> str | None:

    outcomes = parse_json_value(
        market.get(
            "outcomes"
        )
    )

    prices = parse_json_value(
        market.get(
            "outcomePrices"
        )
    )


    if (
        isinstance(
            outcomes,
            list
        )

        and isinstance(
            prices,
            list
        )

        and len(
            outcomes
        )
        == len(
            prices
        )
    ):


        normalized_outcomes = [
            str(
                item
            ).strip().upper()
            for item in outcomes
        ]


        numeric_prices = []


        for price in prices:

            try:

                numeric_prices.append(
                    float(
                        price
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                numeric_prices.append(
                    -1
                )


        candidates = []


        for outcome, price in zip(
            normalized_outcomes,
            numeric_prices
        ):

            if outcome in {
                "YES",
                "NO"
            }:

                candidates.append(
                    (
                        outcome,
                        price
                    )
                )


        if candidates:

            winner = max(
                candidates,
                key=lambda item: item[1]
            )


            if winner[1] >= 0.95:

                return winner[0]


    return None


def extract_coin(
    market: dict[str, Any]
) -> str:

    text = " ".join(
        [
            str(
                market.get(
                    "question",
                    ""
                )
            ),

            str(
                market.get(
                    "slug",
                    ""
                )
            ),

            str(
                market.get(
                    "ticker",
                    ""
                )
            ),
        ]
    ).upper()


    known_coins = [
        "BTC",
        "ETH",
        "SOL",
        "XRP",
        "DOGE",
        "ADA",
        "BNB",
        "AVAX",
        "LINK",
        "SUI",
        "TRX",
        "DOT",
        "TON",
        "SHIB",
        "LTC",
        "BCH",
        "PEPE",
        "WIF",
        "APT",
        "ARB",
        "OP",
        "NEAR",
        "ATOM",
        "MATIC",
        "POL",
        "UNI",
        "AAVE",
        "FIL",
        "INJ",
        "SEI",
        "TIA",
        "RENDER",
        "FET",
        "ALGO",
        "HBAR",
        "ETC",
        "XLM",
        "EOS",
    ]


    for coin in known_coins:

        if coin in text:

            return coin


    return "UNKNOWN"


def fetch_closed_markets_page(
    offset: int
) -> list[dict[str, Any]]:

    data = request_json(
        "/markets",
        {
            "closed": "true",
            "limit": 100,
            "offset": offset,
            "order": "endDate",
            "ascending": "false",
        }
    )


    if not isinstance(
        data,
        list
    ):

        return []


    return data


def get_recent_closed_markets(
) -> list[dict[str, Any]]:

    all_markets = []


    for offset in [
        0,
        100,
        200,
        300,
        400,
    ]:

        try:

            page = (
                fetch_closed_markets_page(
                    offset
                )
            )

        except Exception:

            logger.exception(
                "Failed to fetch markets"
            )

            break


        if not page:

            break


        all_markets.extend(
            page
        )


        if len(
            page
        ) < 100:

            break


    result = []


    for market in all_markets:

        if not market.get(
            "closed",
            False
        ):

            continue


        if not is_five_minute_market(
            market
        ):

            continue


        outcome = get_winning_outcome(
            market
        )


        if outcome not in {
            "YES",
            "NO"
        }:

            continue


        market_id = market.get(
            "id"
        )


        if not market_id:

            continue


        result.append(
            {
                "market_id": str(
                    market_id
                ),

                "coin": extract_coin(
                    market
                ),

                "outcome": outcome,

                "end_date": market.get(
                    "endDate"
                ),

                "start_date": market.get(
                    "startDate"
                ),

                "question": market.get(
                    "question",
                    ""
                ),

                "slug": market.get(
                    "slug",
                    ""
                ),
            }
        )


    unique = {}


    for market in result:

        unique[
            market[
                "market_id"
            ]
        ] = market


    return list(
        unique.values()
    )
