from fastapi import FastAPI
from pydantic import BaseModel

from agent import classify_intent, explain_result
from shopify_client import fetch_orders, fetch_inventory
from analytics import analyze_orders, calculate_reorder_quantity

app = FastAPI(title="AI Shopify Analytics API")

class QuestionRequest(BaseModel):
    question: str
    shop: str
    access_token: str

@app.get("/")
def root():
    return {"status": "AI Shopify Analytics API is running 🚀"}

@app.post("/analyze")
def analyze(req: QuestionRequest):
    intent = classify_intent(req.question)

    if intent == "inventory_risk":
        orders = fetch_orders(req.shop, req.access_token)
        inventory = fetch_inventory(req.shop, req.access_token)
        analysis = calculate_reorder_quantity(orders, inventory)

        answer = (
            f"{len(analysis['value'])} products are likely to go out of stock "
            f"in the next 7 days."
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
