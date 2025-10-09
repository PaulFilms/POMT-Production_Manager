'''
## ⚠️ WARNINGS:
- send_mail / funcion incompleta
'''
import streamlit as st
# from streamlit_timeline import timeline # https://pypi.org/project/streamlit-timeline/
from frontend import *
from functions import *

session_state_start()


## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

## PEDIDOS

pedido: ORM.Pedido = Pedidos.tbl()


if pedido != None:

    ## HITOS / PDCA / EM
    st.container(border=False, height=20) # Separador
    tab_hitos, tab_pdca, tab_manufact, tab_caminos = st.tabs(['HITOS', 'PDCA (All)', '⚠️ ENTREGA MANUFACTURING', 'PLAN DE ENTREGAS'])

    ## HITOS
    with tab_hitos:
        hito = Hitos.tbl(pedido.id)
        if hito:
            st.container(border=False, height=20) # Separador
            st.write('PDCA (Hito)')
            Acciones.tbl(pedido_id=pedido.id, hito_id=hito.id, f_key='by_hito')

    with tab_pdca: ## ALL PDCA
        accion = Acciones.tbl(pedido_id=pedido.id, hito_id=None, f_key='by_gpi')
        if accion:
            pass
        # Acciones.tbl_acciones(hito.id)
    
    with tab_manufact:
        Caminos.tbl(pedido.id)

