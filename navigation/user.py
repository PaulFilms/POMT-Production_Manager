import streamlit as st
from functions import *
from frontend import *


session_state_start()

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

st.write(f'Hello {st.session_state.login.nombre} 🙋')

# col_estado, col_bunit = st.columns(2)

## DATA

df_pedidos = get_pedidos(st.session_state.pedidos)
df_pedidos = df_pedidos[df_pedidos['planificador']==st.session_state.login.id]
df_hitos = get_hitos()
df_hitos = df_hitos[
    df_hitos['responsable']==st.session_state.login.id
]
df_acciones = get_acciones()
df_acciones = df_acciones[
    (df_acciones['planificador']==st.session_state.login.id) | 
    (df_acciones['responsable']==st.session_state.login.id)
]


## KPIs

# with st.container(border=True):
col_kpi_gpi, col_kpi_hitos, col_kpi_pdca = st.columns(3)

col_kpi_gpi.metric(
    'GPIs', border=True,
    value=len(df_pedidos)
)
col_kpi_hitos.metric(
    'Hitos', border=True,
    value=len(df_hitos)
)
col_kpi_pdca.metric(
    'PDCA', border=True,
    value=len(df_acciones)
)

UI.style_metric_cards(border_left_color="#ff9800")



## TABLES

tab_pedidos, tab_hitos, tab_acciones = st.tabs(['GPIs', 'HITOS', 'PDCA'])

with tab_pedidos:
    st.dataframe(
        df_pedidos[Pedidos.columns],
        hide_index=True
    )

with tab_hitos:
    st.dataframe(
        df_hitos[Hitos.columns],
        hide_index=True
    )

with tab_acciones:
    st.dataframe(
        df_acciones[Acciones.columns],
        hide_index=True
    )