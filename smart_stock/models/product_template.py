from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rotation_classification = fields.Selection([
        ('a', 'Class A (High Turnover)'),
        ('b', 'Class B (Medium Turnover)'),
        ('c', 'Class C (Low Turnover)')
    ], string='Rotation Classification')

    safety_stock_days = fields.Integer(
        string='Safety Stock Days', 
        default=7,
        help="Extra days of inventory to buffer demand spikes."
    )
    is_seasonal = fields.Boolean(
        string='Seasonal Product', 
        default=False
    )

    last_purchase_cost = fields.Float(
        compute='_compute_last_purchase_cost',
        string='Last Purchase Cost',
        readonly=True,
        help='Shows the cost if there is only one variant. If there are multiple, check each variant\'s sheet.'
    )

    @api.depends('product_variant_ids', 'product_variant_ids.last_purchase_cost')
    def _compute_last_purchase_cost(self):
        for template in self:
            # If there is only one variant, we display its exact price in the template
            if len(template.product_variant_ids) == 1:
                template.last_purchase_cost = template.product_variant_ids[0].last_purchase_cost
            else:
                # If there are multiple variants, the cost varies for each one.
                template.last_purchase_cost = 0.0