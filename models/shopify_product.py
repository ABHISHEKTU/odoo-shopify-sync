import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_product_id = fields.Char(string='Shopify Product ID', index=True, copy=False)
    shopify_synced_at = fields.Datetime(string='Last Synced')
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], string='Sync Status', default='pending', copy=False)

    def action_sync_from_shopify(self):
        icp = self.env['ir.config_parameter'].sudo()
        store_url = icp.get_param('shopify_sync.store_url')
        token = icp.get_param('shopify_sync.access_token')

        if not store_url or not token:
            raise Exception('Shopify store_url or access_token not configured in System Parameters.')

        url = f'https://{store_url}/admin/api/2024-10/products.json'
        headers = {'X-Shopify-Access-Token': token}

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        products = response.json().get('products', [])

        for sp in products:
            variant = sp['variants'][0] if sp.get('variants') else {}
            existing = self.search([('shopify_product_id', '=', str(sp['id']))], limit=1)
            vals = {
                'name': sp['title'],
                'list_price': float(variant.get('price', 0.0)),
                'shopify_product_id': str(sp['id']),
                'sync_status': 'synced',
                'shopify_synced_at': fields.Datetime.now(),
            }
            if existing:
                existing.write(vals)
                _logger.info('Updated product %s from Shopify', sp['title'])
            else:
                self.create(vals)
                _logger.info('Created product %s from Shopify', sp['title'])

        return False

    def action_push_to_shopify(self):
        icp = self.env['ir.config_parameter'].sudo()
        store_url = icp.get_param('shopify_sync.store_url')
        token = icp.get_param('shopify_sync.access_token')

        if not store_url or not token:
            raise Exception('Shopify store_url or access_token not configured in System Parameters.')

        headers = {'X-Shopify-Access-Token': token, 'Content-Type': 'application/json'}

        for product in self:
            payload = {
                'product': {
                    'title': product.name,
                    'variants': [{'price': str(product.list_price)}],
                }
            }
            if product.shopify_product_id:
                url = f'https://{store_url}/admin/api/2024-10/products/{product.shopify_product_id}.json'
                response = requests.put(url, headers=headers, json=payload, timeout=30)
            else:
                url = f'https://{store_url}/admin/api/2024-10/products.json'
                response = requests.post(url, headers=headers, json=payload, timeout=30)

            response.raise_for_status()
            resp_data = response.json()['product']
            product.write({
                'shopify_product_id': str(resp_data['id']),
                'sync_status': 'synced',
                'shopify_synced_at': fields.Datetime.now(),
            })
            _logger.info('Pushed product %s to Shopify', product.name)

        return False
