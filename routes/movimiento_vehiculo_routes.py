# routes/movimiento_vehiculo_routes.py
from flask import Blueprint
from controllers.movimiento_vehiculo_controller import movimiento_vehiculo_controller, get_parking_detalle

movimiento_vehiculo_bp = Blueprint('movimiento_vehiculo_bp', __name__)

# Ajuste: no se deben ejecutar funciones en la definición de rutas
movimiento_vehiculo_bp.route('/insertMovimientoVehiculo', methods=['POST'])(movimiento_vehiculo_controller)
movimiento_vehiculo_bp.route('/getDetalleParking/<int:id_conjunto>', methods=['GET'])(get_parking_detalle)




