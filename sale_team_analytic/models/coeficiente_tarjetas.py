from odoo import models , fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__) 

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
    
    @api.model
    def create(self,values):
        domain = [
                  ('start_date', '=', values['start_date']),
                  ('end_date', '=', values['end_date']),
                  ('bank_id', '=', values['bank_id']),
                  ('card_id', '=', values['card_id']),
                  ('quota', '=', values['quota']),
                 ]
        object_rate = self.env['coeficiente.tarjetas'].search(domain)
        if object_rate:
            raise UserError(_("Not duplicate with the same range dates, Bank and Card"))
        else:    
            return super(CoeficienteTarjetas, self).create(values)
