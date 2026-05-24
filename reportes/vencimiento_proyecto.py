# reportes/vencimiento_proyecto.py
import streamlit as st
import pandas as pd
from database import obtener_conexion

def mostrar_reporte():
    st.subheader("📋 Tabla de Vencimiento de Posiciones Por Proyecto")
    st.markdown("Muestra el balance actual de posiciones ocupadas vs vacantes agrupadas por Unidad de Negocio (Complejo).")
    
    try:
        conexion = obtener_conexion()
        query = """
            SELECT 
                IFNULL(Complejo, 'NO ASIGNADO') AS UNIDAD,
                SUM(CASE WHEN Estado = 'OCUPADA' THEN 1 ELSE 0 END) AS OCUPADA,
                SUM(CASE WHEN Estado = 'VACANTE' THEN 1 ELSE 0 END) AS VACANTE,
                COUNT(*) AS `Total general`
            FROM posiciones
            GROUP BY Complejo
            ORDER BY `Total general` DESC;
        """
        df_reporte = pd.read_sql(query, conexion)
        conexion.close()
        
        if not df_reporte.empty:
            df_reporte['% Cobertura'] = (df_reporte['OCUPADA'] / df_reporte['Total general']) * 100
            
            total_ocupada = df_reporte['OCUPADA'].sum()
            total_vacante = df_reporte['VACANTE'].sum()
            total_general = df_reporte['Total general'].sum()
            cobertura_global = (total_ocupada / total_general) * 100 if total_general > 0 else 0
            
            fila_total = pd.DataFrame([{
                'UNIDAD': 'Total general',
                'OCUPADA': total_ocupada,
                'VACANTE': total_vacante,
                'Total general': total_general,
                '% Cobertura': cobertura_global
            }])
            
            df_final = pd.concat([df_reporte, fila_total], ignore_index=True)
            df_final['% Cobertura'] = df_final['% Cobertura'].map('{:.1f}%'.format)
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Posiciones Totales", f"{total_general:,}")
            kpi2.metric("Plantilla Activa (Ocupada)", f"{total_ocupada:,}", delta=f"-{total_vacante} Vacantes", delta_color="inverse")
            kpi3.metric("Cobertura Global", f"{cobertura_global:.1f}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar este reporte en CSV",
                data=csv,
                file_name="Reporte_Vencimiento_Posiciones_Proyecto.csv",
                mime="text/csv",
            )
        else:
            st.warning("⚠️ No hay datos disponibles en la tabla 'posiciones' para generar el reporte.")
            
    except Exception as e:
        st.error(f"🚨 Error al generar el reporte desde MySQL: {e}")