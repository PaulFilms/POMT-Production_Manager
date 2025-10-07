import streamlit as st
from app import session_state_start
from functions import *
from estilos import *

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

session_state_start()

title_container = st.container(
    horizontal=True
)
card_container = st.container(
    horizontal=True
)

st.logo(r'assets\logo_extend.svg', size='large')

with title_container:
    st.subheader("Planes de Entrega")
    st.text("Proyectos PPI", width = 100)

with card_container:
    c1, c2, c3 = st.columns(3)
    c1.metric(label="Proyectos Activos", value = 67, delta = 9)
    c2.metric(label="Codigos Retrasados", value = 287, delta = 34)
    c3.metric(label="Proyectos en tiempo", value = 14, delta = -3)

style_metric_cards()






