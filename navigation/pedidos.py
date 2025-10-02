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

# class Hitos:

#     @st.dialog('➕ NUEVO HITO', width='medium')
#     def new(pedido_id: str) -> None:


#     @st.dialog('ℹ️ INFO HITO', width='medium')
#     def edit(hito: 'ORM.Hito') -> None:

#     def tbl_hitos(pedido_id: str) -> 'ORM.Hito':

#         col_hitos_options, col_hitos_filtros, col_hitos_vista = st.columns(3)

#         with col_hitos_options.expander('OPCIONES', icon='🔧', width='stretch'):
#             st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Hitos.new, kwargs={'pedido_id': pedido_id})
#             # st.button('EDITAR', width='stretch', icon=':material/edit_square:', disabled=opt_edit) # edit_square
#             edit_holder = st.empty()
#             # templates = get_templates() # BUG: cache?
#             # template = st.selectbox('TEMPLATE', options=templates, index=None)
#             # if template:
#             #     st.button('TEMPLATE', width='stretch', icon=':material/add_box:', on_click=Hitos.template, kwargs={'pedido_id': pedido_id, 'template': template})

#         with col_hitos_filtros.expander('FILTROS', icon='🔍', width='stretch'):
#             fltr_hitos_str = st.text_input('fltr_hitos_str', label_visibility='collapsed', icon='🔍')
#             st.write('ALERTAS')
#             col_r, col_y, col_g = st.columns(3)
#             # filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
#             col_r.checkbox('🟥', value=1) # 🟥🟨🟩
#             col_y.checkbox('🟨', value=1) # 🟥🟨🟩
#             col_g.checkbox('🟩', value=1) # 🟥🟨🟩
#             st.write('ESTADO')
#             col_e1, col_e2, col_e3, col_e4 = st.columns(4)
#             # filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
#             col_e1.checkbox('⏳', value=1) # ⏳🔍⏫✅
#             col_e2.checkbox('🔍', value=1) 
#             col_e3.checkbox('⏫', value=1)
#             col_e4.checkbox('✅', value=0)

#         vistas: list = [
#             'GANTT', 
#             'TABLA', 
#             # 'CALENDARIO'
#         ]
#         vista = col_hitos_vista.selectbox('VISTA', options=vistas, index=1, accept_new_options=False, label_visibility='collapsed')

#         ## DATAFRAME
#         df = get_hitos(pedido_id)
#         hito_nombre: str = None
#         # st.write(df)

#         if vista == 'GANTT':
#             data = [
#                 UI.Timeline(texto=pedido.id, grupo='GPI', fecha_ini=pedido.fecha_ini, fecha_fin=pedido.fecha_fin, color=pedido.alarma)
#             ]
#             ## Hitos
#             for idx, row in df.iterrows():
#                 tl = UI.Timeline(
#                     texto=row['nombre'],
#                     grupo=row['grupo'],
#                     fecha_ini=safe_datetime(row['fecha_req']),
#                     fecha_fin=safe_datetime(row['fecha_plan']),
#                     color=row['alarma']
#                 )
#                 # if not tl.fecha_ini or pd.isna(tl.fecha_ini): 
#                 #     tl.fecha_ini = fecha_ini
#                 # if not tl.fecha_fin or pd.isna(tl.fecha_fin): 
#                 #     tl.fecha_fin = fecha_fin
#                 data.append(tl)
#             df_gantt = pd.DataFrame(data)
#             # st.write(df_gantt)
#             with st.container(border=True): 
#                 tl_hitos = UI.my_timeline(df_gantt)
#                 # tl_hitos.selection
#                 # st.write(tl_hitos.selection['points'])
#                 if len(tl_hitos.selection['points']) == 1:
#                     hito_indx = tl_hitos.selection['points'][0]['curve_number']
#                     hito_nombre = data[hito_indx].texto
#                     # data[hito_indx].texto
#                     # st.write(data[hito_indx].texto)


#         if vista == 'TABLA':
#             data_holder = st.empty()
#             columns_hitos = ['nombre', 'grupo', 'responsable', '#', 'fecha_req', 'fecha_plan', 'Δ', 'estado']

#             # st.slider(label='con altura', min_value=100, max_value=500, value=150, label_visibility='collapsed', width='')
#             columns_config = {
#                 'nombre': st.column_config.Column('DESCRIPCIÓN HITO', width=None, pinned=True),
#                 'grupo': st.column_config.Column('GRUPO', width=None),
#                 '#': st.column_config.Column('#', width='small'),
#                 'estado': st.column_config.Column('#', width='small'),
#                 'fecha_req': st.column_config.DatetimeColumn('fecha_req', format="YYYY-MM-DD", width='small'),
#                 'fecha_plan': st.column_config.DatetimeColumn('fecha_plan', format="YYYY-MM-DD", width='small'),
#             }
#             # tbl_height = height_holder.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)
#             tbl = data_holder.dataframe(
#                 df[columns_hitos],
#                 hide_index=True,
#                 width='stretch',
#                 selection_mode='single-row',
#                 on_select='rerun',
#                 # height=tbl_height,
#                 row_height=40,
#                 column_config=columns_config
#             )
#             tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
#             hito_nombre = df['nombre'].iloc[tbl_iloc] if tbl_iloc != None else None

#         if vista == 'CALENDARIO':
#             pass
        
#         hito: ORM.Hito = None
        
#         if hito_nombre and hito_nombre != pedido_id:
#             hito_dict = df[df['nombre']==hito_nombre].iloc[0].to_dict()
#             hito = ORM.Hito.from_dict(hito_dict)
#             if hito.grupo != 'GPI':
#                 edit_holder.button('EDITAR', width='stretch', icon=':material/edit_square:', key='hito_options_edit', 
#                     on_click=Hitos.edit, kwargs={'hito': hito},
#                 )

#         return hito

# class Acciones:

#     @st.dialog('➕ NUEVA ACCIÓN', width='medium')
#     def new(hito_id: int) -> None:
#         causa = st.selectbox('CAUSA', options=Causas.get_values(), index=None, accept_new_options=False)
#         causa_id = Causas.get_ids()[Causas.get_values().index(causa)] if causa else None
#         fecha_req = st.date_input('FECHA REQUERIDA', value=None, format='YYYY-MM-DD')
#         info = st.text_area('INFO / DESCRIPCIÓN', value=None, height=1)
#         accion_info = st.text_area('ACCIÓN', value=None, height=1)
#         usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
#         responsable = st.selectbox('RESPONSABLE', options=usuarios, index=None, accept_new_options=False)
#         alarma = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, horizontal=True)
#         alarma_mod = Alarmas.get_int(alarma)

#         btn = st.button('AÑADIR ACCIÓN', width='stretch', icon='⚠️')
#         mail = st.checkbox('ENVIAR MAIL')
    
#         if btn:
#             if not causa_id or not info or not accion_info or not responsable or not fecha_req or not alarma_mod:
#                 st.warning("RELLENA LOS DATOS DE LA ACCIÓN", icon='⚠️')
#             else:
#                 mod = Modificacion(
#                     fecha=datetime.now(),
#                     info='Creación de acción',
#                     data=None,
#                     user=st.session_state.login.id
#                 )

#                 accion = ORM.Accion(
#                     id=None,
#                     hito_id=hito_id,
#                     causa=causa_id,
#                     alarma=alarma_mod,
#                     info=info,
#                     accion=accion_info,
#                     planificador=st.session_state.login.id,
#                     responsable=responsable,
#                     fecha_accion=datetime.now(),
#                     fecha_req=fecha_req,
#                     estado=1,
#                     DB={
#                         'modificaciones': [mod.to_dict()],
#                         'xlsx': None,
#                     },
#                     firm=get_firm(),
#                 )

#                 DB.insert('acciones', values=accion.to_sql())
#                 st.session_state.acciones += 1
#                 if mail:
#                     send_mail()
#                 st.rerun()

#     @st.dialog('DETALLE ACCIÓN', width='medium')
#     def detalle_accion(x):
#         st.write(x)

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

if pedido != None:

    ## HITOS / PDCA / EM
    st.container(border=False, height=20) # Separador
    tab_hitos, tab_pdca, tab_manufact = st.tabs(['HITOS', 'PDCA (All)', '⚠️ ENTREGA MANUFACTURING'])

    ## HITOS
    with tab_hitos:
        hito = Hitos.tbl(pedido.id)

    with tab_pdca:
        # df_acciones = get_acciones(pedido_id=pedido.id, hito_id=None)
        # df_acciones = df_acciones[df_acciones['pedido_id']==pedido.id]
        # st.write(df_acciones)
        Acciones.tbl(pedido.id)
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

