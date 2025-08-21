"""
Centralized navigation component for all pages
This ensures consistency across all layouts and easier maintenance
"""

from dash import dcc
import dash_bootstrap_components as dbc

def create_navigation(active_page=None):
    """
    Create consistent navigation for all pages
    
    Args:
        active_page (str): The currently active page identifier
        Options: 'accueil', 'prospection', 'socio_demo', 'equip_financ', 
                'log_patrimoine', 'assurance', 'depense', 'medical_professionals',
                'experts_comptables', 'pharmacies', 'conseillers'
    
    Returns:
        dbc.Nav: Complete navigation component
    """
    
    # All available navigation links with their configurations
    nav_links = [
        {
            'label': 'Accueil',
            'page_id': 'accueil',
            'href': '/'
        },
        {
            'label': 'Base de Prospection',
            'page_id': 'prospection', 
            'href': '/prospection'
        },
        {
            'label': 'Socio-Démographie',
            'page_id': 'socio_demo',
            'href': '/socio_démographie'
        },
        {
            'label': 'Equipements Financiers',
            'page_id': 'equip_financ',
            'href': '/equip_financ'
        },
        {
            'label': 'Logement et Patrimoine',
            'page_id': 'log_patrimoine',
            'href': '/log_patrimoine'
        },
        {
            'label': 'Assurance',
            'page_id': 'assurance',
            'href': '/assurance'
        },
        {
            'label': 'Dépenses',
            'page_id': 'depense',
            'href': '/depense'
        },
        {
            'label': 'Professionnels Médicaux',
            'page_id': 'medical_professionals',
            'href': '/medical_professionals'
        },
        {
            'label': 'Experts Comptables',
            'page_id': 'experts_comptables',
            'href': '/experts_comptables'
        },
        {
            'label': 'Pharmacies',
            'page_id': 'pharmacies',
            'href': '/pharmacies'
        },
        {
            'label': 'Conseillers',
            'page_id': 'conseillers',
            'href': '/conseillers'
        }
    ]
    
    # Create navigation links
    navigation_components = []
    for link in nav_links:
        is_active = (active_page == link['page_id'])
        nav_component = dcc.Link(
            dbc.NavLink(link['label'], active=is_active),
            href=link['href'],
            refresh=True
        )
        navigation_components.append(nav_component)
    
    # Return complete navigation
    return dbc.Nav(
        navigation_components,
        vertical=True,
        pills=True,
        style={"margin-top": "6rem"}
    )

def create_page_header():
    """
    Create consistent page header with logo and title
    
    Returns:
        dbc.Row: Header component with logo and title
    """
    return dbc.Row([
        dbc.Col(                        
            dcc.Link(
                dbc.NavLink(
                    "assets\\biat.jpg",
                    className="logo",
                ),
                href="https://www.biat.com.tn/"
            ),
            width=3
        ),
        dbc.Col(
            dbc.NavLink("BIAT - OUTIL DE GEOMARKETING", style={"padding-top": "8px"}),
            width=9
        )
    ])