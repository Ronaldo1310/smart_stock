from odoo import models, fields, api, tools

class SmartReplenishmentDashboard(models.Model):
    _name = 'smart.replenishment.dashboard'
    _description = 'Dynamic Analysis of Rotation and Replenishment'
    _auto = False  

    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    categ_id = fields.Many2one('product.category', 'Category', readonly=True)
    rotation_classification = fields.Selection([
        ('a', 'Class A (High)'),
        ('b', 'Class B (Medium)'),
        ('c', 'Class C (Low)')
    ], string='Clasificación ABC', readonly=True)
    date = fields.Date('Date', readonly=True)
    qty_sold = fields.Float('Quantity Sold', readonly=True)
    revenue = fields.Float('Revenue Generated', readonly=True)
    current_forecast = fields.Float('Daily Forecast', readonly=True)

    def init(self):
        # This function runs when the module is installed or updated
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

    @api.model
    def get_dashboard_data(self):
        # 1. Contadores de Clasificación
        class_a = self.env['product.template'].search_count([('rotation_classification', '=', 'a')])
        class_b = self.env['product.template'].search_count([('rotation_classification', '=', 'b')])
        class_c = self.env['product.template'].search_count([('rotation_classification', '=', 'c')])

        # 2. Productos que requieren reabastecimiento
        products = self.env['product.product'].search([
            ('current_forecasted_demand', '>', 0),
            ('seller_ids', '!=', False)
        ])
        replenish_ids = []
        for p in products:
            primary_seller = p.seller_ids[0]
            rop = (p.current_forecasted_demand * primary_seller.delay) + (p.current_forecasted_demand * p.safety_stock_days)
            virtual_stock = p.qty_available + p.incoming_qty
            if virtual_stock <= rop:
                replenish_ids.append(p.id)

        # 3. Top 10 Rotación (Cantidades)
        self.env.cr.execute("""
            SELECT pt.name, SUM(sm.product_uom_qty) as total_qty
            FROM stock_move sm
            JOIN product_product pp ON sm.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sm.state = 'done' 
              AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'customer')
              AND sm.date >= date_trunc('month', CURRENT_DATE)
            GROUP BY pt.name ORDER BY total_qty DESC LIMIT 10
        """)
        top_rotation = self.env.cr.dictfetchall()

        # 4. Top 10 Ingresos
        self.env.cr.execute("""
            SELECT pt.name, SUM(sm.product_uom_qty * pt.list_price) as total_revenue
            FROM stock_move sm
            JOIN product_product pp ON sm.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sm.state = 'done' 
              AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'customer')
              AND sm.date >= date_trunc('month', CURRENT_DATE)
            GROUP BY pt.name ORDER BY total_revenue DESC LIMIT 10
        """)
        top_revenue = self.env.cr.dictfetchall()

        # --- CORRECCIÓN: Función auxiliar para extraer el nombre en texto plano ---
        user_lang = self.env.user.lang or 'es_ES'
        
        def parse_name(name_field):
            if isinstance(name_field, dict):
                # Intenta sacar el idioma del usuario, si no, saca el primer idioma disponible
                return name_field.get(user_lang, list(name_field.values())[0] if name_field else 'Unknown')
            return name_field or 'Unknown'

        return {
            'counts': {
                'class_a': class_a,
                'class_b': class_b,
                'class_c': class_c,
                'replenish_count': len(replenish_ids),
                'replenish_ids': replenish_ids,
            },
            'top_rotation': {
                'labels': [parse_name(r['name']) for r in top_rotation],
                'data': [r['total_qty'] for r in top_rotation]
            },
            'top_revenue': {
                'labels': [parse_name(r['name']) for r in top_revenue],
                'data': [r['total_revenue'] for r in top_revenue]
            }
        }
    
    @api.model
    def get_secondary_dashboard_data(self):
        # 1. KPIs
        total_products = self.env['product.product'].search_count([('type', '=', 'product')])
        
        # Valoración aproximada del inventario (Stock x Costo)
        self.env.cr.execute("""
            SELECT SUM(pp.qty_available * pt.standard_price) 
            FROM product_product pp 
            JOIN product_template pt ON pp.product_tmpl_id = pt.id 
            WHERE pt.type = 'product' AND pp.qty_available > 0
        """)
        total_valuation = self.env.cr.fetchone()[0] or 0.0

        # Valor de las Órdenes de Compra Automáticas en Borrador
        self.env.cr.execute("""
            SELECT SUM(amount_total) 
            FROM purchase_order 
            WHERE state = 'draft' AND is_auto_generated = TRUE
        """)
        pending_po_value = self.env.cr.fetchone()[0] or 0.0

        class_a_count = self.env['product.template'].search_count([('rotation_classification', '=', 'a')])

        # 2. Gráfico Donut: Distribución ABC
        class_b_count = self.env['product.template'].search_count([('rotation_classification', '=', 'b')])
        class_c_count = self.env['product.template'].search_count([('rotation_classification', '=', 'c')])

        # 3. Gráfico de Líneas: Tendencia de Ingresos (Últimos 6 meses)
        self.env.cr.execute("""
            SELECT to_char(date_trunc('month', sm.date), 'Mon YYYY') as month,
                   SUM(sm.product_uom_qty * pt.list_price) as total
            FROM stock_move sm
            JOIN product_product pp ON sm.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sm.state = 'done' AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'customer')
              AND sm.date >= date_trunc('month', CURRENT_DATE - INTERVAL '5 months')
            GROUP BY date_trunc('month', sm.date)
            ORDER BY date_trunc('month', sm.date) ASC
        """)
        trend_data = self.env.cr.dictfetchall()

        return {
            'kpis': {
                'total_products': total_products,
                'total_valuation': round(total_valuation, 2),
                'pending_po_value': round(pending_po_value, 2),
                'class_a_count': class_a_count,
            },
            'abc_donut': [class_a_count, class_b_count, class_c_count],
            'revenue_trend': {
                'labels': [r['month'] for r in trend_data],
                'data': [round(r['total'], 2) for r in trend_data]
            }
        }