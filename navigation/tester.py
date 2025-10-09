import streamlit as st
from functions import *
from frontend import *
from st_aggrid import AgGrid, GridOptionsBuilder

df = get_pedidos()

for c in ['#', 'DB', 'firm']:
    del df[c]

for c in Causas:
    del df[c.name]

gb = GridOptionsBuilder.from_dataframe(df)

gb.configure_default_column(filter='agTextColumnFilter')  # Añade filtro de texto a todas las columnas

# Regla para cambiar color de fila
gb.configure_grid_options(
    getRowStyle="""function(params) { 
        if (params.data.alarma > 0) { 
            return {'background-color': '#f9d5d3'} 
        } 
    }"""
)

gridOptions = gb.build()

# Estilo CSS personalizado
custom_css = {
    ".ag-root": {
        "font-family": "Neo Sans",  # Puedes cambiar por Arial, Roboto, etc.
        "font-size": "14px"
    }
}

AgGrid(
    df,
    gridOptions=gridOptions,
    custom_css=custom_css,
    height='auto',
    theme='alpine'
)
