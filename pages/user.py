import streamlit as st
from functions import *

col_estado, col_bunit = st.columns(2)

tab_pedido, = st.tabs(['PEDIDOS'])

with tab_pedido:
    col_estado, col_bunit = st.columns(2)
    col_estado.radio('ESTADO', options=['TODO', 'PENDIENTE', 'COMPLETO'], index=1, label_visibility='visible', horizontal=True, width='stretch')
    col_bunit.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
