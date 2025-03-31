# routes/vigilantes_routes.py
from flask import Blueprint
from controllers.vigilante_controller import get_vigilantes, post_vigilante, update_vigilante_controller

vigilante_bp = Blueprint('vigilante_bp', __name__)

vigilante_bp.route('/vigilantes', methods=['GET'])(get_vigilantes)
vigilante_bp.route('/signupVigilante', methods=['POST'])(post_vigilante)
vigilante_bp.route('/vigilante/<int:user_id>', methods=['PUT'])(update_vigilante_controller)







