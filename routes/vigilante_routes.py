# routes/vigilantes_routes.py
from flask import Blueprint
from controllers.vigilante_controller import  get_vigilantes, post_vigilante
vigilante_bp = Blueprint('vigilante_bp', __name__)

vigilante_bp.route('/vigilantes', methods=['GET'])(get_vigilantes)
vigilante_bp.route('/signupVigilante', methods=['POST'])(post_vigilante)






