import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def _join_location_parts(*parts: str) -> str:
    return ", ".join([part.strip() for part in parts if part and part.strip()])


def build_location_queries(
    address_line: str,
    neighborhood: str,
    city: str,
    state: str,
    postal_code: str,
) -> list[str]:
    return [
        _join_location_parts(address_line, neighborhood, city, state, postal_code, "México"),
        _join_location_parts(address_line, neighborhood, city, state, "México"),
        _join_location_parts(neighborhood, city, state, postal_code, "México"),
        _join_location_parts(address_line, city, state, postal_code, "México"),
        _join_location_parts(address_line, city, state, "México"),
        _join_location_parts(city, state, postal_code, "México"),
        _join_location_parts(city, state, "México"),
    ]


def geocode_location_preview(
    address_line: str,
    neighborhood: str,
    city: str,
    state: str,
    postal_code: str,
) -> Optional[dict]:
    queries = build_location_queries(
        address_line=address_line,
        neighborhood=neighborhood,
        city=city,
        state=state,
        postal_code=postal_code,
    )

    headers = {
        "User-Agent": "HABITA/1.0 (location preview)",
    }

    for query in queries:
        try:
            response = requests.get(
                NOMINATIM_URL,
                params={
                    "q": query,
                    "format": "jsonv2",
                    "limit": 1,
                    "countrycodes": "mx",
                    "addressdetails": 1,
                },
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()

            logger.info("[geocode_location_preview] query=%s results=%s", query, len(results))

            if not results:
                continue

            item = results[0]

            lat = item.get("lat")
            lon = item.get("lon")

            if not lat or not lon:
                continue

            return {
                "latitude": float(lat),
                "longitude": float(lon),
                "display_name": item.get("display_name") or query,
                "query_used": query,
            }

        except requests.RequestException as exc:
            logger.warning(
                "[geocode_location_preview] error query=%s detail=%s",
                query,
                str(exc),
            )
            continue
        except (TypeError, ValueError) as exc:
            logger.warning(
                "[geocode_location_preview] invalid result query=%s detail=%s",
                query,
                str(exc),
            )
            continue

    return None