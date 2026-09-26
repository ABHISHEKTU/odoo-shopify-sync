{
    'name': 'Shopify Sync',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Sync products and orders between Odoo and Shopify',
    'license': 'LGPL-3',
    'depends': ['sale', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/order_views.xml',
        'views/enrichment_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
}
