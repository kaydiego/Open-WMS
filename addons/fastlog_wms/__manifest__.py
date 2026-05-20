{
    "name": "Fastlog WMS",
    "version": "17.0.0.1.0",
    "summary": "Fastlog-spezifische Erweiterungen des Odoo-Lagerverwaltungsmoduls",
    "author": "Fastlog AG",
    "website": "https://www.fastlog.ch",
    "category": "Inventory/Inventory",
    "license": "OEEL-1",
    "depends": [
        "stock",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_warehouse_views.xml",
        "views/fastlog_wms_config_views.xml",
        "views/fastlog_wms_menus.xml",
    ],
    "application": True,
    "installable": True,
}
