from odoo import models, fields, _

class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']

    fsm_lot_id = fields.Many2one(
        'stock.production.lot',
        domain="[('product_id', '=', product_id)]")