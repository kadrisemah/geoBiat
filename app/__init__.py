from flask import Flask 
from flask.helpers import get_root_path
from config import BaseConfig 
import dash_bootstrap_components as dbc
import dash
# from flask_login import login_required

def create_app():
    server = Flask(__name__,instance_relative_config=False)
    server.config.from_object(BaseConfig)
    
    with server.app_context():
        register_dashapp(server)
        return server


def register_dashapp(app):

    from app.accueil.layout import accueil_page
    from app.accueil.callbacks import register_callbacks_accueil

    from app.base_prospection.layout import prospection_page
    from app.base_prospection.callbacks import register_callbacks_prospections

    from app.socio_demo.layout import socio_demo_page
    from app.socio_demo.callbacks import register_callbacks_socio_demo

    from app.equipement_financiers.layout import equip_financ_page 
    from app.equipement_financiers.callbacks import register_callbacks_equipe_financ

    from app.logement_patrimoine.layout import logement_patrimoine_page  
    from app.logement_patrimoine.callbacks import register_callbacks_logement_patrimoine

    from app.assurance.layout import assurance_page
    from app.assurance.callbacks import register_callbacks_assurance

    from app.depenses.layout import depense_page
    from app.depenses.callbacks import register_callbacks_depenses


    # Meta tags for viewport responsivebess

    meta_viewport = {
        "name" : "viewport",
        "content" : "width=device-width"
    }

    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

    accueil = dash.Dash(__name__,
                        server=app,
                        url_base_pathname='/',
                        assets_folder=get_root_path(__name__)+ '/assets/',
                        meta_tags=[meta_viewport],
                        external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
                        # external_stylesheets=[dbc.themes.SANDSTONE])
    with app.app_context():

        accueil.title = 'BIAT Geomarketing Dashboard - Accueil'
        accueil.layout = accueil_page
        accueil._favicon = 'biat.jpg'
        register_callbacks_accueil(accueil)

    base_prospection = dash.Dash(__name__,
                        server=app,
                        url_base_pathname='/prospection/',
                        assets_folder=get_root_path(__name__)+ '/assets/',
                        meta_tags=[meta_viewport],
                        external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
    with app.app_context():

        base_prospection.title = 'Base de prospection'
        base_prospection.layout = prospection_page
        base_prospection._favicon = 'biat.jpg'
        register_callbacks_prospections(base_prospection)

    socio_demo = dash.Dash(__name__,
                        server=app,
                        url_base_pathname='/socio_démographie/',
                        assets_folder=get_root_path(__name__)+ '/assets/',
                        meta_tags=[meta_viewport],
                        external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
                       
    with app.app_context():

        socio_demo.title = 'Socio-Démographie'
        socio_demo.layout = socio_demo_page
        socio_demo._favicon = 'biat.jpg'
        register_callbacks_socio_demo(socio_demo)

    equip_financ = dash.Dash(__name__,
                    server=app,
                    url_base_pathname='/equip_financ/',
                    assets_folder=get_root_path(__name__)+ '/assets/',
                    meta_tags=[meta_viewport],
                    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
                       
    with app.app_context():

        equip_financ.title = 'Equipement Financiers'
        equip_financ.layout = equip_financ_page
        equip_financ._favicon = 'biat.jpg'
        register_callbacks_equipe_financ(equip_financ)

    log_patrimoine = dash.Dash(__name__,
                    server=app,
                    url_base_pathname='/log_patrimoine/',
                    assets_folder=get_root_path(__name__)+ '/assets/',
                    meta_tags=[meta_viewport],
                    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
                       
    with app.app_context():

        log_patrimoine.title = 'Logement et Patrimoine'
        log_patrimoine.layout = logement_patrimoine_page
        log_patrimoine._favicon = 'biat.jpg'
        register_callbacks_logement_patrimoine(log_patrimoine)

    assurance = dash.Dash(__name__,
                    server=app,
                    url_base_pathname='/assurance/',
                    assets_folder=get_root_path(__name__)+ '/assets/',
                    meta_tags=[meta_viewport],
                    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
                       
    with app.app_context():

        assurance.title = 'Assurance'
        assurance.layout = assurance_page
        assurance._favicon = 'biat.jpg'
        register_callbacks_assurance(assurance)

    depense = dash.Dash(__name__,
                    server=app,
                    url_base_pathname='/depense/',
                    assets_folder=get_root_path(__name__)+ '/assets/',
                    meta_tags=[meta_viewport],
                    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])
                       
    with app.app_context():

        depense.title = 'Dépenses'
        depense.layout = depense_page
        depense._favicon = 'biat.jpg'
        register_callbacks_depenses(depense)


    # __protect_dashviews(dashapp)
        

# def __protect_dashviews(dashapp) :
#     for view_func in dashapp.server.view_functions:
#         if view_func.startwith(dashapp.config.url_base_pathname):
#             dashapp.server.view_functions[view_func] = login_required(
#                 dashapp.server.view_functions[view_func]
#             )