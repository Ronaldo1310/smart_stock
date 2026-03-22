from odoo import models, fields, api

class ProductRotationHistory(models.Model):
    _name = 'product.rotation.history'
    _description = 'ABC Standings History'
    _order = 'date desc'

    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True, 
        ondelete='cascade'
    )
    date = fields.Date(
        string='Date of Evaluation', 
        default=fields.Date.context_today, 
        required=True
    )
    old_classification = fields.Selection([
        ('a', 'Class A'),
        ('b', 'Class B'),
        ('c', 'Class C'),
        ('none', 'Not Classified')
    ], string='Previous Classification')
    
    new_classification = fields.Selection([
        ('a', 'Class A'),
        ('b', 'Class B'),
        ('c', 'Class C')
    ], string='New Classification', required=True)
    
    revenue_in_period = fields.Float(string='Revenue in the Period')