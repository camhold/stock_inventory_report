/** @odoo-module **/

import { Component } from "@odoo/owl";

class InventoryDashboard extends Component {
    static template = "inventory.InventoryDashboard";

    // Definir las propiedades para mostrar el resumen
    state = {
        totalProducts: 0,
        totalQuantity: 0,
        totalValue: 0,
        overdueProducts: 0,
    };

    async willStart() {
        // Llamada al backend para obtener los datos del inventario
        const result = await this.env.services.rpc({
            model: 'stock.inventory.report',
            method: 'get_inventory_summary',
        });

        // Asignar los valores de la consulta al estado del componente
        this.state.totalProducts = result.total_products;
        this.state.totalQuantity = result.total_quantity;
        this.state.totalValue = result.total_value;
        this.state.overdueProducts = result.overdue_products;
    }
}

export default InventoryDashboard;
