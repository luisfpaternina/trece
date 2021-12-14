from odoo import models, api, fields, models, _
from odoo.tools import float_compare, float_round


class Task(models.Model):
    _inherit = "project.task"

    recurrence_id = fields.Many2one('project.task.recurrence', copy=False)
