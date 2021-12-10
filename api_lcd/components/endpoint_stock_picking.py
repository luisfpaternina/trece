from odoo.addons.component.core import Component
from odoo.addons.base_rest import restapi
import json
import logging
_logger = logging.getLogger(__name__)


class StockPicking(Component):
    _inherit = 'base.rest.service'
    _name = 'stock.picking.service'
    _usage = 'Stock Picking'
    _collection = 'contact.services.private.services'
    _description = """
         API Services to search Stock Picking
    """
    
    @restapi.method(
        [(["/<string:name>/search"], "GET")],
        output_param=restapi.CerberusValidator("_validator_search"),
        auth="public",
    )
    
    def search(self, name):
        _logger.info(name)
        stock_picking = self.env["stock.picking"].name_search(name)
        stock_picking = self.env["stock.picking"].browse([i[0] for i in stock_picking])
        if stock_picking:
            for pick in stock_picking:
                res = {
                        "id": pick.id,
                        "code": pick.code,
                        "name": name,
                        "pick_code_prefix": pick.pick_code_prefix,
                        "purchase_aliquots": pick.purchase_aliquots,
                        "report_name": pick.report_name,
                        "internal_type": pick.report_name,
                        "country_id": pick.country_id.id,
                        "country_name": pick.country_id.name,
                        }
        else:
            res = {
                    "message": "No existe una trasferencia con este nombre"
                    }
        return res
    
    def _validator_search(self):
        res = {
                "id": {"type":"integer", "required": False},
                "code": {"type":"string", "required": False},
                "name": {"type":"string", "required": False},
                "message": {"type":"string", "required": False},
                "pick_code_prefix": {"type":"string", "required": False},
                "purchase_aliquots": {"type":"string", "required": False},
                "report_name": {"type":"string", "required": False},
                "internal_type": {"type":"string", "required": False},
                "country_id": {"type":"integer", "required": False},
                "country_name": {"type":"string", "required": False},
              }
        return res
