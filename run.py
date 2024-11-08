from flask import Flask
from flask_cors import CORS
from config import Config
from routes.user_routes import user_bp
from routes.conjunto_routes import conjunto_bp
from  routes.mercado_pago_routes import mercado_pago_bp
from  routes.webhook_routes import webhook_bp
from  routes.transaccion_temporal_router import transaccion_temporal_bp
from  routes.vigilante_routes import vigilante_bp
from flask_jwt_extended import JWTManager
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración de CORS
    CORS(app, resources={r"/*": {"origins": "*"}})


    # Configuración de JWT
    jwt = JWTManager(app)

    # Inicialización de Flask-Mail
    mail.init_app(app)
    # Inicializar mercado pago

    # Registrar Blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(conjunto_bp, url_prefix='/api')
    app.register_blueprint(mercado_pago_bp, url_prefix='/api')
    app.register_blueprint(webhook_bp, url_prefix='/api')
    app.register_blueprint(transaccion_temporal_bp, url_prefix='/api')
    app.register_blueprint(vigilante_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    url_backend = app.config.get('URL_BACKEND', '127.0.0.1')
    port = app.config.get('PORT', 7777)
    app.run(host=url_backend, port=port, debug=True)
