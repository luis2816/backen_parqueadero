
from flask import Blueprint
from controllers.webhook_controller import obtenerDetalleTransacción_id

webhook_bp = Blueprint('webhook_bp', __name__)

# Ajuste: no se deben ejecutar funciones en la definición de rutas
webhook_bp.route('/webhook/<string:id_transaccion>', methods=['GET'])(obtenerDetalleTransacción_id)
