from odoo import models,api,fields, _


class PromotionCard(models.Model):
    _name = 'promotion.card'
    _description = 'promotion card model'

    name = fields.Char(string='',default="Promotion Card Update")
    res_card_id = fields.Many2one('res.tarjeta', string='Card Name')
    card_code = fields.Char(related="res_card_id.code")
    res_bank_id = fields.Many2one('res.bank', string='Bank')
    bank_code = fields.Char(related="res_bank_id.bic")
    start_date = fields.Date(string='Start date promotion')
    monday = fields.Boolean(string="Monday")
    tuesday = fields.Boolean(string="Tuesday")
    wednesday = fields.Boolean(string="Wednesday")
    thurday = fields.Boolean(string="Thurday")
    friday = fields.Boolean(string="Friday")
    saturday = fields.Boolean(string="Saturday")
    sunday = fields.Boolean(string="Sunday")
    all_days = fields.Boolean(string="All days")
    end_date = fields.Date(string='End date promotion')
    percentage = fields.Float(string='Discount Percentage (%)')
    promotion_ids = fields.One2many('promotion.card.lines', 'promotion_id', string='')

    
class PromotionCardLines(models.Model):
    _name = 'promotion.card.lines'
    _description = 'promotion card lines model'
    _rec_name = 'team_id'
    
    team_id = fields.Many2one('crm.team',string="Branches to offer")    
    promotion_id = fields.Many2one('promotion.card',string="promotion card")
    
    _sql_constraints = [
        ('team_unique',
         'unique (team_id)',
        "You cannot select same branches to offer")
    ]