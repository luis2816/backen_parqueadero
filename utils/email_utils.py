from flask_mail import Message
from flask import current_app

def send_email_to_user(email, subject, html_body):
    with current_app.app_context():
        mail = current_app.extensions.get('mail')
        msg = Message(subject=subject,
                      recipients=[email],
                      html=html_body)  # Solo se usa el contenido HTML
        mail.send(msg)