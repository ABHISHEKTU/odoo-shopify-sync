# Shopify Sync for Odoo

Custom Odoo 17 module syncing products bidirectionally with Shopify.

## Features
- Pull sync: Shopify -> Odoo (manual + scheduled cron every 15 min)
- Push sync: Odoo -> Shopify (manual)
- Real-time webhook sync (Shopify product updates instantly reflected in Odoo)
- Sync status tracking per product (Pending / Synced / Error)

## Tech
- Odoo 17 (Python, PostgreSQL, ORM)
- Shopify Admin REST API
- Webhook receiver via Odoo HTTP controllers
- Tested locally using ngrok tunnel for webhook delivery

## Setup
1. Install module in custom_addons
2. Set System Parameters: shopify_sync.store_url, shopify_sync.access_token
3. Use product form actions to trigger manual sync, or let cron/webhooks handle it automatically
