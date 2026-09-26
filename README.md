# Shopify-Odoo Sync

A custom Odoo 17 module that bidirectionally syncs products and orders with Shopify, enriches product listings using AI, and includes a natural-language chatbot for querying live inventory and sales data.

Built as a portfolio project to demonstrate ERP integration, e-commerce API work, webhook-driven real-time sync, and applied LLM usage grounded in real business data.

## Features

### Product Sync
- **Pull sync**: Shopify -> Odoo (manual trigger + automated cron every 15 minutes)
- **Push sync**: Odoo -> Shopify (manual trigger)
- **Real-time webhooks**: Shopify product updates instantly reflected in Odoo via HTTP controller, tested end-to-end using an ngrok tunnel
- Sync status tracking per product (Pending / Synced / Error) with visual badge in the UI

### Order Sync
- Pulls Shopify orders into Odoo as quotations
- Auto-creates or matches customer records by email
- Maps Shopify line items to Odoo order lines using the shared product ID

### AI Product Enrichment
- Generates SEO title, SEO tags, and marketing copy per product using an LLM (Groq / Llama)
- Triggered on-demand from the product form
- Results stored on the product and shown in a dedicated "AI Enrichment" tab

### AI Inventory Assistant (RAG-style chatbot)
- Natural-language Q&A wizard accessible from the Inventory app
- Retrieves live product and order data via the Odoo ORM (not vector search, since exact figures matter more than semantic similarity for structured business data)
- Feeds retrieved data as grounded context to the LLM, preventing hallucinated answers
- Example: "What was our last order total?" -> answers correctly from live data, not guesswork

## ArchitectureShopify                                                                                                  Admin API <--> Odoo Custom Module <--> Groq LLM API
(REST + Webhooks) (ORM, Controllers, (Enrichment +
Cron, Wizards) Chatbot)
- **models/shopify_product.py** - product pull/push sync logic
- **models/shopify_order.py** - order pull sync logic
- **models/ai_enrichment.py** - LLM-based product content generation
- **models/ai_chatbot.py** - RAG-style wizard querying live Odoo data via LLM
- **controllers/webhook.py** - HTTP endpoint receiving real-time Shopify webhooks
- **data/cron.xml** - scheduled action for periodic product sync
- **views/** - UI integration (form badges, action buttons, chatbot wizard, AI tab)

## Tech Stack
- Odoo 17 (Python, PostgreSQL, ORM)
- Shopify Admin REST API (products, orders, webhooks)
- Groq API (Llama / GPT-OSS models) for LLM inference
- ngrok (local webhook tunnel for development/testing)

## Setup

1. Install the module in your Odoo custom_addons directory
2. Set the following System Parameters (Settings > Technical > System Parameters):
   - shopify_sync.store_url
   - shopify_sync.access_token
   - shopify_sync.groq_api_key
3. Product sync: use the Actions menu on any product ("Sync Products from Shopify" / "Push to Shopify")
4. Order sync: use the Actions menu on any sales order ("Sync Orders from Shopify")
5. AI enrichment: open a product, use Actions > "Enrich with AI"
6. Chatbot: Inventory app > AI Assistant menu

## Notes
This was built and tested against a Shopify Partner development store. Webhook delivery was verified in real time using ngrok to expose the local Odoo instance during development.
