# database.py
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

def obtener_conexion():
    """Establece la conexión con MySQL usando las variables de entorno."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def insertar_registros_masivos(registros):
    """Inserta o actualiza miles de registros de golpe utilizando executemany."""
    conexion = None
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            cursor = conexion.cursor()
            
            sql_query = """
                INSERT INTO z_posiciones (
                    posicion, descripcion_posicion, unidad, descripcion_unidad, centro_costos,
                    descripcion_centro_costos, nivel, subnivel, division, descripcion_division,
                    subdivision, descripcion_subdivision, grupo, descripcion_grupo, area,
                    descripcion_area, funcion, descripcion_funcion, localidad, descripcion_localidad,
                    estado, empleado, nombre_empleado, ocupado_ultima_vez, dias_sin_ocupar,
                    pos_supervisor, supervisor, jefe_rh, vigencia, estatus,
                    dias_vencidas, razon, tipo_de_just, clasific, complejo, gerente
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    descripcion_posicion=VALUES(descripcion_posicion), unidad=VALUES(unidad), 
                    descripcion_unidad=VALUES(descripcion_unidad), centro_costos=VALUES(centro_costos),
                    descripcion_centro_costos=VALUES(descripcion_centro_costos), nivel=VALUES(nivel), subnivel=VALUES(subnivel),
                    estado=VALUES(estado), empleado=VALUES(empleado), nombre_empleado=VALUES(nombre_empleado),
                    pos_supervisor=VALUES(pos_supervisor), supervisor=VALUES(supervisor), jefe_rh=VALUES(jefe_rh), 
                    vigencia=VALUES(vigencia), estatus=VALUES(estatus), gerente=VALUES(gerente);
            """
            
            cursor.executemany(sql_query, registros)
            conexion.commit()
            cant_filas = cursor.rowcount
            cursor.close()
            return True, f"Proceso terminado con éxito. Filas afectadas: {cant_filas}"
            
    except Error as e:
        return False, f"Error de MySQL: {e}"
    finally:
        if conexion and conexion.is_connected():
            conexion.close()