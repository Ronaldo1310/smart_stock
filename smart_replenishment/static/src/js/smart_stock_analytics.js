/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { getDefaultConfig } from "@web/views/view";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;

class SmartStockAnalytics extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            kpis: { total_products: 0, total_valuation: 0, pending_po_value: 0, class_a_count: 0 },
            abc_donut: [],
            revenue_trend: { labels: [], data: [] },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.chartDonut = useRef('chart_donut');
        this.chartTrend = useRef('chart_trend');

        onWillStart(async () => {
            let data = await this.orm.call('smart.replenishment.dashboard', 'get_secondary_dashboard_data', []);
            if (data) {
                this.state.kpis = data.kpis;
                this.state.abc_donut = data.abc_donut;
                this.state.revenue_trend = data.revenue_trend;
            }
        });

        onMounted(() => {
            this.renderDonutGraph();
            this.renderTrendGraph();
        });
    }

    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    renderDonutGraph() {
        const options = {
            series: this.state.abc_donut,
            chart: { type: 'donut', height: 350 },
            labels: ['Class A', 'Class B', 'Class C'],
            colors: ['#4CAF50', '#FF9800', '#9E9E9E'],
            dataLabels: { enabled: true },
            title: { text: 'ABC Classification Spread', align: 'left' },
            legend: { position: 'bottom' }
        };
        this.renderGraph(this.chartDonut.el, options);
    }

    renderTrendGraph() {
        const options = {
            series: [{ name: 'Revenue', data: this.state.revenue_trend.data }],
            chart: { type: 'area', height: 350, toolbar: { show: false } },
            stroke: { curve: 'smooth', width: 3 },
            fill: {
                type: 'gradient',
                gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.2, stops: [0, 90, 100] }
            },
            colors: ['#00A09D'],
            dataLabels: { enabled: false },
            xaxis: { categories: this.state.revenue_trend.labels },
            yaxis: { labels: { formatter: (value) => { return "$" + value.toLocaleString() } } },
            title: { text: 'Revenue Trend (Last 6 Months)', align: 'left' }
        };
        this.renderGraph(this.chartTrend.el, options);
    }
}

SmartStockAnalytics.template = "smart_stock.AnalyticsTemplate";
registry.category("actions").add("smart_stock_analytics_dashboard", SmartStockAnalytics);