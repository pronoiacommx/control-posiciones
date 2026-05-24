# database.py
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

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
    """
    Vacía la tabla posiciones e inserta los nuevos registros maestros.
    Desactiva las llaves foráneas temporalmente para permitir el TRUNCATE seguro.
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            conexion.autocommit = False
            cursor = conexion.cursor()
            
            # Desactivar validación de llaves foráneas para poder hacer TRUNCATE
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE posiciones;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            
            sql_query = """
                INSERT INTO posiciones (
                    posicion, descripcion_posicion, unidad, descripcion_unidad, centro_costos,
                    descripcion_centro_costos, nivel, subnivel, division, descripcion_division,
                    subdivision, descripcion_subdivision, grupo, descripcion_grupo, area,
                    descripcion_area, funcion, descripcion_funcion, localidad, descripcion_localidad,
                    estado, empleado, nombre_empleado, ocupado_ultima_vez, dias_sin_ocupar,
                    pos_supervisor, supervisor, jefe_rh, vigencia, estatus,
                    dias_vencidas, razon, tipo_de_just, clasific, complejo, gerente
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """
            
            cursor.executemany(sql_query, registros)
            conexion.commit()
            cant_filas = len(registros)
            cursor.close()
            return True, f"Base de datos sincronizada desde cero. Se importaron {cant_filas} posiciones con éxito."
            
    except Error as e:
        if conexion and conexion.is_connected():
            conexion.rollback()
        return False, f"Error en la sincronización de posiciones (Rollback aplicado): {e}"
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

def insertar_justificaciones_masivas(registros):
    """
    Vacía la tabla justificaciones e inserta los nuevos registros.
    """
    conexion = None
    try:
        conexion = obtener_conexion()
        if conexion.is_connected():
            conexion.autocommit = False
            cursor = conexion.cursor()
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE justificaciones;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            
            sql_query = """
                INSERT INTO justificaciones (
                    posicion, area_codigo, nombre_posicion, vigencia, comentarios,
                    tipo_posicion, fecha_inicio, dias_asignados, estatus_justificacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            cursor.executemany(sql_query, registros)
            conexion.commit()
            cant_filas = len(registros)
            cursor.close()
            return True, f"Tabla de Justificaciones sincronizada. Se importaron {cant_filas} registros con éxito."
            
    except Error as e:
        if conexion and conexion.is_connected():
            conexion.rollback()
        return False, f"Error en la sincronización de Justificaciones (Rollback aplicado): {e}"
    finally:
        if conexion and conexion.is_connected():
            conexion.close()