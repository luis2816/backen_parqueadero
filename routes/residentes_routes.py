# routes/residentes_routes.py
from flask import Blueprint
from controllers.residentes_controller import get_residentes, post_residente, update_residente_controller, \
     get_registrar_ingreso_residente
from models.residentes_model import registrar_salida_residente

residentes_bp = Blueprint('residentes_bp', __name__)
residentes_bp.route('/residentes', methods=['GET'])(get_residentes)
residentes_bp.route('/residente', methods=['POST'])(post_residente)
residentes_bp.route('/residente/<int:user_id>', methods=['PUT'])(update_residente_controller)
residentes_bp.route('/ingreso_residente_placa/<string:placa>', methods=['GET'])(get_registrar_ingreso_residente)
residentes_bp.route('/salida_residente_placa/<string:placa>', methods=['GET'])(registrar_salida_residente)









