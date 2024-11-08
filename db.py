import psycopg2
from flask import current_app

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=current_app.config['DATABASE']['dbname'],
            user=current_app.config['DATABASE']['user'],
            password=current_app.config['DATABASE']['password'],
            host=current_app.config['DATABASE']['host'],
            port=current_app.config['DATABASE']['port']
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
