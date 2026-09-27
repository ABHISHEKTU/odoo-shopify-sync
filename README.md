# 🔄 Shopify ⇄ Odoo Sync

**A custom Odoo 17 module for bidirectional e-commerce sync — enhanced with AI-powered product enrichment and a natural-language inventory assistant.**

[![Odoo](https://img.shields.io/badge/Odoo-17.0-714B67?logo=odoo&logoColor=white)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Shopify API](https://img.shields.io/badge/Shopify-Admin%20REST%20API-95BF47?logo=shopify&logoColor=white)](https://shopify.dev/docs/api/admin-rest)
[![Groq](https://img.shields.io/badge/LLM-Groq%20(Llama)-F55036)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 Overview

Businesses running operations on **Odoo** but selling through **Shopify** face a familiar problem: keeping product and order data in sync across two systems is slow, manual, and error-prone.

**Shopify-Odoo Sync** solves this with a purpose-built Odoo module that:

- Keeps products and orders in sync **bidirectionally**, in real time
- Uses an **LLM** to auto-generate SEO-ready product content
- Answers **natural-language business questions** ("What was our last order total?") using live, grounded data — not vector search guesswork

This was built end-to-end — environment setup, ORM models, webhook controllers, cron automation, and AI integration — as a demonstration of practical full-stack + applied-AI engineering, not a toy demo.

---

## ✨ Key Features

### 🔁 Product Sync (Bidirectional)
| Capability | Details |
|---|---|
| Pull sync | Fetches products from Shopify's Admin REST API into Odoo's `product.template` |
| Push sync | Pushes Odoo-created/edited products to Shopify (create or update) |
| Scheduled automation | Cron job runs every 15 minutes for hands-free pull sync |
| Real-time webhooks | Shopify → Odoo updates land via HMAC-secured webhook, verified at sub-second latency |
| Status tracking | Per-product `sync_status` (Pending / Synced / Error) with a color-coded UI badge |

### 📦 Order Sync
- Imports Shopify orders into Odoo as sales quotations
- Auto-matches or creates `res.partner` customer records by email
- Maps Shopify line items to Odoo order lines via shared Shopify product ID
- Idempotent — checks `shopify_order_id` before creating, so re-runs never duplicate

### 🤖 AI Product Enrichment
- One-click action on any product form
- Calls an LLM (Groq — Llama / GPT-OSS) to generate:
  - A marketing description
  - An SEO-optimized title
  - A set of SEO keyword tags
- Prompt engineered for structured JSON output, parsed and saved directly to the product record
- Displayed in a dedicated **AI Enrichment** tab

### 💬 AI Inventory & Sales Assistant (RAG, done right)
- Plain-English Q&A wizard from the Inventory app — e.g. *"How many Test Hoodies do we have in stock?"*
- **Deliberately skips vector embeddings.** For structured business data, semantic similarity search returns "similar" text — not "correct" numbers. Instead, this assistant runs direct ORM queries against live Odoo data and feeds that as grounded context to the LLM.
- Result: answers that match real Odoo records exactly, not hallucinated approximations.

---

## 🏗️ Architecture

```
Shopify Store (Partner Dev Store)
        │
        │  REST API (products, orders) + Webhooks
        ▼
Odoo 17 Custom Module ("shopify_sync")
  ├── models/
  │     shopify_product.py   → pull/push product sync logic
  │     shopify_order.py     → order pull sync logic
  │     ai_enrichment.py     → LLM product content generation
  │     ai_chatbot.py        → RAG-style data query wizard
  ├── controllers/
  │     webhook.py           → HTTP endpoint receiving real-time Shopify webhooks
  ├── data/
  │     cron.xml             → scheduled 15-min product sync job
  ├── views/
  │     product_views.xml, order_views.xml,
  │     enrichment_views.xml, chatbot_views.xml
  └── security/
        ir.model.access.csv  → access control for custom models
        │
        ▼
Groq LLM API (Llama / GPT-OSS models)
  — used for both product enrichment and chatbot inference
```

**Key design decisions:**

- **Separation of pull vs. push** — explicit, independent methods per direction rather than one "smart" bidirectional function, keeping the conflict surface small and debuggable.
- **Idempotent sync** — Shopify IDs checked before every create, so cron + webhooks can run concurrently without corrupting data.
- **RAG matched to the data shape** — ORM retrieval over vector search, because exact figures matter more than semantic similarity for this use case.
- **No hardcoded secrets** — API tokens live in Odoo's `ir.config_parameter` store, never in source.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ERP Framework | Odoo 17 (Python 3.12, ORM, QWeb/XML views) |
| Database | PostgreSQL 16 |
| E-commerce | Shopify Admin REST API (products, orders, HMAC-secured webhooks) |
| AI / LLM | Groq API (free tier, OpenAI-compatible, open-weight models) |
| Dev Tooling | ngrok (webhook tunneling), Git/GitHub |
| Environment | Windows / PowerShell, Python virtualenv |

---

## 🚀 Installation

1. **Clone the repo into your Odoo custom addons path:**
   ```bash
   git clone https://github.com/ABHISHEKTU/odoo-shopify-sync.git
   ```

2. **Restart Odoo and update the apps list**, then install `shopify_sync` from Apps.

3. **Configure credentials** under `Settings → Technical → System Parameters`:

   | Key | Description |
   |---|---|
   | `shopify_sync.store_url` | Your Shopify store's `.myshopify.com` URL |
   | `shopify_sync.access_token` | Shopify Admin API access token |
   | `shopify_sync.groq_api_key` | Groq API key for LLM calls |

4. **(Optional, for local webhook testing)** expose your local Odoo instance via ngrok and register the tunnel URL as your Shopify webhook endpoint.

---

## 💡 Usage

**Sync products**
- Open any product → Actions → **Sync Products from Shopify** (pull) or **Push to Shopify** (push)

**Sync orders**
- Sales → Orders → Actions → **Sync Orders from Shopify**

**Generate AI content for a product**
- Open a product → Actions → **Enrich with AI**
- Marketing copy, SEO title, and tags appear in the **AI Enrichment** tab

**Ask the inventory assistant a question**
- Inventory app → **AI Assistant**
- Example:
  > "What was our last order total?"
  > → Answered from live Odoo data, not a guess.

---

## 📌 Notes & Current Limitations

This module was built and verified against a real **Shopify Partner development store**, with webhook delivery tested live (not mocked) via an ngrok tunnel.

Known scope boundaries, and natural next steps:

- No conflict resolution for simultaneous edits on both platforms (currently last-write-wins)
- Inventory quantity is not yet synced (price/title/basic fields only)
- Order push (Odoo → Shopify) isn't built — pull-only for now
- Vector-based semantic search could complement the ORM-based chatbot for unstructured queries (e.g., "find products similar to X")

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes with clear messages
4. Open a pull request describing the change and why it's needed

Please keep pull/push sync logic separate per the existing architecture pattern, and avoid hardcoding credentials — use `ir.config_parameter`.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 🔗 Repository

[github.com/ABHISHEKTU/odoo-shopify-sync](https://github.com/ABHISHEKTU/odoo-shopify-sync) — full commit history shows the incremental build: auth → sync → automation → webhooks → AI layers.
