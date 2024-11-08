# routes/user_routes.py
from flask import Blueprint
from controllers.user_controller import get_users_controller, check_token, login_controller, get_user_id_controller, get_user_photo_controller, signup_controller, update_user_controller, cambiar_password, reset_password, verificar_user_email

user_bp = Blueprint('user_bp', __name__)

user_bp.route('/usuarios', methods=['GET'])(get_users_controller)
user_bp.route('/login', methods=['POST'])(login_controller)
user_bp.route('/usuario', methods=['GET'])(get_user_id_controller)
user_bp.route('/usuario/<int:user_id>/foto', methods=['GET'])(get_user_photo_controller)
user_bp.route('/signup', methods=['POST'])(signup_controller)
user_bp.route('/usuario/<int:user_id>', methods=['PUT'])(update_user_controller)
user_bp.route('/usuario/cambiar_password/<int:user_id>', methods=['PUT'])(cambiar_password)
user_bp.route('/reset-password', methods=['POST'])(reset_password)
user_bp.route('/check-token/<string:token>', methods=['GET'])(check_token)
user_bp.route('/verificar_email', methods=['POST'])(verificar_user_email)




