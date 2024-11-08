# routes/transaccion_temporal_routes.py
from flask import Blueprint
from controllers.transaccion_temporal_controller import  registro_transaccion_temporal, actualizar_transaction_id

transaccion_temporal_bp = Blueprint('transaccion_temporal_bp', __name__)

# Ajuste: no se deben ejecutar funciones en la definición de rutas
transaccion_temporal_bp.route('/insertTransaccionTemporal', methods=['POST'])(registro_transaccion_temporal)
transaccion_temporal_bp.route('/actualizar_transaction_id/<int:id>', methods=['PUT'])(actualizar_transaction_id)

