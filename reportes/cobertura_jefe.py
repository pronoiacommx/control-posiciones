# reportes/cobertura_jefe.py
import streamlit as st
import pandas as pd
from database import obtener_conexion

def mostrar_reporte():
    st.subheader("📋 Cobertura de Plantilla por Jefe de Capital Humano")
    st.markdown("Desglose operativo de posiciones activas y vacantes (Planta vs Eventual) asignadas a cada Jefe de RH.")
    
    try:
        conexion = obtener_conexion()
        
        # Query que pivotea las posiciones de PLANTA y EVENTUAL calculando Ocupadas, Vacantes y Totales por Jefe
        query = """
            SELECT 
                IFNULL(jefe_rh, 'NO ASIGNADO') AS `Jefe RH`,
                SUM(CASE WHEN clasific = 'PLANTA' AND Estado = 'OCUPADA' THEN 1 ELSE 0 END) AS `PLANTA OCUPADA`,
                SUM(CASE WHEN clasific = 'PLANTA' AND Estado = 'VACANTE' THEN 1 ELSE 0 END) AS `PLANTA VACANTE`,
                SUM(CASE WHEN clasific = 'PLANTA' THEN 1 ELSE 0 END) AS `TOTAL PLANTA`,
                SUM(CASE WHEN clasific = 'EVENTUAL' AND Estado = 'OCUPADA' THEN 1 ELSE 0 END) AS `EVENTUAL OCUPADA`,
                SUM(CASE WHEN clasific = 'EVENTUAL' AND Estado = 'VACANTE' THEN 1 ELSE 0 END) AS `EVENTUAL VACANTE`,
                SUM(CASE WHEN clasific = 'EVENTUAL' THEN 1 ELSE 0 END) AS `TOTAL EVENTUAL`,
                COUNT(*) AS `Total general`
            FROM z_posiciones
            WHERE jefe_rh IS NOT NULL AND jefe_rh != ''
            GROUP BY jefe_rh
            ORDER BY `Total general` DESC;
        """
        
        df_reporte = pd.read_sql(query, conexion)
        conexion.close()
        
        if not df_reporte.empty:
            # Calcular fila de Totales Generales de manera dinámica
            totales = {
                'Jefe RH': 'Total general',
                'PLANTA OCUPADA': df_reporte['PLANTA OCUPADA'].sum(),
                'PLANTA VACANTE': df_reporte['PLANTA VACANTE'].sum(),
                'TOTAL PLANTA': df_reporte['TOTAL PLANTA'].sum(),
                'EVENTUAL OCUPADA': df_reporte['EVENTUAL OCUPADA'].sum(),
                'EVENTUAL VACANTE': df_reporte['EVENTUAL VACANTE'].sum(),
                'TOTAL EVENTUAL': df_reporte['TOTAL EVENTUAL'].sum(),
                'Total general': df_reporte['Total general'].sum()
            }
            
            df_final = pd.concat([df_reporte, pd.DataFrame([totales])], ignore_index=True)
            
            # --- KPIs Ejecutivos en la parte superior ---
            t_planta = totales['TOTAL PLANTA']
            t_eventual = totales['TOTAL EVENTUAL']
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Estructura Planta", f"{t_planta:,}", f"{totales['PLANTA VACANTE']} vacantes", delta_color="inverse")
            kpi2.metric("Total Estructura Eventual", f"{t_eventual:,}", f"{totales['EVENTUAL VACANTE']} vacantes", delta_color="inverse")
            kpi3.metric("Universo Total Vigilado", f"{totales['Total general']:,}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Formatear la visualización de la tabla
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Botón de descarga para los analistas
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Cobertura por Jefe en CSV",
                data=csv,
                file_name="Reporte_Cobertura_Jefe_RH.csv",
                mime="text/csv",
            )
        else:
            st.warning("⚠️ No se encontraron registros con Jefes de RH asignados para generar la matriz.")
            
    except Exception as e:
        st.error(f"🚨 Error al generar la matriz de Jefes de RH: {e}")