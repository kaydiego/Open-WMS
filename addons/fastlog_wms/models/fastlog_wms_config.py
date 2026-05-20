from odoo import fields, models


class FastlogWmsConfig(models.Model):
    _name = "fastlog.wms.config"
    _description = "Fastlog-WMS Konfiguration"

    name = fields.Char(required=True)
    warehouse_id = fields.Many2one("stock.warehouse", required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text()
