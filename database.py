# fastapi_ferremas_api/database.py
import MySQLdb

def get_conexion():
    try:
        return MySQLdb.connect(
            host='127.0.0.1',
            user='root',
            password='ichigoken28',  # Asegúrate de que sea la correcta
            db='ferremax',
            port=3306  # Agrega el puerto aquí (si es el puerto por defecto)
        )
    except MySQLdb.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None