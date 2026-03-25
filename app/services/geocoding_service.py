import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


def _clean(value: str) -> str:
    return (value or "").strip()


def _build_structured_params(
    *,
    street: str,
    county: str,
    city: str,
    state: str,
    postalcode: str,
    country: str,
) -> dict:
    params = {
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "mx",
    }

    street = _clean(street)
    county = _clean(county)
    city = _clean(city)
    state = _clean(state)
    postalcode = _clean(postalcode)
    country = _clean(country)

    if street:
        params["street"] = street

    if county:
        params["county"] = county

    if city:
        params["city"] = city

    if state:
        params["state"] = state

    if postalcode:
        params["postalcode"] = postalcode

    if country:
        params["country"] = country

    return params


def geocode_structured_location(
    *,
    street: str,
    county: str,
    city: str,
    state: str,
    postalcode: str,
    country: str = "Mexico",
) -> Optional[dict]:
    params = _build_structured_params(
        street=street,
        county=county,
        city=city,
        state=state,
        postalcode=postalcode,
        country=country,
    )

    headers = {
        "User-Agent": "HABITA/1.0 (structured geocode preview)",
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
            "[geocode_structured_location] params=%s results=%s",
            params,
            len(results),
        )

    except requests.RequestException as exc:
        logger.warning(
            "[geocode_structured_location] request_error=%s params=%s",
            str(exc),
            params,
        )
        return None
    except ValueError as exc:
        logger.warning(
            "[geocode_structured_location] invalid_json=%s params=%s",
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