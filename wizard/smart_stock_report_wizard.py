import base64
import io
import xlsxwriter
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError

class SmartStockReportWizard(models.TransientModel):
    _name = 'smart.stock.report.wizard'
    _description = 'Smart Stock Excel Report Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    
    # Nuevos Filtros (Opcionales)
    category_id = fields.Many2one('product.category', string='Product Category')
    product_id = fields.Many2one('product.product', string='Product')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)])

    excel_file = fields.Binary(string='Excel File', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True)

    def action_generate_excel(self):
        # 1. ORM: Filtrar productos basados en la selección del usuario
        domain = [('type', '=', 'product')]
        if self.product_id:
            domain.append(('id', '=', self.product_id.id))
        if self.category_id:
            # Usamos 'child_of' para incluir las subcategorías automáticamente
            domain.append(('categ_id', 'child_of', self.category_id.id))
        if self.vendor_id:
            domain.append(('seller_ids.partner_id', '=', self.vendor_id.id))
            
        products = self.env['product.product'].search(domain)
        
        if not products:
            raise UserError("No products found matching the selected filters.")
            
        product_ids = tuple(products.ids)

        # 2. Identificar los meses dentro del rango
        months_list = []
        current_date = self.date_from.replace(day=1)
        while current_date <= self.date_to:
            months_list.append(current_date.strftime('%Y-%m'))
            current_date += relativedelta(months=1)

        # 3. Consulta SQL Dinámica (Pasamos la tupla de IDs al IN)
        query = """
            SELECT 
                sm.product_id,
                to_char(sm.date, 'YYYY-MM') as month_year,
                SUM(sm.product_uom_qty) as total_qty
            FROM stock_move sm
            WHERE sm.state = 'done' 
              AND sm.location_dest_id IN (SELECT id FROM stock_location WHERE usage = 'customer')
              AND sm.date >= %s AND sm.date <= %s
              AND sm.product_id IN %s
            GROUP BY sm.product_id, month_year
            ORDER BY sm.product_id
        """
        self.env.cr.execute(query, (self.date_from, self.date_to, product_ids))
        results = self.env.cr.dictfetchall()

        data_by_product = {}
        for row in results:
            p_id = row['product_id']
            if p_id not in data_by_product:
                data_by_product[p_id] = {}
            data_by_product[p_id][row['month_year']] = row['total_qty']

        # 4. Preparar archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Rotation Report')

        # Formatos de Celdas
        header_format = workbook.add_format({'bold': True, 'bg_color': '#00A09D', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1})
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        number_format = workbook.add_format({'border': 1})
        product_format = workbook.add_format({'border': 1})

        # Escribir Cabeceras (Inglés)
        sheet.merge_range(0, 0, 1, 0, 'Product', header_format)
        sheet.set_column(0, 0, 45) # Hacemos la columna del producto más ancha

        col = 1
        for month in months_list:
            sheet.merge_range(0, col, 0, col+2, month, header_format)
            sheet.write(1, col, 'Qty Sold', header_format)
            sheet.write(1, col+1, 'Revenue Generated', header_format)
            sheet.write(1, col+2, 'Replacement Cost', header_format)
            col += 3
        
        # Cabeceras de Totales (Inglés)
        sheet.merge_range(0, col, 0, col+2, 'PERIOD TOTALS', header_format)
        sheet.write(1, col, 'Total Qty', header_format)
        sheet.write(1, col+1, 'Total Revenue', header_format)
        sheet.write(1, col+2, 'Total Cost', header_format)

        # 5. Llenar la Data
        row_idx = 2
        
        # Iteramos sobre TODOS los productos filtrados, incluso si en ese mes vendieron 0.
        for product in products:
            months_data = data_by_product.get(product.id, {})
            
            # Si el producto no tuvo ventas en todo el periodo, lo saltamos para no ensuciar el Excel de filas en blanco
            if not months_data:
                continue
                
            list_price = product.list_price
            cost_price = product.last_purchase_cost if product.last_purchase_cost > 0 else product.standard_price

            sheet.write(row_idx, 0, product.display_name, product_format)
            
            total_qty_period = 0
            total_rev_period = 0
            total_cost_period = 0
            col_idx = 1

            for month in months_list:
                qty = months_data.get(month, 0.0)
                revenue = qty * list_price
                cost = qty * cost_price

                sheet.write(row_idx, col_idx, qty, number_format)
                sheet.write(row_idx, col_idx+1, revenue, money_format)
                sheet.write(row_idx, col_idx+2, cost, money_format)
                
                total_qty_period += qty
                total_rev_period += revenue
                total_cost_period += cost
                col_idx += 3

            # Escribir Columnas Finales de Totales
            sheet.write(row_idx, col_idx, total_qty_period, number_format)
            sheet.write(row_idx, col_idx+1, total_rev_period, money_format)
            sheet.write(row_idx, col_idx+2, total_cost_period, money_format)
            row_idx += 1

        workbook.close()
        
        # 6. Guardar en Base64 para descargar
        excel_data = base64.b64encode(output.getvalue())
        self.write({
            'excel_file': excel_data,
            'file_name': f'Smart_Stock_Report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'smart.stock.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }