# routes/vigilantes_routes.py
from flask import Blueprint

from controllers.residentes_controller import get_residentes, post_residente
from controllers.vigilante_controller import get_vigilantes, post_vigilante, update_vigilante_controller

residentes_bp = Blueprint('residentes_bp', __name__)

residentes_bp.route('/residentes', methods=['GET'])(get_residentes)
residentes_bp.route('/residente', methods=['POST'])(post_residente)
residentes_bp.route('/residente/<int:user_id>', methods=['PUT'])(update_vigilante_controller)







