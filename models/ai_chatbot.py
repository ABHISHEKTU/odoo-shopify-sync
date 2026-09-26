import requests
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ShopifyChatbotWizard(models.TransientModel):
    _name = 'shopify.chatbot.wizard'
    _description = 'AI Inventory Chatbot'

    question = fields.Text(string='Ask a question')
    answer = fields.Text(string='Answer', readonly=True)

    def action_ask(self):
        self.ensure_one()
        icp = self.env['ir.config_parameter'].sudo()
        api_key = icp.get_param('shopify_sync.groq_api_key')

        if not api_key:
            raise Exception('Groq API key not configured in System Parameters.')

        Product = self.env['product.template']
        Order = self.env['sale.order']

        products = Product.search([], limit=50)
        product_lines = []
        for p in products:
            product_lines.append(
                p.name + ' | price: ' + str(p.list_price) +
                ' | qty_on_hand: ' + str(p.qty_available) +
                ' | sync_status: ' + str(p.sync_status)
            )
        product_context = chr(10).join(product_lines)

        orders = Order.search([], limit=50)
        order_lines = []
        for o in orders:
            order_lines.append(
                o.name + ' | customer: ' + (o.partner_id.name or '') +
                ' | total: ' + str(o.amount_total) +
                ' | state: ' + str(o.state)
            )
        order_context = chr(10).join(order_lines)

        system_prompt = (
            'You are an assistant answering questions about a company inventory and sales data. '
            'Use ONLY the data provided below. If the answer is not in the data, say so clearly. '
            'Be concise.' + chr(10) + chr(10) +
            'PRODUCTS:' + chr(10) + product_context + chr(10) + chr(10) +
            'ORDERS:' + chr(10) + order_context
        )

        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {
            'Authorization': 'Bearer ' + api_key,
            'Content-Type': 'application/json',
        }
        payload = {
            'model': 'openai/gpt-oss-20b',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': self.question or ''},
            ],
            'temperature': 0.3,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        answer_text = response.json()['choices'][0]['message']['content'].strip()

        self.answer = answer_text

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'shopify.chatbot.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
