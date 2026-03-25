import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


def geocode_location_preview(
    *,
    address_line: Optional[str],
    neighborhood: Optional[str],
    city: Optional[str],
    state: Optional[str],
    postal_code: Optional[str],
    country: str = "Mexico",
) -> Optional[dict]:
    address_line = _clean(address_line)
    neighborhood = _clean(neighborhood)
    city = _clean(city)
    state = _clean(state)
    postal_code = _clean(postal_code)
    # country = _clean(country) or "Mexico"

    if not city or not state:
        return None

    if not address_line and not neighborhood and not postal_code:
        return None

    search_context = {}

    if address_line:
        search_context["street"] = address_line
    if neighborhood:
        search_context["county"] = neighborhood
    # if city:
        # search_context["city"] = city
    if state:
        search_context["state"] = state
    if postal_code:
        search_context["postalcode"] = postal_code
    #if country:
    #    search_context["country"] = country

    request_params = {
        **search_context,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "mx",
    }

    headers = {
        "User-Agent": "HABITA/1.0 (structured geocode preview)",
        "Accept-Language": "es-MX,es;q=0.9",
    }

    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params=request_params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()
    except requests.RequestException as exc:
        logger.warning(
            "[geocode_location_preview] request_error=%s params=%s",
            str(exc),
            request_params,
        )
        return None
    except ValueError as exc:
        logger.warning(
            "[geocode_location_preview] invalid_json=%s params=%s",
            str(exc),
            request_params,
        )
        return None

    if not results:
        logger.info("[geocode_location_preview] no_results params=%s", request_params)
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
        "query_used": search_context,
    }