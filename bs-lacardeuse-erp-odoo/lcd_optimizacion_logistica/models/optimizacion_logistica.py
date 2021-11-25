# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class OptimizacionLogistica(models.Model):
    _name = 'optimizacion.logistica'
    _description = 'Optimización Logística'

    name=fields.Char('Número')
    fecha=fields.Char('Fechas')
    fechas_fabricacion=fields.Char('Fechas de Fabricación',required=True)
    fechas_entrega=fields.Char('Fechas de Entrega',required=True)
    estado=fields.Selection([('pendiente','Pendiente'),('en_proceso','En Proceso'),('optimizado','Optimizado'),('cancelado','Cancelado')],'Estado',default='pendiente')
    items=fields.One2many('optimizacion.logistica.detalle','optimizacion_id','Items')
    totales_categ=fields.One2many('optimizacion.logistica.detalle_categ','optimizacion_id','Totales X Categoría')
    totales_prod=fields.One2many('optimizacion.logistica.detalle_prod','optimizacion_id','Totales X Producto')

    @api.model
    def create(self, vals):
        #Chequeo que la cantidad de dias de fabricacion sean igual a la cantidad de dias de entrega
        fechas_fab=vals['fechas_fabricacion'].split(',')
        fechas_ent=vals['fechas_entrega'].split(',')
        if len(fechas_fab)!=len(fechas_ent):
            raise UserError('La cantidad de días de fecha de entrega debe ser igual a la cantidad de días de fecha de fabricación')
        #Chequeo que las fechas no esten ocupadas en otra optimizacion
        for fecha in fechas_fab:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_fabricacion ilike '%"+fecha+"%'")
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de fabricación "'+fecha+'" ya se encuentra ocupada en otra optimización')
        for fecha in fechas_ent:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_entrega ilike '%"+fecha+"%'")
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de entrega "'+fecha+'" ya se encuentra ocupada en otra optimización')
        #Asigno nombre por secuencia
        vals['name']=self.env['ir.sequence'].next_by_code('optimizacion.logistica')
        return super(OptimizacionLogistica, self).create(vals)

    def write(self, vals):
        res = super(OptimizacionLogistica, self).write(vals)
        #Chequeo que la cantidad de dias de fabricacion sean igual a la cantidad de dias de entrega
        fechas_fab=self.fechas_fabricacion.split(',')
        fechas_ent=self.fechas_entrega.split(',')
        if len(fechas_fab)!=len(fechas_ent):
            raise UserError('La cantidad de días de fecha de entrega debe ser igual a la cantidad de días de fecha de fabricación')
        #Chequeo que las fechas no esten ocupadas en otra optimizacion
        for fecha in fechas_fab:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_fabricacion ilike '%"+fecha+"%' and id<>"+str(self.id))
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de fabricación "'+fecha+'" ya se encuentra ocupada en otra optimización')
        for fecha in fechas_ent:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_entrega ilike '%"+fecha+"%' and id<>"+str(self.id))
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de entrega "'+fecha+'" ya se encuentra ocupada en otra optimización')
        return res

    #en base a una fecha, devuelve la siguente fecha de fabricación si tipo es 0 y devuelve la siguente fecha de entrega si tipo es 1
    def get_next_fecha(self,fecha,tipo):
        if tipo==0:
            fechas=self.fechas_fabricacion.split(',')
        else:
            fechas=self.fechas_entrega.split(',')
        index=0
        total_fechas=len(fechas)
        print('index:',index)
        print('total_fechas:',total_fechas)
        while index<(total_fechas-1):
            print('index:',index)
            print('fechas[index]:',fechas[index][-4:]+"-"+fechas[index][:2]+"-"+fechas[index][3:-5])
            print('fecha:',fecha)
            if fechas[index][-4:]+"-"+fechas[index][:2]+"-"+fechas[index][3:-5]==fecha:
                return fechas[index+1][-4:]+"-"+fechas[index+1][:2]+"-"+fechas[index+1][3:-5]
            index+=1
        return False

    def cargar_optimizacion(self):
        self.items.unlink()
        lista_prioridad_maxima=[]
        lista_sin_prioridad=[]
        producto_fabricable=self.env.ref('mrp.route_warehouse0_manufacture').id
        fechas_ent=self.fechas_entrega.split(',')
        fechas_fab=self.fechas_fabricacion.split(',')
        fechas_string=""
        for item in fechas_ent:
            fechas_string+="'"+item[-4:]+item[:2]+item[3:-5]+"',"
        fechas_string=fechas_string[:-1]
        #Son de prioridad máxima aquellas lineas cuya fecha cierta coincida con la fecha de entrega seleccionada
        #Son de prioridad máxima aquellas lineas cuya fecha de entrega de pedido llega a los dias maximos por canal de venta de entrega
        consulta_max="select bvd.id from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad and (bvd.fecha_cierta in ("+fechas_string+") or bvd.fecha_canal_venta in ("+fechas_string+")) order by bv.fecha"
        self.env.cr.execute(consulta_max)
        for item in self.env.cr.fetchall():
            lista_prioridad_maxima.append(item[0])
#        lista_prioridad_maxima+=self.env['bolsa.ventas.detalle'].search([('estado','in',['pendiente','en_proceso']),('fecha_cierta','in',fechas_ent),('cantidad_a_realizar','<','cantidad')], order='bolsa_id.fecha').ids
#        lista_prioridad_maxima+=self.env['bolsa.ventas.detalle'].search([('estado','in',['pendiente','en_proceso']),('fecha_canal_venta','in',fechas_ent),('cantidad_a_realizar','<','cantidad'),('id','not in', lista_prioridad_maxima)],order='bolsa_id.fecha').ids
        consulta="select bvd.id from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad and bvd.id not in ("+consulta_max+") order by bv.fecha"
#        lista_sin_prioridad=self.env['bolsa.ventas.detalle'].search([('estado','in',['pendiente','en_proceso']),('cantidad_a_realizar','<','cantidad'),('id','not in', lista_prioridad_maxima)], order='bolsa_id.fecha').ids
        self.env.cr.execute(consulta)
        for item in self.env.cr.fetchall():
            lista_sin_prioridad.append(item[0])
        porcentaje_mayoristas=self.env['ir.config_parameter'].search([('key','=','optimizacion.maximo_fabricacion_mayoristas')])
        if not porcentaje_mayoristas:
            raise UserError('Es necesario definir un porcentaje de distribución Mayoristas')
        porcentaje_mayoristas=porcentaje_mayoristas.value
        #Armo un diccionario de categorias con sus capacidades de fabricacion
        categorias=self.env['product.category'].search([]).read(['id','capacidad_fabricacion'])
        #dict_categ Contiene un diccionario con el id de la categoría y una lista con: 1- su capacidad maxima de fabricación 2- su capacidad maximo según el porcentaje mayorista
        dict_categ={}
        #categorias_cant Contiene un diccionario con el id de la categoría y: 1- la cantidad actual que se va completando para optimizar 2- cantidad mayorista que se va completando, 3- fecha de fabricacion
        categorias_cant={}
        for item in categorias:
            dict_categ[item['id']]=[item['capacidad_fabricacion'],round(float(item['capacidad_fabricacion'])*float(porcentaje_mayoristas)/100),0]
            categorias_cant[item['id']]=[0,0,fechas_fab[0][-4:]+"-"+fechas_fab[0][:2]+"-"+fechas_fab[0][3:-5]]
        #####################################################################
        #lineas_a_optimizar lista de (id bolsa detalle,cant a optimizar,cant total-cant realizada,categoria,mayorista si/no,fabricar si/no)
        lineas_a_optimizar=[]
        #lineas_pendientes lista de (id bolsa detalle,cant remanente,categoria,indice)
        lineas_pendientes=[]
        #Pongo en lineas_a_optimizar las que tienen prioridad primero y despues las que tienen menor prioridad, llevo al limite de la capacidad si es que está por excederla
        indice=0
        fin_optimizacion=False
        for linea in self.env['bolsa.ventas.detalle'].browse(lista_prioridad_maxima):
            cantidad_por_fabricar=categorias_cant[linea.product_id.categ_id.id][0]
            cantidad_por_fabricar_mayorista=categorias_cant[linea.product_id.categ_id.id][1]
            fecha_de_fabricacion=categorias_cant[linea.product_id.categ_id.id][2]
            cantidad_a_fabricar_linea=linea.cantidad-linea.cantidad_a_realizar
            cantidad_tope=dict_categ[linea.product_id.categ_id.id][0]
            cantidad_tope_mayorista=dict_categ[linea.product_id.categ_id.id][1]
            print('cantidad_tope:',cantidad_tope)
            print('cantidad_por_fabricar:',cantidad_por_fabricar)
            #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no
            if cantidad_tope==cantidad_por_fabricar:
                print('ES igual')
                fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                print('fecha_de_fabricacion:',fecha_de_fabricacion)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                #Cambio fecha y reseteo contador de capacidad
                categorias_cant[linea.product_id.categ_id.id][0]=0
                categorias_cant[linea.product_id.categ_id.id][1]=0
                categorias_cant[linea.product_id.categ_id.id][2]=fecha_de_fabricacion
                cantidad_por_fabricar=0
                cantidad_por_fabricar_mayorista=0
            #Si tiene cantidad tope=0 entra pero no tiene fabricacion
            if linea.product_id.route_ids ==False or (producto_fabricable not in linea.product_id.route_ids.ids):
                lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,False,fecha_de_fabricacion))
                continue
            #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
            if linea.mayorista==True:
                if cantidad_a_fabricar_linea>cantidad_tope_mayorista-cantidad_por_fabricar_mayorista:
                    #La cantidad mayorista de la linea excede la capacidad mayorista permitida de la categoria, completo hasta la cantidad límite y el remanente lo dejo al final para ver si es posible meterla en la optimizacion
                    lineas_a_optimizar.append((linea.id,cantidad_tope_mayorista-cantidad_por_fabricar_mayorista,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
                    #Si es que hay remanente sin optimizar lo cargo en lineas_pendientes
                    if cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista)>0:
                        lineas_pendientes.append((linea.id,cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista), linea.product_id.categ_id.id, indice))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                else:
                    #La cantidad mayorista de la linea no excede la capacidad mayorista permitida de la categoria, agrego toda la linea
                    lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_a_fabricar_linea
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_a_fabricar_linea
            #Si la cantidad de la linea excede el límite de fabricación, optimizo al maximo posible
            elif cantidad_a_fabricar_linea>cantidad_tope-cantidad_por_fabricar:
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(cantidad_tope-cantidad_por_fabricar)
                lineas_a_optimizar.append((linea.id,cantidad_tope-cantidad_por_fabricar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
            else:
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(linea.cantidad-linea.cantidad_a_realizar)
                lineas_a_optimizar.append((linea.id,linea.cantidad-linea.cantidad_a_realizar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
            indice+=1
        #Pongo en lineas_a_optimizar las que tienen menor prioridad
        for linea in self.env['bolsa.ventas.detalle'].browse(lista_sin_prioridad):
            cantidad_por_fabricar=categorias_cant[linea.product_id.categ_id.id][0]
            cantidad_por_fabricar_mayorista=categorias_cant[linea.product_id.categ_id.id][1]
            fecha_de_fabricacion=categorias_cant[linea.product_id.categ_id.id][2]
            cantidad_a_fabricar_linea=linea.cantidad-linea.cantidad_a_realizar
            cantidad_tope=dict_categ[linea.product_id.categ_id.id][0]
            cantidad_tope_mayorista=dict_categ[linea.product_id.categ_id.id][1]
            print('cantidad_tope:',cantidad_tope)
            print('cantidad_por_fabricar:',cantidad_por_fabricar)
            #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no
            if cantidad_tope==cantidad_por_fabricar:
                print('ES igual')
                fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                print('fecha_de_fabricacion:',fecha_de_fabricacion)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                #Cambio fecha y reseteo contador de capacidad
                categorias_cant[linea.product_id.categ_id.id][0]=0
                categorias_cant[linea.product_id.categ_id.id][1]=0
                categorias_cant[linea.product_id.categ_id.id][2]=fecha_de_fabricacion
                cantidad_por_fabricar=0
                cantidad_por_fabricar_mayorista=0
            #Si tiene cantidad tope=0 entra pero no tiene fabricacion
            if linea.product_id.route_ids ==False or (producto_fabricable not in linea.product_id.route_ids.ids):
                lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,False,fecha_de_fabricacion))
                continue
            #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
            if linea.mayorista==True:
                if cantidad_a_fabricar_linea>cantidad_tope_mayorista-cantidad_por_fabricar_mayorista:
                    #La cantidad mayorista de la linea excede la capacidad mayorista permitida de la categoria, completo hasta la cantidad límite y el remanente lo dejo al final para ver si es posible meterla en la optimizacion
                    lineas_a_optimizar.append((linea.id,cantidad_tope_mayorista-cantidad_por_fabricar_mayorista,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
                    #Si es que hay remanente sin optimizar lo cargo en lineas_pendientes
                    if cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista)>0:
                        lineas_pendientes.append((linea.id,cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista), linea.product_id.categ_id.id, indice))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                else:
                    #La cantidad mayorista de la linea no excede la capacidad mayorista permitida de la categoria, agrego toda la linea
                    lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_a_fabricar_linea
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_a_fabricar_linea
            #Si la cantidad de la linea excede el límite de fabricación, optimizo al maximo posible
            elif cantidad_a_fabricar_linea>cantidad_tope-cantidad_por_fabricar:
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(cantidad_tope-cantidad_por_fabricar)
                lineas_a_optimizar.append((linea.id,cantidad_tope-cantidad_por_fabricar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
            else:
                print('categorias_cant:',categorias_cant)
                print('categorias_cant[linea.product_id.categ_id.id]:',categorias_cant[linea.product_id.categ_id.id])
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(linea.cantidad-linea.cantidad_a_realizar)
                lineas_a_optimizar.append((linea.id,linea.cantidad-linea.cantidad_a_realizar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion))
            indice+=1
            print('lineas_a_optimizar:',lineas_a_optimizar)
        print('#############################################')
        print('lineas_a_optimizar:',lineas_a_optimizar)
        print('#############################################')
        #Chequeo elementos descartados
        for linea in lineas_pendientes:
            #lineas_pendientes lista de (id bolsa detalle,cant remanente,categoria,mayorista si/no)
            cantidad_por_fabricar=categorias_cant[linea[2]][0]
            fecha_de_fabricacion=categorias_cant[linea.product_id.categ_id.id][2]
            cantidad_a_fabricar_linea=linea[1]
            cantidad_tope=dict_categ[linea[2]][0]
            cantidad_tope_mayorista=dict_categ[linea[2]][1]
            #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no
            if cantidad_tope==cantidad_por_fabricar:
                fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                #Cambio fecha y reseteo contador de capacidad
                categorias_cant[linea[2]][0]=0
                categorias_cant[linea[2]][1]=0
                categorias_cant[linea[2]][2]=fecha_de_fabricacion
                cantidad_por_fabricar=0
            #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
            if linea[1]>cantidad_tope-cantidad_por_fabricar:
                #La cantidad remanente de la linea excede la capacidad permitida de la categoria, completo hasta la cantidad límite
                #si la fecha de la linea es la misma que la fecha de la linea a optimizar, la sumo, sino la agrego aparte con la nueva fecha de fabricacion
                if lineas_a_optimizar[linea[3]][6]==fecha_de_fabricacion:
                    lineas_a_optimizar[linea[3]][1]=lineas_a_optimizar[linea[3]][1]+(cantidad_tope-cantidad_por_fabricar)
                else:
#                               0                   1               2                       3           4               5
#lineas_a_optimizar lista de (id bolsa detalle,cant a optimizar,cant total-cant realizada,categoria,mayorista si/no,fabricar si/no)
                    lineas_a_optimizar.append((linea[0], cantidad_tope-cantidad_por_fabricar, cantidad_tope-cantidad_por_fabricar,linea[2], linea[3], True,fecha_de_fabricacion))
                #actualizo cant por fabricar
                dict_categ[linea[2]][0]=dict_categ[linea[2]][0]+cantidad_tope-cantidad_por_fabricar
            else:
                #La cantidad mayorista de la linea no excede la capacidad mayorista permitida de la categoria, agrego toda la linea
                #si la fecha de la linea es la misma que la fecha de la linea a optimizar, la sumo, sino la agrego aparte con la nueva fecha de fabricacion
                if lineas_a_optimizar[linea[3]][6]==fecha_de_fabricacion:
                    lineas_a_optimizar[linea[3]][1]=lineas_a_optimizar[linea[3]][1]+linea[1]
                else:
                    lineas_a_optimizar.append((linea[0], linea[1], cantidad_tope-cantidad_por_fabricar,linea[2], linea[3], True,fecha_de_fabricacion))
                #actualizo cant por fabricar y cant por fabricar mayorista
                categorias_cant[linea[2]][0]=categorias_cant[linea[2]][0]+linea[1]

        #Creo las lineas de optimización   0                1               2                       3           4               5               6
        #lineas_a_optimizar lista de (id bolsa detalle,cant a optimizar,cant total-cant realizada,categoria,mayorista si/no,fabricar si/no,fecha fabricacion)
        for linea in lineas_a_optimizar:
            if linea[1]==0:
                continue
            self.env['optimizacion.logistica.detalle'].create({'optimizacion_id':self.id, 'bolsa_line_id':linea[0], 'cantidad_a_realizar':linea[1], 'fecha_fabricacion':linea[6], 'fabricar':linea[5], 'estado':'borrador'})
            bolsa_det=self.env['bolsa.ventas.detalle'].browse(linea[0])
            bolsa_det.write({'cantidad_a_realizar':bolsa_det.cantidad_a_realizar+linea[1]})
        self.onchange_items()
    #Calculo totales
    @api.onchange('items')
    def onchange_items(self):
        self.totales_categ=False
        self.totales_prod=False
        categs={}
        prods={}
        lista_categs=[]
        lista_prods=[]
        for item in self.items:
            if item.categ_id.name in categs:
                categs[item.categ_id.name]=categs[item.categ_id.name]+item.cantidad_a_realizar
            else:
                categs[item.categ_id.name]=item.cantidad_a_realizar
            if item.product_id.name in prods:
                prods[item.product_id.name]=prods[item.product_id.name]+item.cantidad_a_realizar
            else:
                prods[item.product_id.name]=item.cantidad_a_realizar
        for nombre,cantidad in categs.items():
            lista_categs.append((0, 0, {'name': nombre,'total': cantidad}))
        for nombre,cantidad in prods.items():
            lista_prods.append((0, 0, {'name': nombre,'total': cantidad}))
        self.totales_categ=lista_categs
        self.totales_prod=lista_prods
class OptimizacionLogisticaDetalle(models.Model):
    _name = 'optimizacion.logistica.detalle'
    _description = 'Detalle de Optimizacion Logistica'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    bolsa_line_id=fields.Many2one('bolsa.ventas.detalle','Linea de Bolsa de Ventas')
    bolsa_id=fields.Many2one('bolsa.ventas',related='bolsa_line_id.bolsa_id')
    pedido=fields.Char(related='bolsa_line_id.pedido',string='Pedido',store=True)
    fecha_pedido=fields.Datetime(related='bolsa_line_id.fecha_pedido',string='Fecha Pedido',store=True)
    partner_id=fields.Many2one('res.partner',related='bolsa_line_id.partner_id',string='Cliente',store=True)
    direccion=fields.Char(related='bolsa_line_id.direccion',string='Dirección',store=True)
    product_id=fields.Many2one('product.product',related='bolsa_line_id.product_id',string='Producto',store=True)
    volumen=fields.Float(related='bolsa_line_id.volumen',string='Volumen',store=True)
    fecha_cierta=fields.Date(related='bolsa_line_id.fecha_cierta',string='Fecha Cierta',store=True)
    categ_id=fields.Many2one('product.category',related='bolsa_line_id.categ_id',string='Categoría',store=True)
    zona_id=fields.Many2one('sale.order.zona',related='bolsa_line_id.zona_id',string='Zona',store=True)
    canal_venta_id=fields.Many2one('sale.order.canal',related='bolsa_line_id.canal_venta_id',string='Canal de Venta',store=True)
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',related='bolsa_line_id.tipo_entrega_id',string='Tipo Entrega',store=True)
    cantidad_ov=fields.Float(related='bolsa_line_id.cantidad',string='Cantidad OV')
    cantidad_realizada=fields.Float(related='bolsa_line_id.cantidad_realizada',string='Cantidad Realizada')
    cantidad_a_realizar=fields.Float(string='A Realizar')
    fecha_fabricacion=fields.Date(string='Fecha Fabricación')
    fabricar=fields.Boolean(string='¿Fabricar?')
    estado=fields.Selection([('borrador','Borrador'),('terminado','Terminado')],string='Estado',default='borrador')

    def unlink(self):
        for rec in self:
            rec.bolsa_line_id.write({'cantidad_a_realizar':rec.bolsa_line_id.cantidad_a_realizar-rec.cantidad_a_realizar})
        return super(OptimizacionLogisticaDetalle, self).unlink()

    def write(self, vals):
        if 'cantidad_a_realizar' in vals:
            cant_anterior=self.cantidad_a_realizar
        res = super(OptimizacionLogisticaDetalle, self).write(vals=vals)
        if 'cantidad_a_realizar' in vals:
            cant_nueva=self.cantidad_a_realizar            
        self.bolsa_line_id.write({'cantidad_a_realizar':self.bolsa_line_id.cantidad_a_realizar-(cant_anterior-cant_nueva)})
        return res

class OptimizacionLogisticaDetalleCateg(models.Model):
    _name = 'optimizacion.logistica.detalle_categ'
    _description = 'Detalle de Optimizacion Logistica- Total por Categoría'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    name=fields.Char('Categoría')
    total=fields.Float('Total')

class OptimizacionLogisticaDetalleProd(models.Model):
    _name = 'optimizacion.logistica.detalle_prod'
    _description = 'Detalle de Optimizacion Logistica- Total por Producto'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    name=fields.Char('Producto')
    total=fields.Float('Total')
