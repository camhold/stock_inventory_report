{
    'name': 'Reporte de Inventario a Fecha Pasada',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Permite consultar el inventario a una fecha pasada',
    'description': "Módulo para consultar el inventario a una fecha específica, con vista de lista, wizard para seleccionar la fecha y exportación a Excel.",
    'author': 'I+D, Diego Gajardo, Camilo Neira, Diego Morales',
    'website': 'https://www.holdconet.com',
    'depends': ['stock', 'web'],
    'data': [
        'security/ir.model.access.csv',
       # 'views/assets.xml',
        'views/stock_inventory_report_views.xml',
        'views/stock_inventory_report_wizard_views.xml',
        'views/stock_menu.xml',
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         '/stock_inventory_report/static/src/js/inventory_dashboard_widget.js',
    #         '/stock_inventory_report/static/src/xml/inventory_dashboard_templates.xml',
    #         '/stock_inventory_report/static/src/css/inventory_dashboard.css',
    #     ],
    # },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}