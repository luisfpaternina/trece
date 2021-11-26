from odoo import models,api,fields, _


class ResTarjeta(models.Model):
    _name = 'res.tarjeta'
    _description = 'model res tarjeta'

    name = fields.Char(string='Name')
    code = fields.Integer(string='Code')
    type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Dedit')
    ], string='Card Type')
    shopin = fields.Char(string='Shopin')
    codglamit = fields.Char(string='Codglamit')
     