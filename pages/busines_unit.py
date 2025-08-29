import streamlit as st

st.title('BUSINESS UNIT')

st.warning('ISRA DAME TIEMPOOOOO', icon='⚠️')

bu = ['ALL', 'NAVAL', 'AEROSPACIO', '']

st.selectbox(
    'SELECT BUSINESS UNIT',
    options=bu, accept_new_options=False, width='stretch'
)

