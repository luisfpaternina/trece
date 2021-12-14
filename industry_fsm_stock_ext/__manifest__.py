{
    'name': 'industry fsm stock extended',

    'summary': 'Validate stock moves for product added on sales orders through Field Service Management App',

    'version': '13.1',

    'author': "Nybble group",

    'contributors': ['Luis Felipe Paternina'],

    'website': "",

    'category': 'Hidden',

    'depends': [

        'industry_fsm',

    ],

    'data': [
       
        'security/ir.model.access.csv',
        #'views/product_product_views.xml',
        'wizard/fsm_stock_tracking_views.xml',
             
    ],
    'installable': True
}
