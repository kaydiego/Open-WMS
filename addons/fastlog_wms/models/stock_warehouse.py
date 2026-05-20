from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    fastlog_branch_code = fields.Char(
        string="Fastlog-Niederlassung",
        help="Interner Niederlassungscode der Fastlog AG für dieses Lager.",
    )
