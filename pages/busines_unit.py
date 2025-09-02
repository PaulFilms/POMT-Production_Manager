from typing import TYPE_CHECKING
import pandas as pd
from mysqlite import SQL

import streamlit as st
from functions import *

session_state_start()

## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________


DB = SQL(path_db=path_db)
# if not 'bu' in st.session_state: st.session_state.bu = 1





## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

# st.title('BUSINESS UNIT')

# st.selectbox(
#     'SELECT BUSINESS UNIT',
#     options=get_business_units(st.session_state.bu), 
#     accept_new_options=False, width='stretch'
# )

st_df = st.dataframe(
    get_business_units(st.session_state.bu),
    width='stretch', hide_index=True, on_select='rerun', selection_mode='single-row'
)

if len(st_df.selection['rows']) == 1:
    iloc = st_df.selection['rows']

    tab_usuarios, tab_pedidos,  = st.tabs(["USUARIOS", "PEDIDOS"])

    with tab_usuarios:
        pass

    with tab_pedidos:
        st.radio('')

