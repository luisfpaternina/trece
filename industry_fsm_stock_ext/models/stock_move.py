from odoo import models

class StockMove(models.Model):
    _inherit = ['stock.move']

    def _update_reserved_quantity(self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, strict=True):
        lot_id = self.sale_line_id.fsm_lot_id or lot_id
        return super()._update_reserved_quantity(need, available_quantity, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
