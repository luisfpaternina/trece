# -*- coding: utf-8 -*-
{
    'name': 'lcd_perc_ret_sicore',
    'shortdesc': 'Nybble Retenciones/Percepciones, Sicore y Sifere',
    'version': '2.0',
    'summary': 'Adaptaciones personalizadas',
    'sequence': 1,
    'description': """
Adaptaciones
======================
    """,
    'category': 'Nybble Group',
    'website': 'http://www.nybblegroup.com/',
    'images': ['static/src/img/icon.png'],
    'author': 'Federico Rosales',
    'depends': ['base','l10n_ar','l10n_ar_afipws_fe','l10n_ar_account_withholding','account',
    ],
    'data': [
        'views/account_tax_view.xml',
        'wizards/impuestos_x_periodo_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    # 'post_init_hook': '_auto_install_l10n',
}
