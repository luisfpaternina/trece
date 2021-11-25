# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class RutasHorarios(models.Model):
    _name = 'lcd.rutas_horarios'
    _description = 'Rutas y Horarios'

    name=fields.Char('Número de Ruta')
    camion_id=fields.Many2one('camion.camion','Camión')
    fecha_despacho=fields.Date('Fecha Despacho')
    bodega_id=fields.Many2one('bodega.bodega','Bodega')
    optimizacion_id=fields.Many2one('optimizacion.logistica','Optimización')
    zona_id=fields.Many2one('sale.order.zona','Zona')
    estado=fields.Selection([('borrador','Borrador'),('en_proceso','En Proceso'),('terminado','Terminado')],'Estado')

class RutasHorariosDetalle(models.Model):
    _name = 'lcd.rutas_horarios_detalle'
    _description = 'Detalle de Rutas y Horarios'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    optimizacion_id=fields.Many2one('optimizacion.logistica')
    order_line_id=fields.Many2one('sale.order.line','Linea de OV')
    pedido=fields.Char(related='order_line_id.order_id.name','Pedido')
    fecha_pedido=fields.DateTime(related='order_line_id.order_id.date_order','Fecha Pedido')
    partner_id=fields.Many2one('res.partner',related='order_line_id.order_id.partner_id','Cliente')
    direccion=fields.Many2one('res.partner',related='order_line_id.order_id.partner_id.street','Dirección')
    product_id=fields.Many2one('product.product',related='order_line_id.product_id','Producto')
    volumen=fields.Float(related='order_line_id.product_id.volume','Volumen')
    cantidad=fields.Float('Cantidad')
    fecha_cierta=fields.Date(related='order_line_id.order_id.fecha_cierta','Fecha Cierta')
    categ_id=fields.Many2one('product.category',related='order_line_id.product_id.categ_id','Categoría')
    zona_id=fields.Many2one('sale.order.zona',related='order_line_id.order_id.zona_id','Zona')
    canal_venta_id=fields.Many2one('sale.order.canal',related='order_line_id.order_id.canal_venta_id','Canal de Venta')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',related='order_line_id.order_id.tipo_entrega_id','Tipo Entrega')

