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
#         col_alert, col_bu, col_user = st.columns(3)
#         alarma          = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, label_visibility='visible', width='content', horizontal=True)
#         departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
#         responsable      = col_user.selectbox('RESPONSABLE', options=get_usuarios_by_dept(departamento, st.session_state.usuarios, st.session_state.departamentos), index=None, accept_new_options=False)

#         nombre = st.text_area('NOMBRE', value=None)
#         grupo = st.text_input('GRUPO')
#         fecha_req = st.date_input('FECHA REQUERIDA', value=None, min_value=datetime(2024,1,1), format='YYYY-MM-DD')
#         fecha_plan = st.date_input('FECHA PLANIFICADA', value=None, min_value=datetime(2024,1,1), format='YYYY-MM-DD')


#         if st.button('AÑADIR HITO', icon='🔄️', width='stretch'):
#             if not grupo or not nombre or not fecha_req or not fecha_plan or not responsable:
#                 st.warning("RELLENA TODOS LOS DATOS", icon='⚠️')
#             else:
#                 mod = Modificacion(
#                     fecha=datetime.now(),
#                     info='Creación de hito',
#                     data=None,
#                     user=st.session_state.login.id
#                 )
#                 hito = ORM.Hito(
#                     id=None,
#                     pedido_id=pedido_id,
#                     grupo=grupo,
#                     nombre=nombre,
#                     fecha_req=fecha_req,
#                     fecha_plan=fecha_plan,
#                     responsable=responsable,
#                     alarma=Alarmas.get_int(alarma),
#                     estado=1,
#                     info=None,
#                     DB={
#                         'modificaciones': [mod.to_dict()],
#                     },
#                     firm=get_firm()
#                 )
#                 # values = {
#                 #     'pedido_id': pedido_id,
#                 #     'grupo': grupo,
#                 #     'nombre': nombre,
#                 #     'fecha_ini': fecha_ini.strftime(r'%Y-%m-%d'),
#                 #     'fecha_fin': fecha_fin.strftime(r'%Y-%m-%d'),
#                 #     'responsable': responsable,
#                 #     'alarma': alarma,
#                 #     'estado': 1,
#                 #     'info': info,
#                 #     'firm': get_firm(),
#                 # }
#                 DB.insert('hitos', values=hito.to_sql())
#                 st.session_state.hitos += 1
#                 st.rerun()

#     @st.dialog('ℹ️ INFO HITO', width='medium')
#     def edit(hito: 'ORM.Hito') -> None:
#         st.write(hito.pedido_id, '/', hito.grupo)
#         st.write(hito.nombre)

#         alarma_indx = pedido.alarma - 1 if isinstance(hito.alarma, int) else None
#         alarma_color = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
#         alarma = Alarmas.get_int(alarma_color)
#         # estado_indx = hito.estado - 1 if isinstance(hito.estado, int) else None
#         estado_icon = st.radio('ESTADO', options=Estados.get_estados_icon(), index=hito.estado, horizontal=True)
#         estado = Estados.get_id(estado_icon)
#         fecha_req = st.date_input('FECHA REQUERIDA', value=hito.fecha_req, format='YYYY-MM-DD')
#         fecha_plan = st.date_input('FECHA PLANIFICADA', value=hito.fecha_plan, format='YYYY-MM-DD')
#         # info = st.text_area('INFO / DESCRIPCIÓN', value=hito.info, height=1)
#         btn_mod = st.button('MODIFICAR', width='stretch')
#         info_mod = st.text_area('INFO MODIFICACIÓN', height=1)
#         mail = st.checkbox('ENVIAR MAIL')

#         if btn_mod:
#             # if fecha_fin < fecha_ini:
#             #     st.warning("LA FECHA DE FIN ES MENOR QUE LA FECHA DE INICIO", icon='⚠️')
#             if not info_mod:
#                 st.warning("INDICA EL MOTIVO DE LA MODIFICACIÓN", icon='⚠️')
#             else:
#                 fecha_req = fecha_req.strftime(r'%Y-%m-%d')
#                 fecha_plan = fecha_plan.strftime(r'%Y-%m-%d')
#                 mod = Modificacion(
#                     fecha=datetime.now(),
#                     info=info_mod,
#                     data=dict(),
#                     user=st.session_state.login.id
#                 )
#                 args = {
#                     'fecha_req': fecha_req, 
#                     'fecha_plan': fecha_plan, 
#                     'alarma': alarma, 
#                     'estado': estado, 
#                     # 'info': info,
#                 }
#                 values = dict()
#                 for k, v in args.items():
#                     old = getattr(hito, k)
#                     new = v
#                     if isinstance(old, datetime): old = old.strftime(r'%Y-%m-%d')
#                     if isinstance(new, datetime): new = new.strftime(r'%Y-%m-%d')
#                     if new != old:
#                         mod.data[k] = {
#                             'old': old,
#                             'new': new,
#                         }
#                         values[k] = new
                
#                 values['firm'] = get_firm()
#                 values['DB'] = hito.DB
#                 if not values['DB'].get('modificaciones'):
#                     values['DB']['modificaciones'] = []
#                 values['DB']['modificaciones'].append(mod.to_dict())
#                 values['DB'] = json.dumps(values['DB'])

#                 if mail:
#                     send_mail()
                
#                 DB.update('hitos', values=values, where={'id': hito.id})
#                 st.session_state.hitos += 1
#                 st.rerun()

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

class Acciones:

    @st.dialog('➕ NUEVA ACCIÓN', width='medium')
    def new(hito_id: int) -> None:
        causa = st.selectbox('CAUSA', options=Causas.get_values(), index=None, accept_new_options=False)
        causa_id = Causas.get_ids()[Causas.get_values().index(causa)] if causa else None
        fecha_req = st.date_input('FECHA REQUERIDA', value=None, format='YYYY-MM-DD')
        info = st.text_area('INFO / DESCRIPCIÓN', value=None, height=1)
        accion_info = st.text_area('ACCIÓN', value=None, height=1)
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        responsable = st.selectbox('RESPONSABLE', options=usuarios, index=None, accept_new_options=False)
        alarma = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, horizontal=True)
        alarma_mod = Alarmas.get_int(alarma)

        btn = st.button('AÑADIR ACCIÓN', width='stretch', icon='⚠️')
        mail = st.checkbox('ENVIAR MAIL')
    
        if btn:
            if not causa_id or not info or not accion_info or not responsable or not fecha_req or not alarma_mod:
                st.warning("RELLENA LOS DATOS DE LA ACCIÓN", icon='⚠️')
            else:
                mod = Modificacion(
                    fecha=datetime.now(),
                    info='Creación de acción',
                    data=None,
                    user=st.session_state.login.id
                )

                accion = ORM.Accion(
                    id=None,
                    hito_id=hito_id,
                    causa=causa_id,
                    alarma=alarma_mod,
                    info=info,
                    accion=accion_info,
                    planificador=st.session_state.login.id,
                    responsable=responsable,
                    fecha_accion=datetime.now(),
                    fecha_req=fecha_req,
                    estado=1,
                    DB={
                        'modificaciones': [mod.to_dict()],
                        'xlsx': None,
                    },
                    firm=get_firm(),
                )

                DB.insert('acciones', values=accion.to_sql())
                st.session_state.acciones += 1
                if mail:
                    send_mail()
                st.rerun()

    @st.dialog('DETALLE ACCIÓN', width='medium')
    def detalle_accion(x):
        st.write(x)

    def tbl_acciones(hito_id: int) -> int:
        col_options, col_filtros, col_vista = st.columns(3)

        with col_options.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Acciones.new, kwargs={'hito_id': hito_id}, key='accion_options_new')
            edit_holder = st.empty()
            # templates = get_templates() # BUG: cache?
            # template = st.selectbox('TEMPLATE', options=templates, index=None)
            # if template:
            #     st.button('TEMPLATE', width='stretch', icon=':material/add_box:', on_click=Hitos.template, kwargs={'pedido_id': pedido_id, 'template': template})
            row_height = st.slider(label='ALTO FILA', label_visibility='visible', min_value=40, max_value=300, value=100)

        with col_filtros.expander('FILTROS', icon='🔍', width='stretch'):
            fltr_str = st.text_input('fltr_acciones_str', label_visibility='collapsed', icon='🔍')
            # col_r, col_y, col_g = st.columns(3)
            filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
            # col_r.checkbox('🟥', value=1) # 🟥🟨🟩
            # col_y.checkbox('🟨', value=1) # 🟥🟨🟩
            # col_g.checkbox('🟩', value=1) # 🟥🟨🟩
            # st.write('ESTADO')
            # col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            # # filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
            # col_e1.checkbox('⏳', value=1) # ⏳🔍⏫✅
            # col_e2.checkbox('🔍', value=1) 
            # col_e3.checkbox('⏫', value=1)
            # col_e4.checkbox('✅', value=0)
            filter_causa = st.selectbox('CAUSA', options=[c.value for c in Causas], index=None, accept_new_options=False)

        # vistas: list = [
        #     'GANTT', 
        #     'TABLA', 
        #     # 'CALENDARIO'
        # ]
        # vista = col_vista.selectbox('VISTA', options=vistas, index=0, accept_new_options=False, label_visibility='collapsed')
        
        ## DATAFRAME
        df = get_acciones(hito_id)

        ## TABLA
        columns = ['#', 'causa', 'info', 'accion', 'fecha_accion', 'fecha_req', 'planificador', 'responsable', 'estado']

        # st.slider(label='con altura', min_value=100, max_value=500, value=150, label_visibility='collapsed', width='')
        columns_config = {
            '#': st.column_config.Column('#', width='small'),
            'causa': st.column_config.Column('CAUSA', width='small'),
            'info': st.column_config.Column('info', width='medium'),
            'accion': st.column_config.Column('acción', width='medium'),
            'fecha_accion': st.column_config.DatetimeColumn('fecha_accion', format="YYYY-MM-DD", width='small'),
            'fecha_req': st.column_config.DatetimeColumn('fecha_req', format="YYYY-MM-DD", width='small'),
            'estado': st.column_config.Column('estado', width='small'),
        }
        
        tbl = st.dataframe(
            df[columns],
            hide_index=True,
            width='stretch',
            selection_mode='single-row',
            on_select='rerun',
            # height=tbl_height,
            row_height=row_height,
            column_config=columns_config
        )
        tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None


## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

## PEDIDOS

pedido: ORM.Pedido = Pedidos.tbl()

if pedido != None:

    ## HITOS / PDCA / EM
    st.container(border=False, height=20) # Separador
    tab_hitos, tab_pdca, tab_manufact = st.tabs(['HITOS', 'PDCA', '⚠️ MANUF.'])

    ## HITOS
    with tab_hitos:
        hito = Hitos.tbl(pedido.id)
    #     # df_hitos = get_hitos(pedido.id)
    #     # hito_loc = Hitos.tbl_hitos(df_hitos)

    #     hito: Hitos.Hito = Hitos.tbl_hitos(pedido.id)
    #     # st.write(hito_loc)

    #     if hito and hito.grupo != 'GPI':
    #         st.container(border=False, height=20) # Separador
    #         tab_hito_pdca, tab_hito_log = st.tabs(['PDCA', 'Log'])

    with tab_pdca:
        df_acciones = get_acciones(st.session_state.acciones)
        df_acciones = df_acciones[df_acciones['pedido_id']==pedido.id]
        st.write(df_acciones)
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

