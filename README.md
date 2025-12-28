# README
1. High-Level Architecture
┌────────────┐        ┌────────────────┐        ┌──────────────────────┐
│ Shopify    │◄──────►│ Python AI       │◄──────►│ Rails API (Gateway)  │
│ Store      │ Shopify│ Service (Agent) │ HTTP   │ Auth, Validation     │
│ (Data)     │ APIs   │ FastAPI         │        │ Logging, Tokens      │
└────────────┘        └────────────────┘        └─────────▲────────────┘
                                                               │
                                                               │
                                                        ┌──────┴──────┐
                                                        │ Frontend /  │
                                                        │ API Client  │
                                                        └─────────────┘


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
