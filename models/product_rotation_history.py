from odoo import models, fields, api

class ProductRotationHistory(models.Model):
    _name = 'product.rotation.history'
    _description = 'Historial de Clasificación ABC'
    _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', 
        string='Producto', 
        required=True, 
        ondelete='cascade'
    )
    date = fields.Date(
        string='Fecha de Evaluación', 
        default=fields.Date.context_today, 
        required=True
    )
    old_classification = fields.Selection([
        ('a', 'Clase A'),
        ('b', 'Clase B'),
        ('c', 'Clase C'),
        ('none', 'Sin Clasificar')
    ], string='Clasificación Anterior')
    
    new_classification = fields.Selection([
        ('a', 'Clase A'),
        ('b', 'Clase B'),
        ('c', 'Clase C')
    ], string='Nueva Clasificación', required=True)
    
    revenue_in_period = fields.Float(string='Ingresos en el Periodo')