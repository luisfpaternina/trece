{
    'name': 'Analytic Account Team',
    'version': '1.0',
    'description': 'This module create a field to select analytic account in teams',
    'author': 'Nybble Group',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': [
        'sale_management',
        'account'
    ],
    'data': [
        'views/crm_team_view.xml',
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',
        'views/res_tarjeta_view.xml',
        'views/promotion_card_view.xml',
        'views/coeficiente_tarjetas_view.xml',

    ],
    'auto_install': True,
    'application': True,
}