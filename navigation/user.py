from typing import TYPE_CHECKING

import streamlit as st
from functions import *

# estados = ['TODO']
# estados.extend([e.value[0] for e in Estados])
estados = [f'{e.value[0]} {e.name}' for e in Estados]
# estados_help = ' / '.join(estados_help)

if TYPE_CHECKING:
    from functions import Usuario
#     login: Usuario = st.session_state['login']
# else:
#     login = st.session_state['login']

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.write(f'Hello {st.session_state.login.nombre}')

# col_estado, col_bunit = st.columns(2)

tab_pedidos, tab_acciones = st.tabs(['GPIs', 'PDCA'])

with tab_pedidos:
    # col_estado, col_bunit = st.columns(2)
    # # col_estado.radio('ESTADO', options=estados, index=1, label_visibility='visible', horizontal=True, width='stretch', help=estados_help)
    # col_estado.selectbox('ESTADO', options=estados, index=None, label_visibility='visible', width='stretch',)
    # col_bunit.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )

    # df_pedidos = get_pedidos(st.session_state.pedidos)

    # tbl_pedidos = st.dataframe(
    #     df_pedidos,
    #     width='stretch', on_select='rerun', selection_mode='single-row'
    # )
    st.container(border=False, height=100)


with tab_acciones:
    pass