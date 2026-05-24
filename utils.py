# utils.py
import pandas as pd
from datetime import datetime

def transformar_fecha(val):
    """Convierte formatos de fecha mixtos de Excel al estándar de MySQL YYYY-MM-DD."""
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NaN', 'None']:
        return None
    
    val_str = str(val).strip()
    if '31/12/9999' in val_str or '9999-12-31' in val_str:
        return '9999-12-31'
        
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(val_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None

def limpiar_entero(val):
    """Asegura que valores numéricos vacíos o flotantes se traten como Enteros limpios."""
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NaN', 'None']:
        return None
    try:
        return int(float(val))
    except ValueError:
        return None

def limpiar_texto(val):
    """Elimina espacios en blanco y convierte celdas vacías/con basura en None (NULL)."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s not in ['', 'nan', 'NaN', 'N/A', 'None'] else None