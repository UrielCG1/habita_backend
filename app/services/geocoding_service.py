import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_location_preview(
    address_line: str,
    neighborhood: str,
    city: str,
    state: str,
    postal_code: str,
):
    headers = {
        "User-Agent": "HABITA/1.0 (location preview)",
    }

    structured_params = {
        "street": (address_line or "").strip(),
        "city": (city or "").strip(),
        "county": (neighborhood or "").strip(),
        "state": (state or "").strip(),
        "postalcode": (postal_code or "").strip(),
        "country": "Mexico",
        "countrycodes": "mx",
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1,
    }

    # limpiar vacíos
    structured_params = {k: v for k, v in structured_params.items() if v}

    response = requests.get(
        NOMINATIM_URL,
        params=structured_params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()

    if results:
        item = results[0]
        return {
            "latitude": float(item["lat"]),
            "longitude": float(item["lon"]),
            "display_name": item.get("display_name") or "",
            "query_mode": "structured",
            "query_used": structured_params,
        }

    # fallback libre
    free_form = ", ".join(
        part for part in [
            (address_line or "").strip(),
            (neighborhood or "").strip(),
            (city or "").strip(),
            (state or "").strip(),
            (postal_code or "").strip(),
            "Mexico",
        ] if part
    )

    response = requests.get(
        NOMINATIM_URL,
        params={
            "q": free_form,
            "countrycodes": "mx",
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
        },
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    results = response.json()

    if results:
        item = results[0]
        return {
            "latitude": float(item["lat"]),
            "longitude": float(item["lon"]),
            "display_name": item.get("display_name") or "",
            "query_mode": "free_form",
            "query_used": free_form,
        }

    return None