{
    'name': 'Reporte de Inventario a Fecha Pasada',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Permite consultar el inventario a una fecha pasada',
    'description': "Módulo para consultar el inventario a una fecha específica, con vista de lista, wizard para seleccionar la fecha y exportación a Excel.",
    'author': 'I+D, Diego Gajardo, Camilo Neira, Diego Morales',
    'website': 'https://www.holdconet.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_inventory_report_views.xml',
        'views/stock_inventory_report_wizard_views.xml',
        'views/stock_menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}