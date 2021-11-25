# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class MovimientosBodegas(models.Model):
    _name = 'movimientos.bodegas'
    _description = 'Movimientos Bodegas'

    name=fields.Char('Número Movimiento')
    bodega_origen_id=fields.Many2one('bodega.bodega','Bodega Origen')
    bodega_destino_id=fields.Many2one('bodega.bodega','Bodega Destino')
    camion_origen_id=fields.Many2one('camion.camion','Camión Origen')
    camion_destino_id=fields.Many2one('camion.camion','Camión Destino')
    ruta_horario_id=fields.Many2one('rutas.horarios','Ruta/Horario')
