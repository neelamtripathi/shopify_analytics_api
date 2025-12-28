# ai_service/agent.py

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


def generate_shopifyql(question: str, intent: str) -> str:
    if intent == "orders":
        return """
        FROM orders
        SHOW sum(net_sales) AS total_sales
        SINCE -30d
        """
    if intent == "inventory":
        return """
        FROM inventory
        SHOW sum(available) AS total_inventory
        """
    return ""


def explain_result(question: str, data: dict) -> str:
    return "Based on the last 30 days, your sales trend is stable."
