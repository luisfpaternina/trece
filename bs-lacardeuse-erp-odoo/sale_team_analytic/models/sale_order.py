from odoo import fields,models,api,_

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("team_id")
    def analytic_account_team(self):
        self.analytic_account_id = self.team_id.analytic_account_id.id
