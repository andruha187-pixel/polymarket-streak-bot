import json
import logging
from datetime import datetime, timezone
from typing import Any

import requests

from .config import GAMMA_API_URL


logger = logging.getLogger(
    __name__
)


SESSION = requests.Session()

SESSION.headers.update(
    {
        "User-Agent": (
            "Polymarket-Streak-Bot/1.0"
        )
    }
)


def get_json(
    url: str,
    params: dict[str, Any] | None = None
) -> Any:

    response = SESSION.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def parse_json_field(
    value: Any,
    default: Any
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
        return default

    try:

        return json.loads(
            value
        )

    except json.JSONDecodeError:

        return default


def parse_datetime(
    value: str | None
) -> datetime | None:

    if not value:

        return None

    try:

        value = value.replace(
            "Z",
            "+00:00"
        )

        dt = datetime.fromisoformat(
            value
        )

        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt

    except ValueError:

        return None


def is_five_minute_market(
    market: dict[str, Any]
) -> bool:

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


    if any(
        marker in text
        for marker in markers
    ):

        return True


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


    if start and end:

        duration = (
            end - start
        ).total_seconds()


        if 240 <= duration <= 420:

            return True


    return False


def get_winning_outcome(
    market: dict[str, Any]
) -> str | None:

    """
    Основной метод:
    в закрытом бинарном рынке победивший outcome
    обычно имеет цену около 1.0.

    Дополнительно поддерживаем tokens/winner,
    если эти поля присутствуют.
    """


    outcomes = parse_json_field(
        market.get(
            "outcomes"
        ),
        []
    )


    prices = parse_json_field(
        market.get(
            "outcomePrices"
        ),
        []
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


        for outcome, price in zip(
            outcomes,
            prices
        ):

            try:

                price_float = float(
                    price
                )

            except (
                ValueError,
                TypeError
            ):

                continue


            if price_float >= 0.99:

                normalized = str(
                    outcome
                ).strip().upper()


                if normalized in {
                    "YES",
                    "NO"
                }:

                    return normalized


    tokens = market.get(
        "tokens"
    )


    if isinstance(
        tokens,
        list
    ):


        for token in tokens:

            if not isinstance(
                token,
                dict
            ):

                continue


            if token.get(
                "winner"
            ) is True:

                outcome = str(
                    token.get(
                        "outcome",
                        ""
                    )
                ).strip().upper()


                if outcome in {
                    "YES",
                    "NO"
                }:

                    return outcome


    for key in [
        "winningOutcome",
        "winning_outcome",
        "winner",
    ]:

        value = market.get(
            key
        )


        if value:

            normalized = str(
                value
            ).strip().upper()


            if normalized in {
                "YES",
                "NO"
            }:

                return normalized


    return None


def extract_coin_name(
    event: dict[str, Any],
    market: dict[str, Any]
) -> str:

    text = " ".join(
        [
            str(
                event.get(
                    "title",
                    ""
                )
            ),

            str(
                event.get(
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
                    "slug",
                    ""
                )
            ),
        ]
    )


    text = text.upper()


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


    slug = str(
        event.get(
            "slug"
        )
        or market.get(
            "slug"
        )
        or ""
    )


    if slug:

        first_part = slug.split(
            "-"
        )[0]


        if first_part:

            return first_part.upper()


    return "UNKNOWN"


def get_recent_closed_markets(
) -> list[dict[str, Any]]:

    url = (
        f"{GAMMA_API_URL}/events"
    )


    params = {
        "tag_slug": "crypto",
        "closed": "true",
        "active": "false",
        "archived": "false",
        "limit": 500,
        "order": "endDate",
        "ascending": "false",
    }


    events = get_json(
        url,
        params=params
    )


    if not isinstance(
        events,
        list
    ):

        logger.warning(
            "Unexpected API response"
        )

        return []


    result = []


    for event in events:

        markets = event.get(
            "markets",
            []
        )


        if not isinstance(
            markets,
            list
        ):

            continue


        for market in markets:

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


            coin = extract_coin_name(
                event,
                market
            )


            result.append(
                {
                    "market_id": str(
                        market.get(
                            "id"
                        )
                    ),

                    "event_id": str(
                        event.get(
                            "id"
                        )
                    ),

                    "coin": coin,

                    "outcome": outcome,

                    "end_date": market.get(
                        "endDate"
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


    return result