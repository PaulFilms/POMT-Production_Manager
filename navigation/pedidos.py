'''
## ⚠️ WARNINGS:
- send_mail / funcion incompleta
- update_xlsx / Carga por jupyter
- timeline / Formato no normalizado
'''
import tempfile, json
from time import sleep
from enum import Enum
from dataclasses import dataclass, asdict, fields
from datetime import datetime, date
from typing import Any, List, Dict
import pandas as pd
# from pyreports.xlsx import *

import streamlit as st
# from streamlit_timeline import timeline # https://pypi.org/project/streamlit-timeline/
from frontend import *
from functions import *

session_state_start()


## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________


# class Acciones:


#     def tbl_acciones(hito_id: int) -> int:
#         col_options, col_filtros, col_vista = st.columns(3)

#         with col_options.expander('OPCIONES', icon='🔧', width='stretch'):
#             st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Acciones.new, kwargs={'hito_id': hito_id}, key='accion_options_new')
#             edit_holder = st.empty()
#             # templates = get_templates() # BUG: cache?
#             # template = st.selectbox('TEMPLATE', options=templates, index=None)
#             # if template:
#             #     st.button('TEMPLATE', width='stretch', icon=':material/add_box:', on_click=Hitos.template, kwargs={'pedido_id': pedido_id, 'template': template})
#             row_height = st.slider(label='ALTO FILA', label_visibility='visible', min_value=40, max_value=300, value=100)

#         with col_filtros.expander('FILTROS', icon='🔍', width='stretch'):
#             fltr_str = st.text_input('fltr_acciones_str', label_visibility='collapsed', icon='🔍')
#             # col_r, col_y, col_g = st.columns(3)
#             filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
#             # col_r.checkbox('🟥', value=1) # 🟥🟨🟩
#             # col_y.checkbox('🟨', value=1) # 🟥🟨🟩
#             # col_g.checkbox('🟩', value=1) # 🟥🟨🟩
#             # st.write('ESTADO')
#             # col_e1, col_e2, col_e3, col_e4 = st.columns(4)
#             # # filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
#             # col_e1.checkbox('⏳', value=1) # ⏳🔍⏫✅
#             # col_e2.checkbox('🔍', value=1) 
#             # col_e3.checkbox('⏫', value=1)
#             # col_e4.checkbox('✅', value=0)
#             filter_causa = st.selectbox('CAUSA', options=[c.value for c in Causas], index=None, accept_new_options=False)

#         # vistas: list = [
#         #     'GANTT', 
#         #     'TABLA', 
#         #     # 'CALENDARIO'
#         # ]
#         # vista = col_vista.selectbox('VISTA', options=vistas, index=0, accept_new_options=False, label_visibility='collapsed')
        
#         ## DATAFRAME
#         df = get_acciones(hito_id)

#         ## TABLA
#         columns = ['#', 'causa', 'info', 'accion', 'fecha_accion', 'fecha_req', 'planificador', 'responsable', 'estado']

#         # st.slider(label='con altura', min_value=100, max_value=500, value=150, label_visibility='collapsed', width='')
#         columns_config = {
#             '#': st.column_config.Column('#', width='small'),
#             'causa': st.column_config.Column('CAUSA', width='small'),
#             'info': st.column_config.Column('info', width='medium'),
#             'accion': st.column_config.Column('acción', width='medium'),
#             'fecha_accion': st.column_config.DatetimeColumn('fecha_accion', format="YYYY-MM-DD", width='small'),
#             'fecha_req': st.column_config.DatetimeColumn('fecha_req', format="YYYY-MM-DD", width='small'),
#             'estado': st.column_config.Column('estado', width='small'),
#         }
        
#         tbl = st.dataframe(
#             df[columns],
#             hide_index=True,
#             width='stretch',
#             selection_mode='single-row',
#             on_select='rerun',
#             # height=tbl_height,
#             row_height=row_height,
#             column_config=columns_config
#         )
#         tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None


## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

## PEDIDOS

pedido: ORM.Pedido = Pedidos.tbl()
# hito: ORM.Hito = None
# accion: ORM.Accion = None

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
        accion = Acciones.tbl(pedido_id=pedido.id, hito_id=hito.id if hito else None, f_key='by_gpi')
        if accion:
            pass
        # Acciones.tbl_acciones(hito.id)

    #         with tab_hito_log:
    #             modificaciones = hito.DB.get('modificaciones', None)
    #             if modificaciones:
    #                 for mod in modificaciones:
    #                     # st.write(mod)
    #                     fecha = mod.get('fecha', None)
    #                     info = mod.get('info', None)
    #                     user = mod.get('user', None)
    #                     title = f'{fecha} / {user}'

    #                     st.write(title)
    #                     with st.container(border=True):
    #                         st.caption(info)
    #                         data = mod.get('data', None)
    #                         if data:
    #                             rows = []
    #                             for key, values in data.items():
    #                                 rows.append({
    #                                     "PARAMETRO": key,
    #                                     "ANTERIOR": str(values.get("old")),
    #                                     "NUEVO": str(values.get("new"))
    #                                 })
    #                             df = pd.DataFrame(rows)
    #                             st.dataframe(pd.DataFrame(rows), hide_index=True)

    # ## PDCAs
    # # with tab_acciones:
    # #     Acciones.tbl_acciones(pedido.id)

    # ## GPI Log
    # with tab_gpilog:
    #     # st.write(pedido.DB)
    #     modificaciones = pedido.DB.get('modificaciones', None)
    #     if modificaciones:
    #         for mod in modificaciones:
    #             # st.write(mod)
    #             fecha = mod.get('fecha', None)
    #             info = mod.get('info', None)
    #             user = mod.get('user', None)
    #             title = f'{fecha} / {user}'

    #             st.write(title)
    #             with st.container(border=True):
    #                 st.caption(info)
    #                 data = mod.get('data', None)
    #                 if data:
    #                     rows = []
    #                     for key, values in data.items():
    #                         rows.append({
    #                             "PARAMETRO": key,
    #                             "ANTERIOR": str(values.get("old")),
    #                             "NUEVO": str(values.get("new"))
    #                         })
    #                     df = pd.DataFrame(rows)
    #                     st.dataframe(pd.DataFrame(rows), hide_index=True)

