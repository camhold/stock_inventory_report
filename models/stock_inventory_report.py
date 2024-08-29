from odoo import models, fields, api

class StockInventoryReport(models.Model):
    _name = 'stock.inventory.report'
    _description = 'Reporte de Inventario a Fecha Pasada'

    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    location_id = fields.Many2one('stock.location', string='Ubicación', readonly=True)
    quantity = fields.Float(string='Cantidad', readonly=True)
    date = fields.Date(string='Fecha', readonly=True)

    @api.model
    def generate_report(self, date):
        self.env['stock.inventory.report'].search([]).unlink()  # Limpia reportes previos
        stock_moves = self.env['stock.move'].search([('date', '<=', date), ('state', '=', 'done')])
        inventory_data = {}
        for move in stock_moves:
            key = (move.product_id.id, move.location_id.id)
            if key not in inventory_data:
                inventory_data[key] = 0
            inventory_data[key] += move.product_qty if move.location_dest_id.id == move.location_id.id else -move.product_qty
        
        report_lines = []
        for (product_id, location_id), quantity in inventory_data.items():
            report_lines.append({
                'product_id': product_id,
                'location_id': location_id,
                'quantity': quantity,
                'date': date,
            })
        self.create(report_lines)
