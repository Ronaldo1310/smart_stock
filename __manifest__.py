{
    'name': 'Smart Stock Replenishment',
    'version': '1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Data-driven inventory replenishment, demand forecasting, and automated purchasing.',
    'description': """
Smart Stock Replenishment
=========================
This module transforms standard Odoo replenishment into a dynamic, data-driven system.

Key Features:
- **True Demand Calculation:** Tracks effective days out of stock to calculate real daily demand instead of simple averages.
- **Demand Forecasting:** Utilizes Simple Exponential Smoothing to predict future demand based on recent sales trends.
- **Dynamic ABC Classification:** Automatically classifies products into A, B, or C categories based on the Pareto principle (80/15/5 revenue split).
- **Smart Purchasing:** Automatically generates Draft Purchase Orders or Call for Bids (Tenders) factoring in forecasted demand, Lead Times, Safety Stock, and MOQs.
- **High-Performance Dashboard:** Includes a SQL-backed dynamic dashboard to analyze revenue, product rotation, and performance without slowing down the ORM.
    """,
    'author': 'Freddy Torres - Lixie Studio Digital, C.A.',
    'website': 'https://lixie.io',
    'depends': [
        'base', 
        'stock', 
        'purchase', 
        'purchase_requisition'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'views/product_views.xml',
        'views/smart_replenishment_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}