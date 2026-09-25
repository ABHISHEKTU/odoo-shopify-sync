import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ShopifyWebhookController(http.Controller):

    @http.route('/shopify/webhook/test', type='http', auth='public', csrf=False, methods=['GET'])
    def test_route(self, **kwargs):
        return 'Webhook controller is reachable'

    @http.route('/shopify/webhook/products', type='http', auth='public', csrf=False, methods=['POST'])
    def product_webhook(self, **kwargs):
        data = json.loads(request.httprequest.data)
        _logger.info('Received Shopify product webhook: %s', data.get('title'))

        env = request.env(user=1)
        Product = env['product.template']

        variant = data.get('variants', [{}])[0]
        shopify_id = str(data.get('id'))
        existing = Product.sudo().search([('shopify_product_id', '=', shopify_id)], limit=1)

        vals = {
            'name': data.get('title'),
            'list_price': float(variant.get('price', 0.0)),
            'shopify_product_id': shopify_id,
            'sync_status': 'synced',
        }

        if existing:
            existing.write(vals)
        else:
            Product.sudo().create(vals)

        return json.dumps({'status': 'ok'})
