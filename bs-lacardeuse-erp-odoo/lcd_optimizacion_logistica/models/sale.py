# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import datetime
from odoo import api, fields, models, tools, SUPERUSER_ID

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fecha_cierta=fields.Date('Fecha Cierta')
    canal_venta_id=fields.Many2one('sale.order.canal','Canal de Venta')
    pedido_sin_optimizar=fields.Boolean('Pedido sin Optimizar')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega','Tipo de Entrega')
    zona_id=fields.Many2one('sale.order.zona','Zona')
    bolsa_id=fields.Many2one('bolsa.ventas','Bolsa de Ventas')

    @api.onchange('partner_id')
    def onchange_partner_id_lcd(self):
        if self.partner_id.tipo_entrega_id:
            self.tipo_entrega_id=self.partner_id.tipo_entrega_id.id
        if self.partner_id.canal_venta_id:
            self.canal_venta_id=self.partner_id.canal_venta_id.id
        if self.partner_id.zona_id:
            self.zona_id=self.partner_id.zona_id.id

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.env['bolsa.ventas'].chequear_bolsa()
        return res 

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bolsa_detalle_id=fields.Many2one('bolsa.ventas.detalle','Línea bolsa detalle')

class SaleOrderCanal(models.Model):
    _name = 'sale.order.canal'
    _description = 'Canal de Venta'

    name=fields.Char('Nombre')
    codigo=fields.Char('Código')
    dias_maximos=fields.Integer('Días Máximos')

class SaleOrderTipoEntrega(models.Model):
    _name = 'sale.order.tipo_entrega'
    _description = 'Tipo de Entrega'

    name=fields.Char('Nombre')
    codigo=fields.Char('Código')
    tiempo_entrega=fields.Integer('Tiempo de Entrega (minutos)')

class SaleOrderZona(models.Model):
    _name = 'sale.order.zona'
    _description = 'Zona'

    name=fields.Char('Nombre')
    codigo=fields.Char('Código')
