import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shopify_order_id = fields.Char(string='Shopify Order ID', index=True, copy=False)
    shopify_synced_at = fields.Datetime(string='Last Synced')

    @api.model
    def action_sync_orders_from_shopify(self):
        icp = self.env['ir.config_parameter'].sudo()
        store_url = icp.get_param('shopify_sync.store_url')
        token = icp.get_param('shopify_sync.access_token')

        if not store_url or not token:
            raise Exception('Shopify store_url or access_token not configured in System Parameters.')

        url = 'https://' + store_url + '/admin/api/2024-10/orders.json?status=any'
        headers = {'X-Shopify-Access-Token': token}

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        orders = response.json().get('orders', [])

        Partner = self.env['res.partner']
        Product = self.env['product.template']

        for so in orders:
            shopify_order_id = str(so['id'])
            existing = self.search([('shopify_order_id', '=', shopify_order_id)], limit=1)
            if existing:
                continue

            customer_data = so.get('customer') or {}
            email = customer_data.get('email') or ('shopify-guest-' + shopify_order_id + '@example.com')
            partner = Partner.search([('email', '=', email)], limit=1)
            if not partner:
                first = customer_data.get('first_name', '') or ''
                last = customer_data.get('last_name', '') or ''
                full_name = (first + ' ' + last).strip() or 'Shopify Customer'
                partner = Partner.create({
                    'name': full_name,
                    'email': email,
                })

            order_lines = []
            for li in so.get('line_items', []):
                shopify_product_id = str(li.get('product_id'))
                product = Product.search([('shopify_product_id', '=', shopify_product_id)], limit=1)
                if not product:
                    continue
                order_lines.append((0, 0, {
                    'product_id': product.product_variant_id.id,
                    'product_uom_qty': li.get('quantity', 1),
                    'price_unit': float(li.get('price', 0.0)),
                }))

            self.create({
                'partner_id': partner.id,
                'shopify_order_id': shopify_order_id,
                'shopify_synced_at': fields.Datetime.now(),
                'order_line': order_lines,
            })
            _logger.info('Created Odoo order for Shopify order %s', shopify_order_id)

        return False
