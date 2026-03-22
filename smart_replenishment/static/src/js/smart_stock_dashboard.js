/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { getDefaultConfig } from "@web/views/view";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;

class SmartStockDashboard extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            counts: { class_a: 0, class_b: 0, class_c: 0, replenish_count: 0, replenish_ids: [] },
            top_rotation: { labels: [], data: [] },
            top_revenue: { labels: [], data: [] },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.chartRotation = useRef('chart_rotation');
        this.chartRevenue = useRef('chart_revenue');

        onWillStart(async () => {
            let dashboardData = await this.orm.call('smart.replenishment.dashboard', 'get_dashboard_data', []);
            if (dashboardData) {
                this.state.counts = dashboardData.counts;
                this.state.top_rotation = dashboardData.top_rotation;
                this.state.top_revenue = dashboardData.top_revenue;
            }
        });

        onMounted(() => {
            this.renderRotationGraph();
            this.renderRevenueGraph();
        });
    }

    // --- ACCIONES DE LOS BOTONES ---
    viewClass(classification) {
        let domain = [['rotation_classification', '=', classification]];
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: `Products Class ${classification.toUpperCase()}`,
            res_model: 'product.template',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            domain: domain,
        });
    }

    viewNeedsReplenishment() {
        // Vista Tree especializada para reposición
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Requires Replenishment',
            res_model: 'product.product',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            domain: [['id', 'in', this.state.counts.replenish_ids]],
            context: {
                // Forzamos a mostrar los campos relevantes por defecto
                tree_view_ref: 'smart_stock.view_product_replenish_tree'
            }
        });
    }

    // --- GRÁFICOS APEXCHARTS ---
    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    renderRotationGraph() {
        const options = {
            series: [{ name: 'Qty Sold', data: this.state.top_rotation.data }],
            chart: { height: 350, type: 'area', toolbar: { show: false } },
            colors: ['#00A09D'],
            dataLabels: { enabled: false },
            xaxis: { categories: this.state.top_rotation.labels },
            title: { text: 'Top 10 Rotation (This Month)', align: 'left' }
        };
        this.renderGraph(this.chartRotation.el, options);
    }

    renderRevenueGraph() {
        const options = {
            series: [{ name: 'Revenue', data: this.state.top_revenue.data }],
            chart: { height: 350, type: 'bar', toolbar: { show: false } },
            plotOptions: { bar: { borderRadius: 4, horizontal: true } },
            colors: ['#FF9800'],
            dataLabels: { enabled: true, formatter: function (val) { return "$" + val } },
            xaxis: { categories: this.state.top_revenue.labels },
            title: { text: 'Top 10 Revenue (This Month)', align: 'left' }
        };
        this.renderGraph(this.chartRevenue.el, options);
    }
}

SmartStockDashboard.template = "smart_stock.DashboardTemplate";
registry.category("actions").add("smart_stock_main_dashboard", SmartStockDashboard);