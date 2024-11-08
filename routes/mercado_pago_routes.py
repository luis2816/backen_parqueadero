# routes/user_routes.py
from flask import Blueprint
from controllers.mercado_pago_controller import pay, notifications, compra_sin_registro, notification_compra_sin_registro

mercado_pago_bp = Blueprint('mercado_pago_bp', __name__)

# Ajuste: no se deben ejecutar funciones en la definición de rutas
mercado_pago_bp.route('/pay', methods=['POST'])(pay)
mercado_pago_bp.route('/compra_sin_registro', methods=['POST'])(compra_sin_registro)

mercado_pago_bp.route('/notifications/<string:id_usuario>', methods=['POST'])(notifications)
mercado_pago_bp.route('/notification_compra_sin_registro/<string:id_usuario_temporal>', methods=['POST'])(notification_compra_sin_registro)

