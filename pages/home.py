import streamlit as st
from functions import *


## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

session_state_start()

st.logo(r'assets\logo_extend.svg', size='large')

st.title('PPI PROJECT')
st.divider()
st.caption('''
Este es el proyecto de optimización de datos del PPI
''')

st.image(r'assets\schema.png')