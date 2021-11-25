# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date
import base64


class Account_Tax(models.Model):
    _inherit = 'account.tax'
    

    tipo_txt=fields.Selection([('piibbarbaa', 'Percepción IIBB ARBA Aplicada'),('riibbarbaa', 'Retención IIBB ARBA Aplicada'),('piibbcabaa', 'Percepción IIBB CABA Aplicada'),('riibbcabaa', 'Retención IIBB CABA Aplicada')],'Tipo Generación TXT')


