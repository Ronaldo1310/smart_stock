from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Factor Alpha configurable por producto (por defecto 0.3 es un buen estándar)
    smoothing_alpha = fields.Float(
        string='Factor de Suavizado (Alpha)', 
        default=0.3,
        help='Valor entre 0 y 1. Valores altos dan más peso a ventas recientes.'
    )
    
    # Proyección anterior (Ft)
    last_forecasted_demand = fields.Float(
        string='Proyección Anterior (Diaria)', 
        default=0.0,
        readonly=True
    )
    
    # Proyección actual calculada (Ft+1)
    current_forecasted_demand = fields.Float(
        string='Proyección Actual (Diaria)', 
        default=0.0,
        readonly=True
    )



    @api.model
    def _cron_generate_smart_replenishment(self, days_to_cover=30):
        """
        Evalúa el stock actual contra la demanda proyectada y crea 
        Órdenes de Compra o Licitaciones según corresponda.
        """
        # Buscamos productos con demanda proyectada y que tengan proveedores configurados
        products = self.search([
            ('type', '=', 'product'), 
            ('current_forecasted_demand', '>', 0),
            ('seller_ids', '!=', False)
        ])

        # Agruparemos las compras de proveedor único para no hacer 100 POs al mismo proveedor
        po_lines_by_supplier = {}
        tenders_to_create = []

        for product in products:
            demand = product.current_forecasted_demand
            sellers = product.seller_ids
            primary_seller = sellers[0] # Tomamos el proveedor principal como referencia para tiempos
            
            # 1. Variables del Proveedor y Producto
            lead_time = primary_seller.delay
            moq = primary_seller.min_qty
            safety_stock_qty = demand * product.safety_stock_days
            
            # 2. Calcular ROP (Punto de Reorden)
            rop = (demand * lead_time) + safety_stock_qty
            
            # 3. Stock Físico + Compras en Tránsito
            virtual_stock = product.qty_available + product.incoming_qty
            
            # 4. Decisión: ¿Necesitamos comprar?
            if virtual_stock <= rop:
                # Calcular cuánto necesitamos para cubrir los días deseados
                target_stock = (demand * days_to_cover) + safety_stock_qty
                qty_to_order = target_stock - virtual_stock
                
                # 5. Aplicar Restricción del Proveedor (MOQ)
                if qty_to_order < moq:
                    qty_to_order = moq
                    
                # 6. Lógica de Licitación (Múltiples proveedores) vs Compra Directa
                if len(sellers) > 1:
                    # Guardamos la info para crear un Acuerdos de Compra (Tender)
                    tenders_to_create.append({
                        'product_id': product.id,
                        'product_qty': qty_to_order,
                        'sellers': sellers
                    })
                else:
                    # Agrupamos por proveedor para hacer una sola Orden de Compra multiproducto
                    if primary_seller.partner_id.id not in po_lines_by_supplier:
                        po_lines_by_supplier[primary_seller.partner_id.id] = []
                        
                    po_lines_by_supplier[primary_seller.partner_id.id].append({
                        'product_id': product.id,
                        'product_qty': qty_to_order,
                        'price_unit': primary_seller.price,
                    })

        # 7. Ejecutar la creación de documentos en la base de datos
        self._create_purchase_orders(po_lines_by_supplier)
        self._create_purchase_tenders(tenders_to_create)

    # @api.model
    # def _create_purchase_orders(self, po_data):
    #     for partner_id, lines in po_data.items():
    #         order_lines = []
    #         for line in lines:
    #             order_lines.append((0, 0, {
    #                 'product_id': line['product_id'],
    #                 'product_qty': line['product_qty'],
    #                 'price_unit': line['price_unit'],
    #             }))
                
    #         self.create({
    #             'partner_id': partner_id,
    #             'order_line': order_lines,
    #             'state': 'draft',
    #             'origin': 'Smart Replenishment (Automático)',
    #             'is_auto_generated': True
    #         })

    @api.model
    def _create_purchase_tenders(self, tenders_data):
        Requisition = self.env['purchase.requisition']
        for tender in tenders_data:
            Requisition.create({
                'type_id': self.env.ref('purchase_requisition.type_multi', raise_if_not_found=False).id if self.env.ref('purchase_requisition.type_multi', raise_if_not_found=False) else False,
                'line_ids': [(0, 0, {
                    'product_id': tender['product_id'],
                    'product_qty': tender['product_qty'],
                })],
                'origin': 'Licitación Automática (Smart Replenishment)',
                'is_auto_generated': True  # <--- Aquí inyectamos el flag para la licitación
            })

    @api.model
    def _cron_reclassify_abc(self, days_back=30):
        """
        Evalúa las ventas de los últimos X días, aplica Pareto (80/15/5) 
        y reclasifica los productos, guardando el historial.
        """
        # 1. Consulta SQL para obtener los ingresos por producto de forma masiva y rápida
        query = """
            SELECT 
                sm.product_id, 
                SUM(sm.product_uom_qty * pt.list_price) as total_revenue
            FROM stock_move sm
            JOIN product_product pp ON sm.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sm.state = 'done' 
              AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'customer')
              AND sm.date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY sm.product_id
            ORDER BY total_revenue DESC
        """
        self.env.cr.execute(query, (days_back,))
        results = self.env.cr.dictfetchall()

        # 2. Calcular el Total Global para sacar porcentajes
        total_global_revenue = sum(row['total_revenue'] for row in results)
        
        if total_global_revenue == 0:
            return # No hay ventas en el periodo, no hacemos nada

        cumulative_revenue = 0.0
        history_vals_list = []
        
        # 3. Iterar sobre los resultados ordenados y asignar clasificación
        for row in results:
            product_id = row['product_id']
            revenue = row['total_revenue']
            
            cumulative_revenue += revenue
            cumulative_percentage = (cumulative_revenue / total_global_revenue) * 100

            # Lógica Pareto
            if cumulative_percentage <= 80.0:
                new_class = 'a'
            elif cumulative_percentage <= 95.0:
                new_class = 'b'
            else:
                new_class = 'c'

            # 4. Actualizar el producto y preparar el historial
            product = self.browse(product_id)
            # Como la clasificación suele estar en el template, apuntamos al product_tmpl_id
            template = product.product_tmpl_id
            old_class = template.rotation_classification or 'none'

            if old_class != new_class:
                template.write({'rotation_classification': new_class})
                
                history_vals_list.append({
                    'product_id': product.id,
                    'old_classification': old_class,
                    'new_classification': new_class,
                    'revenue_in_period': revenue,
                })

        # 5. Los productos que NO tuvieron ventas en este periodo (no salieron en el SQL)
        # deben degradarse a Clase C.
        sold_product_ids = [row['product_id'] for row in results]
        unsold_products = self.search([
            ('type', '=', 'product'), 
            ('id', 'not in', sold_product_ids),
            ('product_tmpl_id.rotation_classification', 'in', ['a', 'b'])
        ])
        
        for unsold in unsold_products:
            old_class = unsold.product_tmpl_id.rotation_classification
            unsold.product_tmpl_id.write({'rotation_classification': 'c'})
            history_vals_list.append({
                'product_id': unsold.id,
                'old_classification': old_class,
                'new_classification': 'c',
                'revenue_in_period': 0.0,
            })

        # 6. Insertar todo el historial en bloque (Bulk Create)
        if history_vals_list:
            self.env['product.rotation.history'].create(history_vals_list)

    @api.model
    def _cron_log_daily_stockouts(self):
        """
        Calcula y registra los productos sin stock al final del día.
        Usa Raw SQL para saltarse el ORM y evitar problemas de rendimiento.
        """
        query = """
            INSERT INTO product_stock_daily_log 
                (product_id, date, is_out_of_stock, create_uid, create_date, write_uid, write_date)
            SELECT 
                pp.id, 
                CURRENT_DATE, 
                TRUE, 
                %s, (NOW() at time zone 'UTC'), %s, (NOW() at time zone 'UTC')
            FROM product_product pp
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN (
                -- Subconsulta para obtener el stock libre en ubicaciones internas
                SELECT 
                    sq.product_id, 
                    SUM(sq.quantity - sq.reserved_quantity) AS free_qty
                FROM stock_quant sq
                JOIN stock_location sl ON sq.location_id = sl.id
                WHERE sl.usage = 'internal'
                GROUP BY sq.product_id
            ) AS stock ON stock.product_id = pp.id
            WHERE 
                pt.type = 'product' 
                AND pt.active = TRUE
                AND COALESCE(stock.free_qty, 0) <= 0
            ON CONFLICT DO NOTHING; -- Evita duplicados si el cron corre dos veces el mismo día
        """
        # Ejecutamos la consulta pasando el ID del usuario sistema (generalmente 1)
        self.env.cr.execute(query, (self.env.uid, self.env.uid))


    @api.model
    def _cron_calculate_demand_forecast(self, days_back=30):
        """
        Calcula la demanda real y proyecta la futura usando Suavizado Exponencial.
        """
        today = fields.Date.today()
        start_date = today - relativedelta(days=days_back)
        
        # 1. Obtener los productos que vamos a analizar (almacenables y activos)
        products = self.search([('type', '=', 'product')])
        
        for product in products:
            # Si es estacional, la lógica debería buscar el mismo periodo del año pasado.
            # Aquí implementamos el flujo estándar.
            if product.is_seasonal:
                continue # Lógica estacional a desarrollar aparte
            
            # 2. Buscar ventas reales (salidas de almacén a clientes)
            domain_moves = [
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('location_dest_id.usage', '=', 'customer'),
                ('date', '>=', start_date),
                ('date', '<=', today)
            ]
            moves = self.env['stock.move'].search(domain_moves)
            total_sold = sum(moves.mapped('product_uom_qty'))
            
            # 3. Consultar nuestra tabla ultra-rápida de quiebres de stock
            stockout_days = self.env['product.stock.daily.log'].search_count([
                ('product_id', '=', product.id),
                ('date', '>=', start_date),
                ('date', '<=', today)
            ])
            
            # 4. Calcular Demanda Real (Dt)
            effective_days = days_back - stockout_days
            
            # Evitar división por cero si estuvo agotado todo el periodo
            if effective_days <= 0:
                real_daily_demand = 0.0
            else:
                real_daily_demand = total_sold / effective_days
                
            # 5. Aplicar Suavizado Exponencial (Ft+1)
            alpha = product.smoothing_alpha
            last_forecast = product.current_forecasted_demand # El actual pasa a ser el anterior
            
            # Si es la primera vez que se calcula, Ft es igual a Dt
            if last_forecast == 0.0:
                new_forecast = real_daily_demand
            else:
                new_forecast = (alpha * real_daily_demand) + ((1 - alpha) * last_forecast)
            
            # 6. Actualizar el producto
            product.write({
                'last_forecasted_demand': last_forecast,
                'current_forecasted_demand': new_forecast
            })