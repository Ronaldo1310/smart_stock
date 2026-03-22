from odoo import models, fields, api

class ProductStockDailyLog(models.Model):
    _name = 'product.stock.daily.log'
    _description = 'Daily Stock Out Log'
    _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True, 
        ondelete='cascade'
    )
    date = fields.Date(
        string='Date', 
        default=fields.Date.context_today, 
        required=True
    )
    is_out_of_stock = fields.Boolean(
        string='Out of Stock', 
        default=True
    )

    _sql_constraints = [
        ('unique_product_date', 'unique(product_id, date)', 'The stock out log entry for a product and date must be unique.')
    ]