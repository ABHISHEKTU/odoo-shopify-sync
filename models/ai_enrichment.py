import requests
import json
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

BACKTICK = chr(96)


class ProductTemplateEnrichment(models.Model):
    _inherit = 'product.template'

    ai_marketing_copy = fields.Text(string='AI Marketing Description')
    ai_seo_title = fields.Char(string='AI SEO Title')
    ai_seo_tags = fields.Char(string='AI SEO Tags')

    def action_enrich_with_ai(self):
        icp = self.env['ir.config_parameter'].sudo()
        api_key = icp.get_param('shopify_sync.groq_api_key')

        if not api_key:
            raise Exception('Groq API key not configured in System Parameters.')

        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {
            'Authorization': 'Bearer ' + api_key,
            'Content-Type': 'application/json',
        }

        for product in self:
            prompt = (
                'You are an e-commerce copywriter. For the product "' + product.name +
                '", generate a JSON object with exactly these keys: '
                '"marketing_copy" (a 2-3 sentence engaging product description), '
                '"seo_title" (a short SEO-friendly title, under 60 characters), '
                '"seo_tags" (a comma-separated list of 5 relevant SEO keywords). '
                'Respond with ONLY the raw JSON object, no markdown, no explanation.'
            )

            payload = {
                'model': 'openai/gpt-oss-20b',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7,
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].strip()

            fence = BACKTICK * 3
            content = content.replace(fence + 'json', '').replace(fence, '').strip()

            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                _logger.error('Failed to parse AI response for %s: %s', product.name, content)
                continue

            product.write({
                'ai_marketing_copy': data.get('marketing_copy', ''),
                'ai_seo_title': data.get('seo_title', ''),
                'ai_seo_tags': data.get('seo_tags', ''),
            })
            _logger.info('Enriched product %s with AI content', product.name)

        return False
