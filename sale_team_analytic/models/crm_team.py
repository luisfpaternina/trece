from odoo import fields,models,api,_

class CrmTeam(models.Model):
    _inherit = "crm.team"

    analytic_account_id = fields.Many2one("account.analytic.account","Analytic Account")

