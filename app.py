# app.py
import streamlit as st
import pandas as pd
import importlib  # <-- Librería mágica de Python para importaciones dinámicas
from utils import limpiar_entero, limpiar_texto, transformar_fecha
from database import insertar_registros_masivos

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
if opcion_menu == "📥 Carga de Archivo Excel":
    st.title("📥 Cargador de Reportes de Posiciones")
    st.markdown("Arrastra el archivo maestro de Recursos Humanos para sincronizar de forma masiva la base de datos MySQL.")

    archivo_cargado = st.file_uploader("Selecciona el archivo Excel (.xlsx)", type=["xlsx"])

    if archivo_cargado is not None:
        try:
            excel_file = pd.ExcelFile(archivo_cargado)
            pestanas = excel_file.sheet_names
            
            # Intenta preseleccionar la pestaña 'Rep Posiciones' por defecto
            indice_defecto = pestanas.index("Rep Posiciones") if "Rep Posiciones" in pestanas else 0
            
            col1, _ = st.columns([2, 2])
            with col1:
                pestana_seleccionada = st.selectbox("Selecciona la pestaña a importar:", pestanas, index=indice_defecto)
            
            df = pd.read_excel(archivo_cargado, sheet_name=pestana_seleccionada, dtype=str)
            
            st.subheader(f"👀 Vista previa de los datos ('{pestana_seleccionada}')")
            st.dataframe(df.head(5), use_container_width=True)
            
            if st.button("🚀 Procesar e Insertar en Base de Datos", type="primary"):
                with st.spinner("Limpiando e inyectando registros masivos en MySQL..."):
                    registros_a_insertar = []
                    
                    for _, fila in df.iterrows():
                        posicion = limpiar_entero(fila.get('Posición'))
                        if not posicion:
                            continue  # Ignora filas vacías o sin número de posición válido
                        
                        registro = (
                            posicion,
                            limpiar_texto(fila.get('Descripción posición')),
                            limpiar_entero(fila.get('Unidad')),
                            limpiar_texto(fila.get('Descripción unidad')),
                            limpiar_entero(fila.get('Centro costos')),
                            limpiar_texto(fila.get('Descripción centro de costos')),
                            limpiar_texto(fila.get('Nivel')),
                            limpiar_entero(fila.get('Subnivel')),
                            limpiar_entero(fila.get('División')),
                            limpiar_texto(fila.get('Descripción división')),
                            limpiar_texto(fila.get('Subdivisión')),
                            limpiar_texto(fila.get('Descripción subdivisión')),
                            limpiar_entero(fila.get('Grupo')),
                            limpiar_texto(fila.get('Descripción grupo')),
                            limpiar_texto(fila.get('Área')),
                            limpiar_texto(fila.get('Descripción área')),
                            limpiar_entero(fila.get('Función')),
                            limpiar_texto(fila.get('Descripción función')),
                            limpiar_entero(fila.get('Localidad')),
                            limpiar_texto(fila.get('Descripción localidad')),
                            limpiar_texto(fila.get('Estado')),
                            limpiar_entero(fila.get('Empleado')),
                            limpiar_texto(fila.get('Nombre empleado')),
                            transformar_fecha(fila.get('Ocupado ultima vez')),
                            limpiar_entero(fila.get('Días sin ocupar')),
                            limpiar_entero(fila.get('Pos. Supervisor')),
                            limpiar_entero(fila.get('Supervisor')),
                            limpiar_texto(fila.get('JEFE RH')),
                            transformar_fecha(fila.get('VIGENCIA')),
                            limpiar_texto(fila.get('ESTATUS')),
                            limpiar_entero(fila.get('DIAS VENCIDAS')),
                            limpiar_texto(fila.get('RAZÓN')),
                            limpiar_texto(fila.get('Tipo de Just')),
                            limpiar_texto(fila.get('Clasific')),
                            limpiar_texto(fila.get('Complejo')),
                            limpiar_texto(fila.get('Gerente'))
                        )
                        registros_a_insertar.append(registro)
                    
                    if registros_a_insertar:
                        exito, mensaje = insertar_registros_masivos(registros_a_insertar)
                        if exito:
                            st.success(f"🎉 {mensaje}")
                            st.balloons()
                        else:
                            st.error(f"❌ Ocurrió un error: {mensaje}")
                    else:
                        st.warning("⚠️ No se encontraron posiciones estructuradas válidas para insertar.")
                        
        except Exception as e:
            st.error(f"🚨 Error al abrir o procesar el libro de Excel: {e}")


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