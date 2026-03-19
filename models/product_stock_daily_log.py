from odoo import models, fields, api

class ProductStockDailyLog(models.Model):
    _name = 'product.stock.daily.log'
    _description = 'Registro Diario de Quiebres de Stock'
    _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', 
        string='Producto', 
        required=True, 
        ondelete='cascade'
    )
    date = fields.Date(
        string='Fecha', 
        default=fields.Date.context_today, 
        required=True
    )
    is_out_of_stock = fields.Boolean(
        string='Sin Stock', 
        default=True
    )

    _sql_constraints = [
        ('unique_product_date', 'unique(product_id, date)', 'El registro de quiebre de stock por producto y fecha debe ser único.')
    ]