# -*- coding: utf-8 -*-
# (C) 2020 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "LCD Optimización Logística",
    "version": "0.1",
    "sequence": 100,
    "category": "Nybble",
    "author": "Nybble",
    "license": 'LGPL-3',
    "description": """
Módulo de Optimización Logística para La Cardeuse""",
    "depends": [
        'sale','sales_team','account','multiple_datepicker_widget'
    ],
    "data": [
        'data/data_view.xml',
        'security/ir.model.access.csv',
        'views/bodegas_view.xml',
        'views/camiones_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/optimizacion_logistica_view.xml',
        'views/bolsa_view.xml',
        'views/res_config_settings_view.xml',
        'wizards/wzd_optimizacion_camion_bodega_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
