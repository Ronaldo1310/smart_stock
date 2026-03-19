from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rotation_classification = fields.Selection([
        ('a', 'Clase A (Alta Rotación)'),
        ('b', 'Clase B (Media Rotación)'),
        ('c', 'Clase C (Baja Rotación)')
    ], string='Clasificación de Rotación')

    safety_stock_days = fields.Integer(
        string='Días de Stock de Seguridad', 
        default=7,
        help="Días extra de inventario para amortiguar picos de demanda."
    )
    is_seasonal = fields.Boolean(
        string='Producto Estacional', 
        default=False
    )