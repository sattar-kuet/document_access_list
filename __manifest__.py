
{
    'name': 'document_access_list',
    'version': '1.0',
    'summary': 'Document Access List',
    'sequence': 10,
    'description': """Document Module """,
    'depends': ['base',
        'documents',],
    'data': [
        'views/user_with_document_access_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
        ],
       
        'web.assets_frontend': [
        ],
        
    },
    'installable': True,
}
