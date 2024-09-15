from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
import io
import xlsxwriter

class StockInventoryReportWizard(models.TransientModel):
    _name = 'stock.inventory.report.wizard'
    _description = 'Wizard para consultar inventario a una fecha pasada'

    date = fields.Date(string='Fecha de consulta', required=True, default=fields.Date.context_today)

    def action_view_inventory_report(self):
        self.ensure_one()

        # Borrar registros anteriores
        self.env['stock.inventory.report'].sudo().search([]).unlink()

        # Filtrar las ubicaciones de tipo "Interna" y "Tránsito"
        location_types = ['internal', 'transit']
        valid_locations = self.env['stock.location'].search([('usage', 'in', location_types)])

        # Obtener los movimientos de stock hasta la fecha seleccionada y que involucren las ubicaciones deseadas
        stock_moves = self.env['stock.move'].search([
            ('date', '<=', self.date),
            ('state', '=', 'done'),
            '|', 
            ('location_id', 'in', valid_locations.ids),
            ('location_dest_id', 'in', valid_locations.ids)
        ])

        # Procesar datos del inventario
        report_lines = []
        for move in stock_moves:
            product = move.product_id
            location_src = move.location_id
            location_dest = move.location_dest_id
            quantity = move.quantity
            unit_cost = product.standard_price if product else 0.0
            total_value = quantity * unit_cost

            # Obtener todos los nombres de lotes asociados al movimiento y concatenarlos
            lot_names = ', '.join(move.move_line_ids.mapped('lot_id.name')) if move.move_line_ids else 'N/A'

            report_lines.append({
                'product_id': product.id if product else False,
                'location_src_id': location_src.id if location_src else False,  # Ubicación de origen
                'location_dest_id': location_dest.id if location_dest else False,  # Ubicación de destino
                'lot_name': lot_names,
                'last_move_date': move.date,
                'move_type': 'Compra' if move.picking_type_id.code == 'incoming' else 'Transferencia Interna',
                'quantity': quantity,
                'unit_value': unit_cost,
                'total_value': total_value,
            })

        # Crear registros del reporte
        self.env['stock.inventory.report'].sudo().create(report_lines)

        # Mostrar la vista del reporte
        return {
            'type': 'ir.actions.act_window',
            'name': 'Informe de Inventario Histórico',
            'res_model': 'stock.inventory.report',
            'view_mode': 'tree',
            'target': 'current',
        }

    def action_export_inventory_report(self):
        self.ensure_one()

        # Borrar registros anteriores
        self.env['stock.inventory.report'].sudo().search([]).unlink()

        # Filtrar las ubicaciones de tipo "Interna" y "Tránsito"
        location_types = ['internal', 'transit']
        valid_locations = self.env['stock.location'].search([('usage', 'in', location_types)])

        # Obtener los movimientos de stock hasta la fecha seleccionada y que involucren las ubicaciones deseadas
        stock_moves = self.env['stock.move'].search([
            ('date', '<=', self.date),
            ('state', '=', 'done'),
            '|', 
            ('location_id', 'in', valid_locations.ids),
            ('location_dest_id', 'in', valid_locations.ids)
        ])

        # Preparar los datos para el reporte
        inventory_data = []
        for move in stock_moves:
            lot_names = ', '.join(move.move_line_ids.mapped('lot_id.name')) if move.move_line_ids else 'N/A'
            move_type = 'Compra' if move.picking_type_id.code == 'incoming' else 'Transferencia Interna'
            unit_value = move.product_id.standard_price
            total_value = move.product_qty * unit_value

            inventory_data.append({
                'product_name': move.product_id.display_name,
                'location_src_name': move.location_id.display_name,  # Ubicación de origen
                'location_dest_name': move.location_dest_id.display_name,  # Ubicación de destino
                'lot_name': lot_names,
                'last_move_date': move.date,
                'move_type': move_type,
                'product_qty': move.product_qty,
                'unit_value': unit_value,
                'total_value': total_value,
            })

        # Crear archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet('Inventario')
        headers = ['Producto', 'Ubicación Origen', 'Ubicación Destino', 'Lote/Serie', 'Fecha Último Movimiento', 'Tipo Movimiento',
                   'Cantidad', 'Valor Unitario', 'Valorizado']

        # Escribir encabezados
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        # Escribir datos en Excel
        row = 1
        for data in inventory_data:
            sheet.write(row, 0, data['product_name'])
            sheet.write(row, 1, data['location_src_name'])  # Ubicación de origen
            sheet.write(row, 2, data['location_dest_name'])  # Ubicación de destino
            sheet.write(row, 3, data['lot_name'])
            sheet.write(row, 4, str(data['last_move_date']))
            sheet.write(row, 5, data['move_type'])
            sheet.write(row, 6, data['product_qty'])
            sheet.write(row, 7, data['unit_value'])
            sheet.write(row, 8, data['total_value'])
            row += 1

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Crear y devolver el archivo adjunto para su descarga
        attachment = self.env['ir.attachment'].sudo().create({
            'name': f'Reporte_Inventario_{self.date}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'store_fname': f'Reporte_Inventario_{self.date}.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # Devolver acción para descargar el archivo
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
