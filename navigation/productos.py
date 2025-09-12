
import streamlit as st
from functions import *
import pandas as pd

session_state_start()

columns = ['id', 'info', 'sap_id']

@st.dialog('NUEVO PRODUCTO', width='medium')
def add_producto():
    info = st.text_area('DESCRIPCIÓN', value=None, height=1)
    empresa = st.selectbox('FABRICANTE', options=['INDRA'], label_visibility='visible', accept_new_options=False, index=None)
    url = st.text_input('URL', icon='🌐')

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

col_tbl_opctions, col_tbl_new, col_tbl_filter = st.columns(3)

with col_tbl_opctions.popover('TABLE OPTIONS', icon='🔧', width='stretch'):
    df_height = st.slider(label='HEIGHT', label_visibility='visible', min_value=200, max_value=1000)
df_filter_str = col_tbl_filter.text_input('FILTER', label_visibility='collapsed', icon='🔍')

col_tbl_new.button('AÑADIR PRODUCTO', width='stretch', icon='➕', on_click=add_producto)# : add_producto()

df = get_productos()
df['DB'] = df['DB'].apply(safe_json_loads)

## FILTERS
df_filtered1 = df[columns]
if df_filter_str and df_filter_str != '':
    mask = df_filtered1.select_dtypes(include=['object']).apply(
            lambda col: col.str.contains(df_filter_str, na=False)
        ).any(axis=1)
    df_filtered2 = df_filtered1[mask]
else: df_filtered2 = df_filtered1

st_df = st.dataframe(
    df_filtered2,
    width='stretch', hide_index=True, selection_mode='single-row', on_select='rerun',
    height=df_height
)

df_iloc = st_df.selection['rows'][0] if st_df.selection['rows'] != [] else None

if df_iloc is not None:
    st.write('SUB-PRODUCTS:')
    producto_id = df['id'].iloc[df_iloc]
    producto_db = df['DB'].iloc[df_iloc]
    sub_products = producto_db.get('productos_id')

    st.write(sub_products)


# Lista de semanas
semanas = list(range(1, 13))  # Puedes ajustar a 52 semanas si quieres

# Lista de hitos
hitos = ['Inicio Proyecto', 'Fase de Diseño', 'Desarrollo', 'Pruebas', 'Entrega']

# Crear DataFrame vacío
df = pd.DataFrame('', index=hitos, columns=semanas)

# Definir en qué semanas ocurre cada hito (rellenar con "X" o algo similar)
timeline_data = {
    'Inicio Proyecto': [1, 2],
    'Fase de Diseño': [3, 4, 5],
    'Desarrollo': [6, 7, 8],
    'Pruebas': [9, 10],
    'Entrega': [11, 12]
}

# Rellenar el DataFrame con marca para cada semana activa
for hito, semanas_activas in timeline_data.items():
    for semana in semanas_activas:
        df.at[hito, semana] = '●'

# Función para aplicar color a las celdas con '●'
def color_cells(val):
    color = 'background-color: lightgreen' if val == '●' else ''
    return color

# Mostrar el timeline estilizado
# st.title("Timeline del Proyecto")

st.dataframe(
    df.style.map(color_cells), 
    # height=300, 
    width='stretch'
)

semanas = [1, 2, 3, 4, 5, 6, 7, 8]

