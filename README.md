# Smart Stock Replenishment for Odoo

🌍 *[Leer versión en Español](#versión-en-español)*

Transform your standard Odoo inventory into a dynamic, data-driven supply chain engine. This module calculates real demand, forecasts future needs, dynamically classifies your products, and automates your purchasing process.

## 🌟 Core Features

* **True Demand Tracking:** Automatically logs "out of stock" days to calculate real daily demand, ensuring stockouts don't artificially lower your sales averages.
* **Exponential Smoothing Forecast:** Predicts future demand giving more weight to recent sales trends, adapting quickly to viral products or dying trends.
* **Dynamic ABC Classification:** Automatically groups products into A (80% revenue), B (15%), and C (5%) categories using the Pareto Principle via scheduled SQL-optimized tasks.
* **Automated Procurement:** Generates multiproduct Draft Purchase Orders. If a product has multiple vendors, it automatically creates a Call for Bids (Purchase Tender) to help you compare prices.
* **Smart Parameters:** Considers Vendor Lead Time, Minimum Order Quantity (MOQ), and Safety Stock days before triggering any purchase.
* **SQL-Backed Dashboard:** Monitor top performers, revenue by classification, and global rotation metrics via a high-speed, dynamic pivot and graph view.

## ⚙️ Technical Requirements
* **Odoo Version:** 16.0 / 17.0 (Adjust according to your target version)
* **Dependencies:** `stock`, `purchase`, `purchase_requisition`

## 👨‍💻 Author & Support
* **Author:** Freddy Torres
* **Company:** Lixie Studio Digital, C.A.
* **Website:** [lixie.io](https://lixie.io)

---

# Versión en Español

Transforma tu inventario estándar de Odoo en un motor de cadena de suministro dinámico y basado en datos. Este módulo calcula la demanda real, proyecta necesidades futuras, clasifica dinámicamente tus productos y automatiza tu proceso de compras.

## 🌟 Características Principales

* **Rastreo de Demanda Real:** Registra automáticamente los días "sin stock" para calcular la demanda diaria real, evitando que los quiebres de inventario bajen artificialmente tus promedios de ventas.
* **Proyección por Suavizado Exponencial:** Predice la demanda futura dándole mayor peso a las tendencias de ventas recientes, adaptándose rápidamente a productos virales o estancados.
* **Clasificación ABC Dinámica:** Agrupa automáticamente los productos en categorías A (80% de ingresos), B (15%) y C (5%) usando el Principio de Pareto mediante tareas SQL optimizadas.
* **Abastecimiento Automatizado:** Genera Órdenes de Compra en borrador multiproducto. Si un producto tiene múltiples proveedores, crea automáticamente una Licitación (Call for Bids) para comparar precios.
* **Parámetros Inteligentes:** Considera el Tiempo de Entrega del proveedor (Lead Time), la Cantidad Mínima de Pedido (MOQ) y los días de Stock de Seguridad antes de disparar una compra.
* **Dashboard basado en SQL:** Monitorea los mejores productos, los ingresos por clasificación y las métricas globales de rotación a través de una vista dinámica ultrarrápida (Pivot y Gráficos).

## ⚙️ Requisitos Técnicos
* **Versión de Odoo:** 16.0 / 17.0 (Ajustar según la versión destino)
* **Dependencias:** `stock`, `purchase`, `purchase_requisition`

## 👨‍💻 Autor y Soporte
* **Autor:** Freddy Torres
* **Empresa:** Lixie Studio Digital, C.A.
* **Sitio Web:** [lixie.io](https://lixie.io)