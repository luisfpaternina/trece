from odoo import models , fields, api, _

class CoeficienteTarjetas(models.Model):
    _name = 'coeficiente.tarjetas'
    _description = 'Coeficiente Tarjetas'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    bank_id = fields.Many2one('res.bank',
        string='Bank')
    bank_code = fields.Char(string='Bank Code',
        related="bank_id.bic")
    card_id = fields.Many2one('res.tarjeta',
        string="Card")
    card_code = fields.Integer(string='Card Code',
        related="card_id.code")
    quota = fields.Integer(string='Quota')
    rate = fields.Float(string='Rate')