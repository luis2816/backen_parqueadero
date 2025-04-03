import os

#postgresql://felipe:N4590ixFcMkqAEEn5UruOwLXG1e5iT1e@dpg-csmntrhu0jms73fqhe4g-a.oregon-postgres.render.com/secury_park
class Config:
    UPLOAD_FOLDER_FOTO_PERFIL = 'foto_perfil'
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret')  # Cambia esto por una clave secreta más segura
    DATABASE = {
        'dbname': os.getenv('DB_NAME', 'secury_park_iny2'),
        'user': os.getenv('DB_USER', 'secury_park_iny2_user'),
        'password': os.getenv('DB_PASSWORD', 'nawWNMIlFHddgWyGwB1y9C7Mhnw8qskg'),
        'host': os.getenv('DB_HOST', 'pg-cvmru66mcj7s73bvnq60-a.oregon-postgres.render.com'),
        'port': os.getenv('DB_PORT', '5432')
    }
    URL_BACKEND = os.getenv('URL_BACKEND', '127.0.0.1')

    PORT = int(os.getenv('PORT', 7777))
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ordonezfelipe2816@gmail.com'
    MAIL_PASSWORD = 'tgop olmt qxql oykj'
    MAIL_DEFAULT_SENDER = 'ordonezfelipe2816@gmail.com'
    URL_PRODUCCION= 'https://backen-parqueadero.onrender.com'
    URL_PRODUCCION_FRONTEND= 'hhttps://fronted-parqueadero.onrender.com'