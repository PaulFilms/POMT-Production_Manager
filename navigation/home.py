import streamlit as st
from app import session_state_start
from functions import *


## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

session_state_start()

st.logo(r'assets/logo_extend.svg', size='large')

st.title('PRODUCTION MANAGER')
st.divider()

st.caption(
'''
Este proyecto está en fase de pruebas, puede tener errores de funcionamiento.

Para mas información, ponte en contacto con:

- Israel HS / ihernandez@indra.es
- Pablo GP / pgonzalezp@indra.es
- Luis GC / lgarridoc@indra.es
''')

# st.image(r'assets\schema.png')