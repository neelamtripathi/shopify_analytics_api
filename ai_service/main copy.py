from datetime import datetime, timedelta
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="AI Shopify Analytics API")

# ------------------------
# Request Models
# ------------------------

class QuestionRequest(BaseModel):
    question: str
    shop: str
    access_token: str

# ------------------------
# Utility / AI Logic (TEMP MOCK IMPLEMENTATION)
# ------------------------

def classify_intent(question: str) -> str:
    q = question.lower()

    if "out of stock" in q or "inventory" in q or "stock" in q:
        return "inventory_risk"

    if "sales" in q or "revenue" in q:
        return "sales_analysis"

    if "orders" in q:
        return "order_analysis"

    if "customers" in q:
        return "customer_analysis"

    return "general"


def fetch_orders(shop: str, token: str, days: int = 30):
    since = (datetime.now().astimezone() - timedelta(days=days)).isoformat()

    url = f"https://{shop}/admin/api/2024-01/orders.json"
    headers = {
        "X-Shopify-Access-Token": token
    }

    params = {
        "status": "any",
        "created_at_min": since,
        "limit": 250
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["orders"]

def analyze_orders(intent: str, orders: list):
    if intent == "sales_analysis":
        total = sum(float(o.get("total_price", 0)) for o in orders)
        return {
            "metric": "total_sales",
            "value": round(total, 2),
            "currency": orders[0].get("currency", "INR") if orders else "INR"
        }

    if intent == "order_analysis":
        return {
            "metric": "total_orders",
            "value": len(orders)
        }

    return {
        "metric": "unknown",
        "value": None
    }



def generate_shopifyql(question: str, intent: str) -> str:
    if intent == "inventory_risk":
        return """
        FROM inventory
        SHOW
          product_title,
          sum(available) AS stock_left
        SINCE -7d
        ORDER BY stock_left ASC
        LIMIT 10
        """

    if intent == "sales_analysis":
        return """
        FROM sales
        SHOW sum(net_sales)
        SINCE -30d
        """

    if intent == "order_analysis":
        return """
        FROM orders
        SHOW count()
        SINCE -30d
        """

    return None


def execute_shopifyql(shop: str, token: str, query: str) -> dict:
    """
    Call Shopify Analytics API
    """
    url = f"https://{shop}/admin/api/2024-01/graphql.json"

    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "query": f"""
        {{
          shopifyqlQuery(query: \"\"\"{query}\"\"\") {{
            __typename
            ... on TableResponse {{
              tableData
            }}
            ... on ErrorResponse {{
              message
            }}
          }}
        }}
        """
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()

def fetch_inventory(shop: str, token: str):
    url = f"https://{shop}/admin/api/2024-01/products.json?limit=50"

    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    products = response.json()["products"]

    inventory = []

    for product in products:
        for variant in product["variants"]:
            inventory.append({
                "product": product["title"],
                "variant": variant["title"],
                "inventory_quantity": variant["inventory_quantity"]
            })

    return inventory

def calculate_reorder_quantity(orders, inventory):
    sales_count = {}

    for order in orders:
        for item in order["line_items"]:
            name = item["title"]
            sales_count[name] = sales_count.get(name, 0) + item["quantity"]

    recommendations = []

    for item in inventory:
        sold = sales_count.get(item["product"], 0)
        daily_avg = sold / 30
        reorder_qty = max(0, int(daily_avg * 7 - item["inventory_quantity"]))

        if reorder_qty > 0:
            recommendations.append({
                "product": item["product"],
                "recommended_reorder": reorder_qty
            })

    return recommendations


def extract_inventory_risk(inventory):
    low_stock = []

    for item in inventory:
        if item["inventory_quantity"] <= 10:
            low_stock.append({
                "product": item["product"],
                "variant": item["variant"],
                "stock_left": item["inventory_quantity"]
            })

    return {
        "metric": "inventory_risk",
        "value": low_stock
    }



def explain_result(question: str, analysis: dict) -> str:
    if not analysis:
        return "No data available."

    if analysis["metric"] == "total_sales":
        return f"Your total sales were {analysis['currency']} {analysis['value']}."

    if analysis["metric"] == "total_orders":
        return f"You received {analysis['value']} orders in the last 30 days."

    if analysis["metric"] == "inventory_risk":
        return f"{len(analysis['value'])} products are low in stock."

    return "I analyzed your store data."


# ------------------------
# API Routes
# ------------------------

@app.get("/")
def root():
    return {
        "status": "AI Shopify Analytics API is running 🚀"
    }

from fastapi import HTTPException

@app.post("/analyze")
def analyze(req: QuestionRequest):
    intent = classify_intent(req.question)

    if intent == "inventory_risk":
        orders = fetch_orders(req.shop, req.access_token)
        inventory = fetch_inventory(req.shop, req.access_token)

        analysis = calculate_reorder_quantity(orders, inventory)

        answer = (
            f"{len(analysis)} products are likely to go out of stock "
            f"in the next 7 days based on recent sales."
        )

    else:
        orders = fetch_orders(req.shop, req.access_token)
        analysis = analyze_orders(intent, orders)
        answer = explain_result(req.question, analysis)

    return {
        "answer": answer,
        "intent": intent,
        "analysis": analysis,
        "confidence": "high"
    }




@app.post("/ask")
def ask(payload: dict):
    question = payload["question"]
    shop = payload["shop"]
    token = payload["token"]

    intent = classify_intent(question)
    query = generate_shopifyql(question, intent)
    data = execute_shopifyql(shop, token, query)
    explanation = explain_result(question, data)

    return {
        "answer": explanation,
        "intent": intent,
        "raw_data": data,
        "confidence": "medium"
    }
