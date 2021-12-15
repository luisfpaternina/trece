from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def message_new(self, msg, custom_values=None):
        canal_obj = self.env["helpdesk.ticket.type"]
        canal_obj.search([("name","=","Contacto")],limit = 1)
        channel_obj = self.env["helpdesk.ticket.channel"]
        channel_obj.search([("name","=","Defensa Consumidor")],limit = 1)
        if msg.get("from") == 'test@luisfpaternina-trece-25-11-2021-3678198.dev.odoo.com':
            _logger.info("entro al if****************************")
            defaults["canal_id"] = canal_obj.id
            defaults["priority"] = "3"
            defaults["channel_id"] = channel_obj.id
            _logger.info(defaults)
        ticket = super().message_new(msg, custom_values=defaults)
        return ticket