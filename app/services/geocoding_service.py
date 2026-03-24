from decimal import Decimal
from typing import Optional

import requests


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "HABITA/1.0 (admin@habita.local)",
    "Accept-Language": "es-MX,es;q=0.9",
}


def build_property_query(
    address_line: Optional[str],
    neighborhood: Optional[str],
    city: Optional[str],
    state: Optional[str],
    postal_code: Optional[str],
) -> str:
    parts = [
        (address_line or "").strip(),
        (neighborhood or "").strip(),
        (city or "").strip(),
        (state or "").strip(),
        (postal_code or "").strip(),
        "México",
    ]
    return ", ".join([part for part in parts if part])


def geocode_property_address(
    address_line: Optional[str],
    neighborhood: Optional[str],
    city: Optional[str],
    state: Optional[str],
    postal_code: Optional[str],
) -> Optional[dict]:
    query = build_property_query(address_line, neighborhood, city, state, postal_code)
    if not query:
        return None

    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "mx",
                "addressdetails": 1,
            },
            headers=NOMINATIM_HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        if not payload:
            return None

        first = payload[0]
        lat = first.get("lat")
        lon = first.get("lon")
        if lat is None or lon is None:
            return None

        return {
            "latitude": Decimal(str(lat)),
            "longitude": Decimal(str(lon)),
            "display_name": first.get("display_name", query),
            "query": query,
        }
    except (requests.RequestException, ValueError):
        return None