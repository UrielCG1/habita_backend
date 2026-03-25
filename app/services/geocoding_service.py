import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


def _build_structured_params(
    *,
    address_line: Optional[str],
    neighborhood: Optional[str],
    city: Optional[str],
    state: Optional[str],
    postal_code: Optional[str],
) -> dict:
    params = {
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "mx",
        "country": "Mexico",
    }

    address_line = _clean(address_line)
    neighborhood = _clean(neighborhood)
    city = _clean(city)
    state = _clean(state)
    postal_code = _clean(postal_code)

    if address_line:
        params["street"] = address_line

    if neighborhood:
        params["county"] = neighborhood

    if city:
        params["city"] = city

    if state:
        params["state"] = state

    if postal_code:
        params["postalcode"] = postal_code

    return params


def geocode_location_preview(
    *,
    address_line: Optional[str],
    neighborhood: Optional[str],
    city: Optional[str],
    state: Optional[str],
    postal_code: Optional[str],
) -> Optional[dict]:
    city = _clean(city)
    state = _clean(state)

    if not city or not state:
        return None

    params = _build_structured_params(
        address_line=address_line,
        neighborhood=neighborhood,
        city=city,
        state=state,
        postal_code=postal_code,
    )

    headers = {
        "User-Agent": "HABITA/1.0 (structured geocode)",
        "Accept-Language": "es-MX,es;q=0.9",
    }

    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()

        logger.info(
            "[geocode_location_preview] structured params=%s results=%s",
            params,
            len(results),
        )

    except requests.RequestException as exc:
        logger.warning(
            "[geocode_location_preview] request_error=%s params=%s",
            str(exc),
            params,
        )
        return None
    except ValueError as exc:
        logger.warning(
            "[geocode_location_preview] invalid_json=%s params=%s",
            str(exc),
            params,
        )
        return None

    if not results:
        return None

    item = results[0]

    lat = item.get("lat")
    lon = item.get("lon")

    if not lat or not lon:
        return None

    return {
        "latitude": float(lat),
        "longitude": float(lon),
        "display_name": item.get("display_name") or "",
        "query_used": params,
    }