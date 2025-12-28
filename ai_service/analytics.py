# analytics.py

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

    return {"metric": "unknown", "value": None}


def calculate_reorder_quantity(orders, inventory):
    sales_count = {}

    for order in orders:
        for item in order["line_items"]:
            sales_count[item["title"]] = sales_count.get(item["title"], 0) + item["quantity"]

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

    return {
        "metric": "inventory_risk",
        "value": recommendations
    }
