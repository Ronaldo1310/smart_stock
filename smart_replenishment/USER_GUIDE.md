# User Guide: Smart Stock Replenishment
*Por / By Freddy Torres - Lixie Studio Digital*

🌍 *[Leer versión en Español](#guía-de-usuario-versión-en-español)*

Welcome to the Smart Stock Replenishment module. This guide will help you understand how to configure and use the module to automate your supply chain.

## 1. Initial Configuration
Before the system can automate your purchases, you need to configure your products.
1. Go to **Inventory > Products > Products**.
2. Open any physical (storable) product.
3. Navigate to the new **Smart Replenishment** tab.
4. Set the **Safety Stock Days** (e.g., 7 days) to create a buffer against unexpected demand.
5. If the product only sells during specific seasons, check the **Seasonal Product** box.
6. **Crucial:** Ensure your product has at least one Vendor configured in the *Purchase* tab, including the Vendor's Delivery Lead Time and Minimum Order Quantity (MOQ).

## 2. How the Automation Works (Background Process)
You don't need to manually click any buttons for calculations. The module runs automated tasks (Cron Jobs) behind the scenes:
* **Daily (11:50 PM):** Logs if any product ran out of stock during the day.
* **Daily (01:00 AM):** Calculates real demand (ignoring out-of-stock days) and projects future demand using Exponential Smoothing.
* **Daily (02:00 AM):** Evaluates your current stock. If it falls below the Reorder Point, it creates a Draft Purchase Order. If the product has multiple vendors, it creates a Call for Bids (Purchase Tender).
* **Monthly (1st of the month):** Evaluates all sales and classifies your products into A, B, or C (Pareto Principle).

## 3. Daily Usage & Dashboard
* **Checking Auto-Generated Orders:** Go to **Purchase > Requests for Quotation**. Look for orders with the toggle **"Auto-Generated"** turned on. These were created by the module. You just need to review and confirm them.
* **Analyzing Rotation:** Go to **Purchase > Smart Stock > Rotation Dashboard**. Here you can group by "Classification" to see your Class A products, view total revenue, and identify which items have the highest daily demand projection.

---

# Guía de Usuario: Versión en Español

Bienvenido al módulo Smart Stock Replenishment. Esta guía te ayudará a configurar y utilizar el módulo para automatizar tu cadena de suministro.

## 1. Configuración Inicial
Antes de que el sistema pueda automatizar tus compras, debes configurar tus productos.
1. Ve a **Inventario > Productos > Productos**.
2. Abre cualquier producto físico (almacenable).
3. Navega a la nueva pestaña **Smart Replenishment**.
4. Define los **Días de Stock de Seguridad** (ej. 7 días) para crear un colchón contra picos de demanda.
5. Si el producto solo se vende en temporadas específicas, marca la casilla **Producto Estacional**.
6. **Crucial:** Asegúrate de que tu producto tenga al menos un Proveedor configurado en la pestaña *Compra*, incluyendo el Tiempo de Entrega (Lead Time) y la Cantidad Mínima de Pedido (MOQ).

## 2. Cómo funciona la Automatización (Procesos en Segundo Plano)
No necesitas hacer clic en ningún botón manualmente para los cálculos. El módulo ejecuta tareas programadas (Cron Jobs) en segundo plano:
* **Diario (23:50):** Registra si algún producto se quedó sin stock durante el día.
* **Diario (01:00 AM):** Calcula la demanda real (ignorando los días sin stock) y proyecta la demanda futura usando Suavizado Exponencial.
* **Diario (02:00 AM):** Evalúa tu stock actual. Si cae por debajo del Punto de Reorden, crea una Orden de Compra en borrador. Si el producto tiene múltiples proveedores, crea una Licitación (Acuerdo de Compra).
* **Mensual (Día 1):** Evalúa todas las ventas y clasifica tus productos en A, B o C (Principio de Pareto).

## 3. Uso Diario y Tablero de Control (Dashboard)
* **Revisar Órdenes Automáticas:** Ve a **Compra > Peticiones de Presupuesto**. Busca las órdenes que tengan el interruptor **"Generada Automáticamente"** activado. Estas fueron creadas por el módulo. Solo necesitas revisarlas y confirmarlas.
* **Análisis de Rotación:** Ve a **Compra > Smart Stock > Dashboard de Rotación**. Aquí puedes agrupar por "Clasificación" para ver tus productos Clase A, visualizar los ingresos totales e identificar qué artículos tienen la mayor proyección de demanda diaria.