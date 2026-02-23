import os
import httpx

PRODUCTS_API_URL = os.getenv(
    "PRODUCTS_API_URL",
    "https://product-service-products-service.2.rahtiapp.fi"
)


def fetch_products_by_codes(product_codes: list[str]) -> list[dict]:
    """Hämta produktinfo från Produktregister (products API) för givna koder."""
    if not product_codes:
        return []

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{PRODUCTS_API_URL}/products")
            resp.raise_for_status()
            all_products = resp.json()
    except httpx.RequestError:
        # Om Produktregister inte svarar, returnera koder utan info
        return [
            {"productCode": code, "product_name": "Okänd produkt", "price": None, "img": None}
            for code in product_codes
        ]

    # Bygg en lookup-dict med product_code som nyckel
    catalog = {p["product_code"]: p for p in all_products}

    result = []
    for code in product_codes:
        info = catalog.get(code)
        if info:
            result.append({
                "productCode": code,
                "product_name": info["product_name"],
                "price": info["price"],
                "img": info["img"],
                "description": info.get("description_text"),
            })
        else:
            result.append({
                "productCode": code,
                "product_name": "Okänd produkt",
                "price": None,
                "img": None,
            })

    return result
