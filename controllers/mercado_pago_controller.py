from flask import Flask, request, jsonify, redirect, url_for
import mercadopago
from  models.user_model import update_user_estado, get_user_id, update_user_cantidad_licencias, insert_user
from models.webhook_model import insert_webhook, get_webhook_id
from models.transaccion_temporal_model import update_transaction_id, get_transaccion_temporal_byf_id, delete_transaccion_temporal
from utils.email_utils import send_email_to_user
from flask import current_app
from datetime import datetime
import  json


sdk = mercadopago.SDK("TEST-6016242716648256-040301-45e8c8a0fe3644074d60dba0cedadfe8-2000752194")

def pay():
    url_backend = current_app.config['URL_PRODUCCION']
    url_fronend = current_app.config['URL_PRODUCCION_FRONTEND']
    # Obtén los datos del pago del request
    if request.is_json:
        data = request.get_json()
        cantidad = data.get("cantidad")
        precio = data.get("precio")
        id_usuario = data.get("id_usuario")
        print(cantidad, precio, id_usuario)
    else:
        data = request.form

    # Crea una preferencia de pago
    url_webhook = f"{url_backend}/api/notifications/{id_usuario}"
    url_success = f"{url_fronend}/success"
    url_rejection = f"{url_fronend}/failure"
    url_pending = f"{url_fronend}/pending"
    preference_data = {
        "items": [
            {
                "id_persona": id_usuario,
                "quantity": float(cantidad),
                "unit_price": float(precio)
            }
        ],
        "back_urls": {
            "success": url_success,
            "failure": url_rejection,
            "pending": url_pending
        },
        "auto_return": "approved",
        "notification_url": url_webhook
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print(preference_response)  # Imprimir la respuesta completa para depuración
        preference = preference_response.get("response")

        if "response" in preference_response and "init_point" in preference_response["response"]:
            preference = preference_response["response"]
            payment_url = preference["init_point"]
            print(payment_url)
            return jsonify({"payment_url": payment_url})
        else:
            return jsonify({"error": "Error en la respuesta de Mercado Pago", "details": preference_response}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def notifications(id_usuario):
    try:
        data = request.json
        print("dato del usuario", id_usuario)
        if "type" in data and data["type"] == "payment":
            transaction_id = data["data"]["id"]
            transaction_details = sdk.payment().get(transaction_id)

            print("detalle d ela transacción")
            print(transaction_details)
            status = transaction_details["response"].get("status")
            cantidad = transaction_details["response"]["additional_info"]["items"][0]["quantity"]
            unit_price = transaction_details["response"]["additional_info"]["items"][0]["unit_price"]

            # Convertir a números
            cantidad = int(cantidad)
            unit_price = float(unit_price)
            valor_total = cantidad * unit_price

            # Obtener la fecha actual
            fecha_actual = datetime.now()
            # Formatear la fecha al formato deseado (YYYY-MM-DD)
            fecha_formateada = fecha_actual.strftime('%Y-%m-%d')


            if status == "released":
                print("La transacción está en estado 'released'. No se realizará ninguna acción.")

            elif status == "approved":
                insert_webhook(transaction_details, cantidad, valor_total, id_usuario, transaction_id, "approved")
                print("Actualizando cantidad de licencias del usuario")
                update_user_cantidad_licencias(id_usuario, cantidad)
                print("Obtener información del usuario como el correo")
                user_details = get_user_id(id_usuario)

                email = user_details[6]  # El email está en la posición 6 de la tupla
                fecha_registro = user_details[9]  # fecha de regitro está en la posición 9 de la tupla
                print(email, cantidad, fecha_registro)

                if email:
                    print("entro al envio del correo")
                    # Enviar correo electrónico al usuario con el link para ingresar  ala plataforma
                    reset_link = f"https://b4ec-45-167-125-15.ngrok-free.app"
                    email_body = f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f8f9fa;
                                margin: 0;
                                padding: 20px;
                            }}
                            .container {{
                                background-color: #ffffff;
                                border-radius: 8px;
                                padding: 20px;
                                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                            }}
                            h2 {{
                                color: #007bff;
                            }}
                            p {{
                                line-height: 1.6;
                            }}
                            .footer {{
                                margin-top: 20px;
                                font-size: 12px;
                                color: #777;
                            }}
                            a {{
                                color: #007bff;
                                text-decoration: none;
                            }}
                            a:hover {{
                                text-decoration: underline;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h2>Confirmación de compra de cuentas</h2>
                            <p>Estimado/a usuario,</p>
                            <p>Nos complace informarle que hemos recibido su pedido y que la compra de las licencias ha sido procesada con éxito. Agradecemos sinceramente su confianza en nuestros servicios.</p>

                            <h3>Detalles de su compra:</h3>
                            <ul>
                                <li><strong>codigo de transacción:</strong> {transaction_id}</li>
                                <li><strong>Número de licencias adquiridas:</strong> {cantidad}</li>
                                <li><strong>Fecha de compra:</strong> {fecha_formateada}</li>
                                <li><strong>Total de la transacción:</strong> {valor_total}</li>
                            </ul>

                            <p>Por favor, haz clic en el siguiente enlace para ingresar a la plataforma:</p>
                            <p><a href="{reset_link}">{reset_link}</a></p>

                            <p>Si tiene alguna pregunta o necesita asistencia, no dude en ponerse en contacto con nuestro equipo de soporte.</p>

                            <p>Agradecemos nuevamente su compra y quedamos a su disposición para cualquier consulta adicional.</p>

                            <div class="footer">
                                Atentamente,<br>
                                [Tu nombre]<br>
                                [Tu puesto]<br>
                                [Nombre de la empresa]<br>
                                [Teléfono de contacto]<br>
                                [Correo electrónico]<br>
                                [Web de la empresa]
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    send_email_to_user(email, "Confirmación de compra de cuentas", email_body)

            elif status == "rejected":
                print(f"Entro al estado rejected: {status}")
                insert_webhook(transaction_details, cantidad, valor_total, id_usuario, transaction_id, "rejected")


            elif status == "pending":
                print(f"Entro al estado pending: {status}")
                insert_webhook(transaction_details, cantidad, valor_total, id_usuario, transaction_id, "pending")

            print("Datos de webhook insertados en la base de datos.")
            return jsonify({"message": "Webhook recibido"}), 200

        else:
            return jsonify({"message": "No se encontraron datos de pago"}), 200

    except Exception as e:
        print("Error en webhook:", str(e))
        return jsonify({"error": str(e)}), 500


def compra_sin_registro():
    url_backend = current_app.config['URL_PRODUCCION']
    url_frontend = current_app.config['URL_PRODUCCION_FRONTEND']

    if request.is_json:
        data = request.get_json()
        cantidad = int(data.get("cantidad"))
        precio = float(data.get("precio"))
        id_usuario_temporal = data.get("id_usuario_temporal")

        print("Cantidad:", cantidad, "Precio:", precio, "id_usuario_temporal:", id_usuario_temporal)  # Para depuración
    else:
        data = request.form

    # Crear preferencia de pago
    url_webhook = f"{url_backend}/api/notification_compra_sin_registro/{id_usuario_temporal}"
    url_success = f"{url_frontend}/success"
    url_rejection = f"{url_frontend}/failure"
    url_pending = f"{url_frontend}/pending"

    # Ajustando el formato del preference_data
    preference_data = {
        "items": [
            {
                "id_usuario_temporal": id_usuario_temporal,
                "quantity": cantidad,
                "unit_price": precio
            }
        ],
        "back_urls": {
            "success": url_success,
            "failure": url_rejection,
            "pending": url_pending
        },
        "auto_return": "approved",
        "notification_url": url_webhook,
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        print("Respuesta de preferencia:", preference_response)  # Imprimir para depuración
        preference = preference_response.get("response")

        if "response" in preference_response and "init_point" in preference_response["response"]:
            payment_url = preference["init_point"]
            print("URL de pago:", payment_url)

            # Obtener el ID de la transacción
            transaction_id = preference.get("id")  # Obtén el ID de la transacción

            # Actualizar el registro temporal con el ID de la transacción
            update_transaction_id(id_usuario_temporal, transaction_id)

            return jsonify({"payment_url": payment_url})
        else:
            return jsonify({"error": "Error en la respuesta de Mercado Pago", "details": preference_response}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def notification_compra_sin_registro(id_usuario_temporal):
    print("Webhook recibido")
    print("usuario temporal")
    print(id_usuario_temporal)
    try:
        data = request.json
        if "type" in data and data["type"] == "payment":
            transaction_id = data["data"]["id"]
            transaction_details = sdk.payment().get(transaction_id)

            print("detalle d ela transacción")
            print(transaction_details)
            status = transaction_details["response"].get("status")
            cantidad = transaction_details["response"]["additional_info"]["items"][0]["quantity"]
            unit_price = transaction_details["response"]["additional_info"]["items"][0]["unit_price"]

            # Convertir a números
            cantidad = int(cantidad)
            unit_price = float(unit_price)
            valor_total = cantidad * unit_price

            # Obtener la fecha actual
            fecha_actual = datetime.now()
            # Formatear la fecha al formato deseado (YYYY-MM-DD)
            fecha_formateada = fecha_actual.strftime('%Y-%m-%d')


            if status == "released":
                print("La transacción está en estado 'released'. No se realizará ninguna acción.")

            elif status == "approved":
                ##Obtenemos la indformación del registro temporal
                transaction_data = get_transaccion_temporal_byf_id(id_usuario_temporal)
                if transaction_data:
                    print("Datos de la transacción:", transaction_data)
                    # Extraer los datos necesarios para insertar
                    nombre = transaction_data["nombre"]
                    apellido = transaction_data["apellido"]
                    tipo_identificacion = transaction_data["tipo_identificacion"]
                    numero_identificacion = transaction_data["numero_identificacion"]
                    email = transaction_data["email"]
                    sexo = transaction_data["sexo"]
                    telefono = transaction_data["telefono"]
                    fecha_nacimiento = transaction_data["fecha_nacimiento"]
                    rol_id = transaction_data["rol_id"]
                    estado = transaction_data["estado"]
                    cantidad_licencia = transaction_data["cantidad_licencia"]
                    password= None
                    # Llamar a la función para insertar los datos en la base de datos a la tabla usuarios
                    user_id = insert_user(
                        nombre,
                        apellido,
                        tipo_identificacion,
                        numero_identificacion,
                        email,
                        password,  # Contraseña generada
                        sexo,
                        telefono,
                        fecha_nacimiento,
                        rol_id,
                        cantidad_licencia,
                        estado
                    )
                    #Registrar el detalle de la transacción aprovada
                    insert_webhook(transaction_details, cantidad, valor_total, user_id, transaction_id, "approved")
                    #Elimino el registro temporal
                    delete_transaccion_temporal(id_usuario_temporal)
                    #obtenemos

                    #envio de correo
                    print("Obtener información del usuario como el correo")
                    user_details = get_user_id(user_id)

                    email = user_details[6]  # El email está en la posición 6 de la tupla
                    token = user_details[7]  # El token está en la posición 7 de la tupla

                    fecha_registro = user_details[9]  # fecha de regitro está en la posición 9 de la tupla
                    print(email, cantidad, fecha_registro)

                    if email:
                        print("entro al envio del correo")
                        # Enviar correo electrónico al usuario con el link para ingresar  ala plataforma
                        reset_link = f"{current_app.config['URL_PRODUCCION_FRONTEND']}/reset-password?token={token}"
                        email_body = f"""
                                       <!DOCTYPE html>
                                       <html lang="es">
                                       <head>
                                           <meta charset="UTF-8">
                                           <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                           <style>
                                               body {{
                                                   font-family: Arial, sans-serif;
                                                   background-color: #f8f9fa;
                                                   margin: 0;
                                                   padding: 20px;
                                               }}
                                               .container {{
                                                   background-color: #ffffff;
                                                   border-radius: 8px;
                                                   padding: 20px;
                                                   box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                                               }}
                                               h2 {{
                                                   color: #007bff;
                                               }}
                                               p {{
                                                   line-height: 1.6;
                                               }}
                                               .footer {{
                                                   margin-top: 20px;
                                                   font-size: 12px;
                                                   color: #777;
                                               }}
                                               a {{
                                                   color: #007bff;
                                                   text-decoration: none;
                                               }}
                                               a:hover {{
                                                   text-decoration: underline;
                                               }}
                                           </style>
                                       </head>
                                       <body>
                                           <div class="container">
                                               <h2>Confirmación de compra de cuentas</h2>
                                               <p>Estimado/a usuario,</p>
                                               <p>Nos complace informarle que hemos recibido su pedido y que la compra de las licencias ha sido procesada con éxito. Agradecemos sinceramente su confianza en nuestros servicios.</p>

                                               <h3>Detalles de su compra:</h3>
                                               <ul>
                                                   <li><strong>codigo de transacción:</strong> {transaction_id}</li>
                                                   <li><strong>Número de licencias adquiridas:</strong> {cantidad}</li>
                                                   <li><strong>Fecha de compra:</strong> {fecha_formateada}</li>
                                                   <li><strong>Total de la transacción:</strong> {valor_total}</li>
                                               </ul>

                                               <p>Por favor, haz clic en el siguiente enlace para  asignar contraseña:</p>
                                               <p><a href="{reset_link}">{reset_link}</a></p>

                                               <p>Si tiene alguna pregunta o necesita asistencia, no dude en ponerse en contacto con nuestro equipo de soporte.</p>

                                               <p>Agradecemos nuevamente su compra y quedamos a su disposición para cualquier consulta adicional.</p>

                                               <div class="footer">
                                                   Atentamente,<br>
                                                   [Tu nombre]<br>
                                                   [Tu puesto]<br>
                                                   [Nombre de la empresa]<br>
                                                   [Teléfono de contacto]<br>
                                                   [Correo electrónico]<br>
                                                   [Web de la empresa]
                                               </div>
                                           </div>
                                       </body>
                                       </html>
                                       """
                        send_email_to_user(email, "Confirmación de compra de cuentas", email_body)

                    print("registros exitosos estado aprovado")
                else:
                    print("No se encontró la transacción.")


            elif status == "rejected":
                print(f"Entro al estado rejected: {status}")


            elif status == "pending":
                print(f"Entro al estado pending: {status}")

            print("Datos de webhook insertados en la base de datos.")
            return jsonify({"message": "Webhook recibido"}), 200
        else:
            return jsonify({"message": "No se encontraron datos de pago"}), 200

    except Exception as e:
        print("Error en webhook:", str(e))
        return jsonify({"error": str(e)}), 500



def obtenerDetalleTransacción_id(id_transaccion):
    """Controlador para obtener un usuario por ID."""
    try:
        transaccion = get_webhook_id(id_transaccion)
        print(transaccion)
        if not transaccion:
            return jsonify({"msg": "Transacción not found"}), 404

        result = {
            'id': transaccion[0],
            'cantidad_licencia': transaccion[1],
            'valor_compra': transaccion[2],
            'fecha_registro': transaccion[3],
            'id_transaccion': transaccion[4],
            'estado': transaccion[5]
        }
        return jsonify(result), 200
    except Exception as e:
        print(e)
        return jsonify({"msg": str(e)}), 500
