from odoo import models, fields, api

class StockInventoryReport(models.Model):
    _name = 'stock.inventory.report'
    _description = 'Línea del Informe de Inventario Histórico'

    product_id = fields.Many2one('product.product', string='Producto')
    location_src_id = fields.Many2one('stock.location', string='Ubicación Origen')
    location_dest_id = fields.Many2one('stock.location', string='Ubicación Destino')
    lot_name = fields.Char(string='Lotes/Series')  # Definido como Char para recibir los lotes concatenados
    last_move_date = fields.Datetime(string='Fecha Último Movimiento')
    move_type = fields.Selection([('Compra', 'Compra'), ('Transferencia Interna', 'Transferencia Interna')], string='Tipo de Movimiento')
    quantity = fields.Float(string='Cantidad')
    unit_value = fields.Float(string='Valor Unitario')
    total_value = fields.Float(string='Valorizado', compute='_compute_total_value')

    @api.depends('quantity', 'unit_value')
    def _compute_total_value(self):
        for line in self:
            line.total_value = line.quantity * line.unit_value

    @api.model
    def generate_report(self, date):
        self.env['stock.inventory.report'].search([]).unlink()  # Limpia reportes previos
        
        # Buscar movimientos de stock hasta la fecha seleccionada
        stock_moves = self.env['stock.move'].search([
            ('date', '<=', date),
            ('state', '=', 'done'),
            '|',
            ('location_id', 'in', self.env['stock.location'].search([('usage', 'in', ['internal', 'transit'])]).ids),
            ('location_dest_id', 'in', self.env['stock.location'].search([('usage', 'in', ['internal', 'transit'])]).ids)
        ])

        report_lines = []
        for move in stock_moves:
            # Obtener todos los nombres de lotes asociados al movimiento y concatenarlos
            lot_names = ', '.join(move.move_line_ids.mapped('lot_id.name')) if move.move_line_ids else 'N/A'
            
            # Determinar el tipo de movimiento
            move_type = 'Compra' if move.picking_type_id.code == 'incoming' else 'Transferencia Interna'
            
            report_lines.append({
                'product_id': move.product_id.id,
                'location_src_id': move.location_id.id,  # Ubicación de origen
                'location_dest_id': move.location_dest_id.id,  # Ubicación de destino
                'lot_name': lot_names,
                'last_move_date': move.date,
                'move_type': move_type,
                'quantity': move.product_qty,
                'unit_value': move.product_id.standard_price,
                'total_value': move.product_qty * move.product_id.standard_price,
            })

        self.create(report_lines)

    def get_inventory_summary(self):
        total_products = len(self.search([]))
        total_quantity = sum(self.search([]).mapped('quantity'))
        total_value = sum(self.search([]).mapped(lambda r: r.quantity * r.product_id.standard_price))
        overdue_products = len(self.search([('last_move_date', '<', fields.Datetime.now())]))

        return {
            'total_products': total_products,
            'total_quantity': total_quantity,
            'total_value': total_value,
            'overdue_products': overdue_products,
        }
