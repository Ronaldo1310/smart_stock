from odoo import models, fields, api, tools

class SmartReplenishmentDashboard(models.Model):
    _name = 'smart.replenishment.dashboard'
    _description = 'Análisis Dinámico de Rotación y Reposición'
    _auto = False  # Esto le dice a Odoo que no cree la tabla, nosotros daremos el SQL

    product_id = fields.Many2one('product.product', 'Producto', readonly=True)
    categ_id = fields.Many2one('product.category', 'Categoría', readonly=True)
    rotation_classification = fields.Selection([
        ('a', 'Clase A (Alta)'),
        ('b', 'Clase B (Media)'),
        ('c', 'Clase C (Baja)')
    ], string='Clasificación ABC', readonly=True)
    date = fields.Date('Fecha de Venta', readonly=True)
    qty_sold = fields.Float('Cantidad Vendida', readonly=True)
    revenue = fields.Float('Ingresos Generados', readonly=True)
    current_forecast = fields.Float('Proyección Diaria', readonly=True)

    def init(self):
        # Esta función se ejecuta al instalar/actualizar el módulo
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () as id, -- Odoo exige un ID único
                    pp.id as product_id,
                    pt.categ_id as categ_id,
                    pt.rotation_classification,
                    sm.date::date as date,
                    sm.product_uom_qty as qty_sold,
                    (sm.product_uom_qty * pt.list_price) as revenue, -- Simplificación del ingreso
                    pp.current_forecasted_demand as current_forecast
                FROM stock_move sm
                JOIN product_product pp ON sm.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE sm.state = 'done' 
                  AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'customer')
            )
        """ % (self._table,))