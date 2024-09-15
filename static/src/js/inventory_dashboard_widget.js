/** @odoo-module **/

import { Component } from "@odoo/owl";

export class InventoryDashboard extends Component {
    static template = "inventory.InventoryDashboard";

    state = {
        totalProducts: 0,
        totalQuantity: 0,
        totalValue: 0,
        overdueProducts: 0,
    };

    async willStart() {
        const result = await this.env.services.rpc({
            model: 'stock.inventory.report',
            method: 'get_inventory_summary',
        });

        this.state.totalProducts = result.total_products;
        this.state.totalQuantity = result.total_quantity;
        this.state.totalValue = result.total_value;
        this.state.overdueProducts = result.overdue_products;
    }
}

