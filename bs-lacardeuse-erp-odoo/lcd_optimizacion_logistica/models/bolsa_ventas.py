# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import datetime
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class BolsaVentas(models.Model):
    _name = 'bolsa.ventas'
    _description = 'Bolsa de Ventas'

    fecha=fields.Date('Fecha')
    name=fields.Char('Número')
    estado=fields.Selection([('abierta','Abierta'),('en_proceso','En Proceso'),('cerrada','Cerrada')],string='Estado',default='abierta')
    bolsa_lines=fields.One2many('bolsa.ventas.detalle','bolsa_id','Items')

    def chequear_bolsa(self):
        #Armo un diccionario de categorias con sus capacidades de fabricacion
        categorias=self.env['product.category'].search([]).read(['id','capacidad_fabricacion'])
        dict_categ={}
        categorias_cant={}
        for item in categorias:
            dict_categ[item['id']]=item['capacidad_fabricacion']
            categorias_cant[item['id']]=0
        #####################################################################
        #Recorro pedidos que no estan en bolsa y chequeo si excede capacidad
        excede_limite=False
        bolsa_pedidos=[]
        ordenes=self.env['sale.order'].search([('bolsa_id','=',False)],order="date_order")
        for orden in ordenes:
            bolsa_pedidos.append(orden.id)
            for linea in orden.order_line:
                categorias_cant[linea.product_id.categ_id.id]=categorias_cant[linea.product_id.categ_id.id]+linea.product_uom_qty
                #Si la cantidad de la ov excede la capacidad de fabricacion cierro bolsa
                if categorias_cant[linea.product_id.categ_id.id]>dict_categ[linea.product_id.categ_id.id] and dict_categ[linea.product_id.categ_id.id]!=0:
                    excede_limite=True
            if excede_limite==True:
                break
        parametro=self.env['ir.config_parameter'].search([('key','=','optimizacion.dias_venta')])
        ultima_bolsa=self.env['bolsa.ventas'].search([],order="fecha desc",limit=1)
        if ultima_bolsa:
            fecha_comparacion=ultima_bolsa.fecha
        else:
            #Si no tengo bolsa para comparar, agarro la orden mas vieja sin bolsa asociada
            orden=self.env['sale.order'].search([('bolsa_id','=',False)],order="date_order",limit=1)
            if orden:
                fecha_comparacion=orden.date_order
            else:
                fecha_comparacion=datetime.datetime.today()
        #Si se excede el límite de fabricación por categoria o se cumple la cantidad de días de bolsa definido, creo nueva bolsa
        if excede_limite or (datetime.date.today()-fecha_comparacion).days>=int(parametro.value):
            lineas_bolsa=[]
            pedidos=self.env['sale.order'].browse(bolsa_pedidos)
            for line in self.env['sale.order.line'].search([('order_id','in',pedidos.ids)]):
                lineas_bolsa.append((0, 0, {'order_line_id': line.id,'estado':'pendiente'}))
            bolsa=self.env['bolsa.ventas'].create({'fecha':datetime.datetime.today(),'name':self.env['ir.sequence'].next_by_code('bolsa.ventas'),'bolsa_lines':lineas_bolsa})
            pedidos.write({'bolsa_id':bolsa.id})

class BolsaVentasDetalle(models.Model):
    _name = 'bolsa.ventas.detalle'
    _description = 'Detalle de Bolsa de Ventas'

    bolsa_id=fields.Many2one('bolsa.ventas','Bolsa de Ventas')
    order_line_id=fields.Many2one('sale.order.line','Linea de OV')
    pedido=fields.Char(related='order_line_id.order_id.name',string='Pedido',store=True)
    fecha_pedido=fields.Datetime(related='order_line_id.order_id.date_order',string='Fecha Pedido',store=True)
    partner_id=fields.Many2one('res.partner',related='order_line_id.order_id.partner_id',string='Cliente',store=True)
    direccion=fields.Char(related='order_line_id.order_id.partner_id.street',string='Dirección',store=True)
    product_id=fields.Many2one('product.product',related='order_line_id.product_id',string='Producto',store=True)
    volumen=fields.Float(related='order_line_id.product_id.volume',string='Volumen',store=True)
    fecha_cierta=fields.Date(related='order_line_id.order_id.fecha_cierta',string='Fecha Cierta',store=True)
    categ_id=fields.Many2one('product.category',related='order_line_id.product_id.categ_id',string='Categoría',store=True)
    zona_id=fields.Many2one('sale.order.zona',related='order_line_id.order_id.zona_id',string='Zona',store=True)
    canal_venta_id=fields.Many2one('sale.order.canal',related='order_line_id.order_id.canal_venta_id',string='Canal de Venta',store=True)
    fecha_canal_venta=fields.Date(string='Fecha Máxima Canal de Venta',store=True,compute='calcular_defaults')
    mayorista=fields.Boolean(string='Mayorista',store=True,compute='calcular_defaults')
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',related='order_line_id.order_id.tipo_entrega_id',string='Tipo Entrega',store=True)
    cantidad=fields.Float(related='order_line_id.product_uom_qty',string='Cantidad',store=True)
    cantidad_a_realizar=fields.Float(string='Cantidad A Realizar',default=0)
    cantidad_realizada=fields.Float(string='Cantidad Realizada',default=0)
    estado=fields.Selection([('pendiente','Pendiente'),('en_proceso','En Proceso'),('optimizado','Optimizado'),('cancelado','Cancelado')],string='Estado',default='pendiente')

    def calcular_defaults(self):
        for rec in self:
            rec.fecha_canal_venta=fields.Date.from_string(rec.fecha_pedido)+datetime.timedelta(days=rec.canal_venta_id.dias_maximos)
            etiquetas_mayoristas=self.env['ir.config_parameter'].search([('key','=','optimizacion.etiquetas_mayoristas')])
            if etiquetas_mayoristas:
                etiquetas_mayoristas=etiquetas_mayoristas.value.split(',')
                for tag in rec.partner_id.category_id:
                    if tag.id in etiquetas_mayoristas:
                        rec.mayorista=True
                        break
            else:
                rec.mayorista=False
