# app.py
import streamlit as st
import pandas as pd
import importlib  # <-- Librería mágica de Python para importaciones dinámicas
from utils import limpiar_entero, limpiar_texto, transformar_fecha
from database import insertar_registros_masivos
from utils import bloqueo_pantalla_carga
# IMPORTACIÓN DINÁMICA DEL DICCIONARIO DE REPORTES
from reportes import DICCIONARIO_REPORTES


# Configuración global de la página
st.set_page_config(page_title="Sistema de Administración de Plantillas", page_icon="📊", layout="wide")

# --- MENÚ LATERAL DE NAVEGACIÓN ---
st.sidebar.title("Menú Principal")
opcion_menu = st.sidebar.radio(
    "Selecciona una sección:",
    ["📥 Carga de Archivo Excel", "📊 Panel de Reportes (Gerentes)"]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 Desarrollado para el análisis estratégico de cobertura de vacantes y control de nómina.")


# =========================================================================
# SECCIÓN 1: CARGA DE ARCHIVO
# =========================================================================
# app.py (Sección de Carga de Archivo unificada y protegida por FK)
if opcion_menu == "📥 Carga de Archivo Excel":
    st.title("📥 Cargador de Reportes de Posiciones e Insumos")
    st.markdown("Sube el archivo maestro en formato `.xlsx`. El sistema procesará automáticamente las pestañas **'Rep Posiciones'** y **'Justificación'** en orden jerárquico.")
    
    archivo_subido = st.file_uploader("Selecciona el archivo Excel corporativo:", type=["xlsx"])
    
    if archivo_subido is not None:
        try:
            excel_file = pd.ExcelFile(archivo_subido)
            pestanas = excel_file.sheet_names
            
            st.info(f"📁 Archivo detectado correctamente. Pestañas encontradas: {', '.join(pestanas)}")
            
            if st.button("🚀 Procesar y Sincronizar Base de Datos", type="primary"):
                from utils import bloqueo_pantalla_carga
                from database import insertar_registros_masivos, insertar_justificaciones_masivas
                
                exito_pos = False
                msg_pos = "No se encontró la pestaña 'Rep Posiciones'."
                set_posiciones_validas = set()  # Para guardar los IDs de posiciones válidas insertadas
                
                # =============================================================
                # PASO 1: INSERTAR PRIMERO EL MAESTRO DE POSICIONES (PADRE)
                # =============================================================
                if "Rep Posiciones" in pestanas:
                    with bloqueo_pantalla_carga("Procesando y limpiando Maestro de Posiciones..."):
                        df_pos = pd.read_excel(archivo_subido, sheet_name="Rep Posiciones")
                        
                        registros_pos = []
                        for _, fila in df_pos.iterrows():
                            id_pos = limpiar_entero(fila.get('Posición'))
                            if id_pos:
                                set_posiciones_validas.add(id_pos)
                                
                            registros_pos.append((
                                id_pos,
                                limpiar_texto(fila.get('Descripción posición')),
                                limpiar_entero(fila.get('Unidad')),
                                limpiar_texto(fila.get('Descripción unidad')),
                                limpiar_texto(fila.get('Centro costos')),
                                limpiar_texto(fila.get('Descripción centro de costos')),
                                limpiar_texto(fila.get('Nivel')),
                                limpiar_texto(fila.get('Subnivel')),
                                limpiar_texto(fila.get('División')),
                                limpiar_texto(fila.get('Descripción división')),
                                limpiar_texto(fila.get('Subdivisión')),
                                limpiar_texto(fila.get('Descripción subdivisión')),
                                limpiar_texto(fila.get('Grupo')),
                                limpiar_texto(fila.get('Descripción grupo')),
                                limpiar_texto(fila.get('Área')),
                                limpiar_texto(fila.get('Descripción área')),
                                limpiar_texto(fila.get('Función')),
                                limpiar_texto(fila.get('Descripción función')),
                                limpiar_texto(fila.get('Localidad')),
                                limpiar_texto(fila.get('Descripción localidad')),
                                limpiar_texto(fila.get('Estado')),
                                limpiar_entero(fila.get('Empleado')),
                                limpiar_texto(fila.get('Nombre empleado')),
                                transformar_fecha(fila.get('Ocupado ultima vez')),
                                limpiar_entero(fila.get('Días sin ocupar')),
                                limpiar_entero(fila.get('Pos. Supervisor')),
                                limpiar_texto(fila.get('Supervisor')),
                                limpiar_texto(fila.get('JEFE RH')),
                                transformar_fecha(fila.get('VIGENCIA')),
                                limpiar_texto(fila.get('ESTATUS')),
                                limpiar_entero(fila.get('DIAS VENCIDAS')),
                                limpiar_texto(fila.get('RAZÓN')),
                                limpiar_texto(fila.get('Tipo de Just')),
                                limpiar_texto(fila.get('Clasific')),
                                limpiar_texto(fila.get('Complejo')),
                                limpiar_texto(fila.get('Gerente'))
                            ))
                        
                        if registros_pos:
                            exito_pos, msg_pos = insertar_registros_masivos(registros_pos)
                
                # =============================================================
                # PASO 2: INSERTAR LAS JUSTIFICACIONES (HIJO) FILTRANDO POR REFERENCIA
                # =============================================================
                exito_just = False
                msg_just = "No se encontró la pestaña 'Justificación'."
                
                if "Justificación" in pestanas:
                    if not exito_pos:
                        st.error("🛑 Se detuvo la carga de 'Justificación' porque el maestro de posiciones falló o no existe.")
                    else:
                        with bloqueo_pantalla_carga("Procesando y validando Pestaña de Justificaciones..."):
                            df_just = pd.read_excel(archivo_subido, sheet_name="Justificación")
                            
                            registros_just = []
                            omitidos = 0
                            
                            for _, fila in df_just.iterrows():
                                id_pos_just = limpiar_entero(fila.get('Posición'))
                                
                                # VALIDACIÓN DE INTEGRIDAD REFERENCIAL ANTES DE IR A MYSQL
                                if id_pos_just not in set_posiciones_validas:
                                    omitidos += 1
                                    continue  # Se salta el registro para evitar romper la llave foránea
                                    
                                registros_just.append((
                                    id_pos_just,
                                    limpiar_texto(fila.get('Area')),
                                    limpiar_texto(fila.get('Posicion')),
                                    transformar_fecha(fila.get('Vigencia')),
                                    limpiar_texto(fila.get('Comentarios')),
                                    limpiar_texto(fila.get('Tipo')),
                                    transformar_fecha(fila.get('Fecha de Inicio')),
                                    limpiar_entero(fila.get('Dias Asignados')),
                                    limpiar_texto(fila.get('Estatus'))
                                ))
                                
                            if registros_just:
                                exito_just, msg_just = insertar_justificaciones_masivas(registros_just)
                                if omitidos > 0:
                                    msg_just += f" (Se omitieron {omitidos} registros huérfanos que no existían en el maestro)."
                            else:
                                msg_just = f"⚠️ No se cargaron justificaciones. Las {omitidos} posiciones procesadas eran huérfanas."
                
                # --- RENDER DE RESULTADOS FINALES ---
                st.markdown("### 📊 Resultado de la Sincronización Integrada:")
                if exito_pos:
                    st.success(f"🔹 {msg_pos}")
                else:
                    st.error(f"❌ Posiciones: {msg_pos}")
                    
                if exito_just:
                    st.success(f"🔹 {msg_just}")
                elif "Justificación" in pestanas and exito_pos:
                    st.warning(f"⚠️ Justificaciones: {msg_just}")
                    
        except Exception as e:
            st.error(f"🚨 Error crítico en la orquestación del libro Excel: {e}")



# =========================================================================
# SECCIÓN 2: PANEL DE REPORTES DE GERENCIA (DINÁMICO)
# =========================================================================
elif opcion_menu == "📊 Panel de Reportes (Gerentes)":
    st.title("📈 Centro de Inteligencia & Reportes Directivos")
    st.markdown("Selecciona el análisis ejecutivo que deseas consultar en tiempo real.")
    st.markdown("---")
    
    # El selectbox ahora se alimenta AUTOMÁTICAMENTE de las llaves de nuestro diccionario
    opciones_reportes = list(DICCIONARIO_REPORTES.keys())
    
    reporte_seleccionado = st.selectbox(
        "Reporte Ejecutivo Disponible:",
        opciones_reportes
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- MOTOR DE IMPORTACIÓN EN TIEMPO REAL ---
    if reporte_seleccionado:
        # 1. Obtener el nombre del archivo asociado al reporte seleccionado
        nombre_modulo = DICCIONARIO_REPORTES[reporte_seleccionado]
        
        try:
            # 2. Cargar el archivo .py de forma dinámica desde la carpeta reportes
            modulo_reporte = importlib.import_module(f"reportes.{nombre_modulo}")
            
            # 3. Ejecutar la función estándar 'mostrar_reporte' de ese archivo
            if hasattr(modulo_reporte, "mostrar_reporte"):
                modulo_reporte.mostrar_reporte()
            else:
                st.error(f"🚨 Error: El archivo '{nombre_modulo}.py' no tiene definida la función 'mostrar_reporte()'.")
                
        except ModuleNotFoundError:
            st.error(f"❌ No se encontró el archivo físico 'reportes/{nombre_modulo}.py'. Verifica la configuración.")
        except Exception as e:
            st.error(f"🚨 Error al intentar renderizar el módulo: {e}")