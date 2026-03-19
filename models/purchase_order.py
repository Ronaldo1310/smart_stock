from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Le añadimos readonly=True y copy=False para que no se copie si duplican la PO manualmente
    is_auto_generated = fields.Boolean(
        string='Generada Automáticamente', 
        default=False, 
        readonly=True,
        copy=False,
        help='Indica si esta orden de compra fue generada por el sistema basado en la demanda proyectada.'
    )

    @api.model
    def _create_purchase_orders(self, po_data):
        for partner_id, lines in po_data.items():
            order_lines = []
            for line in lines:
                order_lines.append((0, 0, {
                    'product_id': line['product_id'],
                    'product_qty': line['product_qty'],
                    'price_unit': line['price_unit'],
                }))
                
            self.create({
                'partner_id': partner_id,
                'order_line': order_lines,
                'state': 'draft',
                'origin': 'Smart Replenishment (Automático)',
                'is_auto_generated': True
            })