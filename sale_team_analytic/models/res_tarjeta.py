from odoo import models,api,fields, _


class ResTarjeta(models.Model):
    _name = 'res.tarjeta'
    _description = 'model res tarjeta'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Dedit')
    ], string='Card Type')
    