# reportes/justificacion_eventuales.py
import streamlit as st
import pandas as pd
from database import obtener_conexion

def mostrar_reporte():
    st.subheader("📋 Desglose de Justificaciones de Posiciones Eventuales")
    st.markdown("Analiza la distribución de las posiciones eventuales según su motivo de apertura por cada Unidad de Negocio.")
    
    try:
        conexion = obtener_conexion()
        
        # SQL Corregido: Usamos las columnas reales de la base de datos (en minúsculas y con guiones bajos)
        # y asignamos los alias (AS) con los nombres ejecutivos que requieres.
        query = """
            SELECT 
                IFNULL(complejo, 'NO ASIGNADO') AS `Unidad de Negocio`,
                SUM(CASE WHEN tipo_de_just LIKE '%Incapacidad%' THEN 1 ELSE 0 END) AS `Incapacidad (#)`,
                SUM(CASE WHEN tipo_de_just LIKE '%Capacitación%' OR tipo_de_just LIKE '%Global Talent%' OR tipo_de_just LIKE '%Onboarding%' THEN 1 ELSE 0 END) AS `Onboarding (#)`,
                SUM(CASE WHEN tipo_de_just LIKE '%Proyecto%' THEN 1 ELSE 0 END) AS `Proyecto (#)`,
                SUM(CASE WHEN tipo_de_just NOT LIKE '%Incapacidad%' AND tipo_de_just NOT LIKE '%Capacitación%' AND tipo_de_just NOT LIKE '%Global Talent%' AND tipo_de_just NOT LIKE '%Onboarding%' AND tipo_de_just NOT LIKE '%Proyecto%' THEN 1 ELSE 0 END) AS `Otros (#)`,
                SUM(CASE WHEN clasific = 'EVENTUAL' THEN 1 ELSE 0 END) AS `Total General (#)`
            FROM posiciones
            WHERE clasific = 'EVENTUAL'
            GROUP BY complejo
            ORDER BY `Total General (#)` DESC;
        """
        
        df_reporte = pd.read_sql(query, conexion)
        conexion.close()
        
        if not df_reporte.empty:
            # 1. Calcular Totales de las Columnas Numéricas
            total_incapacidad = df_reporte['Incapacidad (#)'].sum()
            total_onboarding = df_reporte['Onboarding (#)'].sum()
            total_proyecto = df_reporte['Proyecto (#)'].sum()
            total_otros = df_reporte['Otros (#)'].sum()
            total_universo = df_reporte['Total General (#)'].sum()
            
            # 2. Calcular los Porcentajes para cada fila de forma segura
            df_reporte['Incapacidad (%)'] = df_reporte.apply(lambda r: (r['Incapacidad (#)'] / r['Total General (#)'] * 100) if r['Total General (#)'] > 0 else 0, axis=1)
            df_reporte['Onboarding (%)'] = df_reporte.apply(lambda r: (r['Onboarding (#)'] / r['Total General (#)'] * 100) if r['Total General (#)'] > 0 else 0, axis=1)
            df_reporte['Proyecto (%)'] = df_reporte.apply(lambda r: (r['Proyecto (#)'] / r['Total General (#)'] * 100) if r['Total General (#)'] > 0 else 0, axis=1)
            df_reporte['Otros (%)'] = df_reporte.apply(lambda r: (r['Otros (#)'] / r['Total General (#)'] * 100) if r['Total General (#)'] > 0 else 0, axis=1)
            df_reporte['Total General (%)'] = 100.0
            
            # 3. Construir e integrar el renglón final de Totales Generales
            fila_totales = {
                'Unidad de Negocio': 'Total general',
                'Incapacidad (#)': total_incapacidad,
                'Onboarding (#)': total_onboarding,
                'Proyecto (#)': total_proyecto,
                'Otros (#)': total_otros,
                'Total General (#)': total_universo,
                'Incapacidad (%)': (total_incapacidad / total_universo * 100) if total_universo > 0 else 0,
                'Onboarding (%)': (total_onboarding / total_universo * 100) if total_universo > 0 else 0,
                'Proyecto (%)': (total_proyecto / total_universo * 100) if total_universo > 0 else 0,
                'Otros (%)': (total_otros / total_universo * 100) if total_universo > 0 else 0,
                'Total General (%)': 100.0
            }
            
            df_final = pd.concat([df_reporte, pd.DataFrame([fila_totales])], ignore_index=True)
            
            # 4. Dar formato ejecutivo a las columnas de porcentaje
            columnas_pct = ['Incapacidad (%)', 'Onboarding (%)', 'Proyecto (%)', 'Otros (%)', 'Total General (%)']
            for col in columnas_pct:
                df_final[col] = df_final[col].map('{:.1f}%'.format)
                
            # Reordenar las columnas intercalando número y porcentaje
            columnas_ordenadas = [
                'Unidad de Negocio',
                'Incapacidad (#)', 'Incapacidad (%)',
                'Onboarding (#)', 'Onboarding (%)',
                'Proyecto (#)', 'Proyecto (%)',
                'Otros (#)', 'Otros (%)',
                'Total General (#)', 'Total General (%)'
            ]
            df_final = df_final[columnas_ordenadas]
            
            # --- KPIs Superiores del Reporte ---
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Eventuales Registrados", f"{total_universo:,}")
            k1.caption("Suma de plazas eventuales activas/vacantes")
            k2.metric("Plazas por Incapacidad", f"{total_incapacidad:,}", f"{(total_incapacidad / total_universo * 100):.1f}% del total")
            k3.metric("Plazas por Nuevos Proyectos", f"{total_proyecto:,}", f"{(total_proyecto / total_universo * 100):.1f}% del total")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Renderizar la tabla interactiva
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Botón de exportación masiva
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Desglose en CSV",
                data=csv,
                file_name="Reporte_Justificacion_Eventuales.csv",
                mime="text/csv",
            )
            
        else:
            st.warning("⚠️ No se encontraron registros categorizados como 'EVENTUAL' para procesar.")
            
    except Exception as e:
        st.error(f"🚨 Error al compilar el reporte de eventuales: {e}")