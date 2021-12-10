from odoo import models, fields, api, _

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def message_new(self, msg, custom_values=None):
        canal_obj = self.env["helpdesk.ticket.type"]
        canal_obj.search([("name","=","Contacto")],limit = 1)
        channel_obj = self.env["helpdesk.ticket.channel"]
        channel_obj.search([("name","=","Defensa Consumidor")],limit = 1)
        if msg.get("from")=='test2@luisfpaternina-trece-25-11-2021-3678198.dev.odoo.com':
            custom_values["canal_id"] = canal_obj.id
            custom_values["priority"] = "3"
            custom_values["channel_id"] = channel_obj.id
        ticket = super().message_new(msg, custom_values=custom_values)
        return ticket
    