from odoo import models, fields

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    is_auto_generated = fields.Boolean(
        string='Generada Automáticamente', 
        default=False, 
        readonly=True,
        copy=False,
        help='Indica si esta licitación fue generada por el sistema.'
    )