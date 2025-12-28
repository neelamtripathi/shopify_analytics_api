# README
1. High-Level Architecture

<img width="681" height="281" alt="Screenshot 2025-12-28 at 21 21 36" src="https://github.com/user-attachments/assets/cd8501ef-6b57-45d8-9f67-4f3514f055f4" />


Key idea:

Rails = secure gateway + Shopify OAuth + API contract

Python = intelligence layer (LLM + agent logic)

ShopifyQL = analytics language to query store data

This separation keeps business logic, AI reasoning, and security cleanly isolated.

2. Shopify Integration (OAuth + Data Access)
OAuth Flow

Merchant installs the app

Shopify redirects to Rails /auth/shopify/callback

Rails exchanges code → access token

Token stored securely (encrypted DB / credentials store)

# Rails stores
Store {
  shop_domain,
  access_token,
  scopes,
  installed_at
}

Shopify APIs Used

ShopifyQL Analytics API (primary)

Orders

Products

Inventory levels

Why ShopifyQL?
It’s optimized for analytics queries, not transactional reads.

3. Rails API (Backend Gateway)
Responsibilities

✅ OAuth & token management
✅ Input validation
✅ Request logging
✅ Forward request to Python AI service
✅ Format final response

API Endpoint
POST /api/v1/questions


Request

{
  "store_id": "example-store.myshopify.com",
  "question": "How much inventory should I reorder for next week?"
}

4. Installation
git clone https://github.com/neelamtripathi/shopify_analytics_api.git)
cd ~/shopify_analytics_api/ai_service

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows


Run the API
uvicorn main:app --reload
API will be available at:

http://127.0.0.1:8000


Swagger UI:

http://127.0.0.1:8000/docs
<img width="1680" height="1050" alt="Screenshot 2025-12-28 at 18 50 44" src="https://github.com/user-attachments/assets/8ee86a5f-5939-4de8-a0f8-b300b9589a40" />
<img width="1680" height="1050" alt="Screenshot 2025-12-28 at 18 27 53" src="https://github.com/user-attachments/assets/3590bd37-ee97-40b1-a1e3-22dd0e1fa7f2" />
<img width="1680" height="1050" alt="Screenshot 2025-12-28 at 18 27 32" src="https://github.com/user-attachments/assets/22470fba-383c-41c0-ab1d-4f416c6ed95e" />
<img width="1680" height="1050" alt="Screenshot 2025-12-28 at 18 27 32" src="https://github.com/user-attachments/assets/741c7e99-e752-4c0a-9deb-73578db07864" />
<img width="1680" height="1050" alt="Screenshot 2025-12-28 at 17 27 57" src="https://github.com/user-attachments/assets/ed5bc6b5-469a-4ea5-8fdc-158925538122" />

5. Architecture Explanation
High-Level Components
Client (User Question)
        |
        v
FastAPI (main.py)
        |
        v
Agent Layer (agent.py)
(Intent Classification + Reasoning)
        |
        v
Analytics Layer (analytics.py)
(Business Logic & Metrics)
        |
        v
Shopify Client (shopify_client.py)
(Shopify Admin API)

6. Step-by-Step Agent Flow
1️⃣ Intent Classification

The agent first understands what the user is asking.

Example:

“How much inventory should I reorder for next week?”


Agent output:

{
  "domain": "inventory",
  "metric": "reorder_qty",
  "period": "next_7_days"
}


Handled in:

agent.py → classify_intent()

2️⃣ Planning & Tool Selection

Based on intent, the agent decides:

Which Shopify resource to query

What aggregation logic to use

Example:

Tables: orders, inventory_levels

Aggregations:

SUM(quantity)

AVG(daily_sales)

Forecast logic:

Rolling 30-day average

3️⃣ Data Retrieval (Shopify Integration)

Handled by:

shopify_client.py


Features:

Shopify Admin REST API

Date filtering

Pagination-safe logic

Graceful empty-data handling

4️⃣ Analytics & Reasoning

Handled by:

analytics.py


Examples:

Total sales

Order count

Inventory risk detection

Reorder quantity recommendation

5️⃣ Explanation Generation

The agent converts raw metrics into simple business language:

“3 products are likely to go out of stock in the next 7 days based on recent sales trends.”

4️⃣ Sample API Requests & Responses
🔹 Request

Endpoint

POST /analyze


Payload

{
  "question": "How many orders did I get in the last 30 days?",
  "shop": "your-store.myshopify.com",
  "access_token": "shpat_xxxxxxxxxxxxx"
}
.env file having all credential

SHOPIFY_API_KEY=31f28507b6b9901a26d748c64fa1623d
SHOPIFY_API_SECRET=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
SHOPIFY_SCOPES=read_products,read_orders
APP_URL=https://unpreordained-alan-judgmatic.ngrok-free.dev
AI_SERVICE_URL=http://localhost:8000/analyze
SHOPIFY_SHOP=cafenosta.myshopify.com
SHOPIFY_ACCESS_TOKEN=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

<img width="130" height="494" alt="Screenshot 2025-12-28 at 21 23 14" src="https://github.com/user-attachments/assets/eab4bcfc-477f-41f5-b741-1c0f7aae3245" />
