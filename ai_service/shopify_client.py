# ai_service/shopify_client.py

import requests

def execute_shopifyql(shop: str, token: str, query: str):
    url = f"https://{shop}/admin/api/2024-10/graphql.json"

    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "query": f"""
        {{
          shopifyqlQuery(query: \"\"\"{query}\"\"\") {{
            __typename
            ... on ShopifyqlQueryResponse {{
              tableData
            }}
          }}
        }}
        """
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# shopify_client.py

import requests
from datetime import datetime, timedelta

def fetch_orders(shop: str, token: str, days: int = 30):
    since = (datetime.now().astimezone() - timedelta(days=days)).isoformat()

    url = f"https://{shop}/admin/api/2024-01/orders.json"
    headers = {"X-Shopify-Access-Token": token}

    params = {
        "status": "any",
        "created_at_min": since,
        "limit": 250
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["orders"]


def fetch_inventory(shop: str, token: str):
    url = f"https://{shop}/admin/api/2024-01/products.json?limit=50"
    headers = {"X-Shopify-Access-Token": token}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    inventory = []
    for product in response.json()["products"]:
        for variant in product["variants"]:
            inventory.append({
                "product": product["title"],
                "variant": variant["title"],
                "inventory_quantity": variant["inventory_quantity"]
            })
    return inventory
