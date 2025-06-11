{
    'name': 'Diferent TPV',
    'version': '18.0.1.0.0',
    'summary': 'Restaurant POS system with room and table management',
    'description': """
        Complete POS system for restaurants that includes:
        - Room and table management
        - Orders per table
        - Real-time stock control
        - Visual interface for the venue
    """,
    'author': 'Caín Martínez',
    'website': 'https://cain-dev.es',
    'license': 'AGPL-3',
    'category': 'Point of Sale',
    'depends': ['base', 'product', 'stock', 'sale', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/diferent_data.xml',
        'views/diferent_room_views.xml',
        'views/diferent_table_views.xml',
        'views/diferent_order_views.xml',
        'views/diferent_room_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}