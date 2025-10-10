'''
## ⚠️ WARNINGS:
- send_mail / funcion incompleta
'''
import streamlit as st
# from streamlit_timeline import timeline # https://pypi.org/project/streamlit-timeline/
from frontend import *
from functions import *

session_state_start()


## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets/logo_extend.svg', size='large')

## PEDIDOS

pedido: ORM.Pedido = Pedidos.tbl()


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
        accion = Acciones.tbl(pedido_id=pedido.id, hito_id=None, f_key='by_gpi')
        if accion:
            pass
        # Acciones.tbl_acciones(hito.id)
        st.write('Agregar Acción por lotes')
        column_config = {
            'causa': st.column_config.SelectboxColumn('CAUSA', options=Causas.get_values(), width='medium'),
            'alarma': st.column_config.SelectboxColumn('ALARMA', options=Alarmas.colors(), width=None),
            'info': st.column_config.TextColumn('INFORMACIÓN', width=None),
            'accion': st.column_config.TextColumn('ACCIÓN', width=None),
            'departamento': st.column_config.SelectboxColumn('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].to_list(), width=None),
            'responsable': st.column_config.SelectboxColumn('RESPONSABLE', options=get_usuarios(st.session_state.usuarios)['id'].to_list(), width=None),
            'fecha_req': st.column_config.DatetimeColumn('FECHA REQUERIDA', format='YYYY-MM-DD', width=None),
        }
        df_acciones_new = st.data_editor(
            pd.DataFrame(columns=column_config.keys()),
            column_config=column_config,
            hide_index=True,
            key=f'new_accion_{pedido.id}',
            width='stretch',
            num_rows='dynamic',
            row_height=40
            # disabled=not (st.session_state['user'] and st.session_state['user'].departamento in ['PPD', 'CALIDAD']),
            # on_change=Acciones.add,
            # args=(pedido.id,),
            # kwargs={'hito_id': None, 'f_key': f'new_accion_{pedido.id}'},
        )

        if df_acciones_new.shape[0] > 0:
            st.button('AÑADIR ACCIONES', icon='➕')
    
    with tab_manufact:
        Caminos.tbl(pedido.id)

