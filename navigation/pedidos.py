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
from pyreports.xlsx import *
# from mysqlite import SQL

import streamlit as st
from streamlit_timeline import timeline # https://pypi.org/project/streamlit-timeline/
from app import session_state_start
from functions import *

session_state_start()


## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

class Templates:
    

class Pedidos:
    @dataclass
    class Pedido:
        id: str
        info: str
        bu_id: str
        planificador: str
        fecha_ini: datetime
        fecha_fin: datetime
        alarma: int = None
        contraseña: str = None
        DB: dict = None
        firm: str = None

        def to_dict(self):
            return asdict(self)
        
        def to_sql(self) -> Dict[str, Any]:
            '''
            Devuelve un diccionario de valores para INSERT / UPDATE 
            '''
            if isinstance(self.fecha_ini, datetime):
                self.fecha_ini = self.fecha_ini.strftime(r'%Y-%m-%d')
            if isinstance(self.fecha_fin, datetime):
                self.fecha_fin = self.fecha_fin.strftime(r'%Y-%m-%d')
            if not self.DB:
                self.DB = {}
            self.DB = json.dumps(self.DB)
            if not self.firm:
                self.firm = f'{st.session_state.login.id} / {datetime.now().strftime(r'%Y-%m-%d %H:%M')}'
            return asdict(self)

        @classmethod
        def from_dict(cls, values: Dict[str, Any]) -> 'Pedidos.Pedido':
            cls_fields = {f.name for f in fields(cls)}
            data = {k: v for k, v in values.items() if k in cls_fields}
            if isinstance(data['fecha_ini'], str):
                data['fecha_ini'] = datetime.strptime(data['fecha_ini'], r'%Y-%m-%d')
            if isinstance(data['fecha_fin'], str):
                data['fecha_fin'] = datetime.strptime(data['fecha_fin'], r'%Y-%m-%d')
            return cls(**data)

    @st.dialog('➕ NUEVA GPI', width='medium')
    def new_pedido() -> None:
        pedido_id = st.text_input('PEDIDO Id', value=None)
        contraseña = st.text_input('CONTRASEÑA', value=None)
        info = st.text_area('INFO / DESCRIPCIÓN', value=None, height=1)
        fecha_ini = st.date_input('FECHA INICIO', value=None, format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=None, format='YYYY-MM-DD')
        b_units = get_business_units(st.session_state.bu)['id'].to_list()
        bu_id = st.selectbox('BUSINESS UNIT', options=b_units, index=None, accept_new_options=False)
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        planificador = st.selectbox('PLANIFICADOR', options=usuarios, index=None, accept_new_options=False)
        alarma = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, horizontal=True)
        alarma_mod = Alarmas.get_int(alarma)
        btn = st.button('CREAR PEDIDO', width='stretch', icon='⚠️')
        mail = st.checkbox('ENVIAR MAIL')
        fecha_mod = datetime.now().strftime(r'%Y-%m-%d %H:%M')
    
        if btn:
            if not pedido_id or not info or not fecha_ini or not fecha_fin:
                st.warning("RELLENA LOS DATOS DEL PEDIDOS", icon='⚠️')
            else:
                if fecha_fin <= fecha_ini:
                    st.warning("FECHA DE FIN TIENE QUE SER MAYOR QUE FECHA DE INICIO", icon='⚠️')
                else:
                    if not planificador:
                        st.warning("ES NECESARIO ASIGNAR UN PLANIFICADOR", icon='⚠️')
                    else:
                        count = DB.execute('SELECT COUNT (*) FROM pedidos WHERE id=?', [pedido_id], fetch=1)[0]
                        if count > 0:
                            st.warning("ESTE PEDIDO YA EXISTE", icon='⚠️')
                        else:
                            mod = Modificacion(
                                fecha=datetime.now(),
                                info='Creación de pedido',
                                data=None,
                                user=st.session_state.login.id
                            )
                            pedido = Pedidos.Pedido(
                                id=pedido_id.upper(),
                                info=info,
                                bu_id=bu_id,
                                planificador=planificador,
                                fecha_ini=fecha_ini,
                                fecha_fin=fecha_fin,
                                contraseña=contraseña,
                                alarma=alarma_mod,
                                DB={
                                    'modificaciones': [mod.to_dict()],
                                    'xlsx': None,
                                },
                            )
                            DB.insert('pedidos', values=pedido.to_sql())
                            st.session_state.pedidos += 1
                            if mail:
                                send_mail()
                            st.rerun()

    @st.dialog('ℹ️ INFO GPI', width='medium')
    def edit_pedido(pedido: 'Pedidos.Pedido') -> None:
        st.header(pedido.id, divider='blue')
        info = st.text_area('INFO / DESCRIPCIÓN', value=pedido.info, height=1)
        fecha_ini = st.date_input('FECHA INICIO', value=pedido.fecha_ini, format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=pedido.fecha_fin, format='YYYY-MM-DD')
        b_units = get_business_units(st.session_state.bu)['id'].to_list()
        bu_id = st.selectbox('BUSINESS UNIT', options=b_units, index=b_units.index(pedido.bu_id), accept_new_options=False)
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        planificador = st.selectbox('PLANIFICADOR', options=usuarios, index=usuarios.index(pedido.planificador), accept_new_options=False)
        alarma_indx = pedido.alarma - 1 if isinstance(pedido.alarma, int) else None
        alarma_color = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
        alarma = Alarmas.get_int(alarma_color)
        btn_mod = st.button('MODIFICAR', width='stretch')
        info_mod = st.text_area('INFO MODIFICACIÓN', height=1)
        mail = st.checkbox('ENVIAR MAIL')
        fecha_mod = datetime.now().strftime(r'%Y-%m-%d %H:%M')
        # st.write(pedido)

        if btn_mod:
            if fecha_fin < fecha_ini:
                st.warning("LA FECHA DE FIN ES MENOR QUE LA FECHA DE INICIO", icon='⚠️')
            elif not info_mod:
                st.warning("INDICA EL MOTIVO DE LA MODIFICACIÓN", icon='⚠️')
            else:
                mod = Modificacion(
                    fecha=datetime.now(),
                    info=info_mod,
                    data=dict(),
                    user=st.session_state.login.id
                )
                # info_mod = f'## MODIFICACIÓN: {fecha_mod}\n{info_mod}\n\n'
                values = dict()
                if info != pedido.info:
                    values['info'] = info
                if fecha_ini != pedido.fecha_ini.date():
                    values['fecha_ini'] = fecha_ini.strftime(r'%Y-%m-%d')
                if fecha_fin != pedido.fecha_fin.date():
                    values['fecha_fin'] = fecha_fin.strftime(r'%Y-%m-%d')
                if bu_id != pedido.bu_id:
                    values['bu_id'] = bu_id
                if planificador != pedido.planificador:
                    values['planificador'] = planificador
                if alarma != pedido.alarma:
                    values['alarma'] = alarma
                pedido_dict = pedido.to_dict()
                for k, v in values.items():
                    old = pedido_dict[k]
                    new = v
                    if isinstance(old, datetime): old = old.strftime(r'%Y-%m-%d')
                    if isinstance(new, datetime): new = new.strftime(r'%Y-%m-%d')
                    mod.data[k] = {'old': old, 'new': new}
                values['firm'] = f'{st.session_state.login.id} / {fecha_mod}'
                values['DB'] = pedido.DB
                if not values['DB'].get('modificaciones'):
                    values['DB']['modificaciones'] = []
                values['DB']['modificaciones'].append(mod.to_dict())
                values['DB'] = json.dumps(values['DB'])
                if mail:
                    send_mail()
                
                DB.update('pedidos', values=values, where={'id': pedido.id})
                st.session_state.pedidos += 1
                st.rerun()

    def tbl_pedidos(df: pd.DataFrame) -> int:
        pedidos_columns = ['info', 'id', 'bu_id', '#', 'hitos', 'fecha_ini', 'fecha_fin']
        col1, col2, col3 = st.columns(3)

        ## OPCIONES
        with col1.expander('OPCIONES', icon='🔧', width='stretch'):
            # tbl_height = st.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)
            st.button('NUEVO', width='stretch', icon=':material/add_box:', key='gpi_options_new', on_click=Pedidos.new_pedido)
            edit_holder = st.empty()
            # btn_edit = st.button('EDITAR', width='stretch', icon=':material/edit_square:', disabled=st.session_state.pedido_selection, key='gpi_options_edit', ) # on_click=Pedidos.edit_pedido / edit_square
            # st.write('REPORT')
            holder_report = st.empty()
            btn_report = holder_report.button('REPORT .xlsx', icon=r':material/docs:', width='stretch') # , on_click=report_pedidos
            if btn_report:
                report_bytes = report_pedidos()
                p_bar = holder_report.progress(0, 'Creando Report...')
                for percent_complete in range(100):
                    sleep(0.01)
                    p_bar.progress(percent_complete + 1, text='Creando Report...')
                holder_report.download_button(
                    'Download', 
                    data=report_bytes, 
                    file_name=r'report_pedidos.xlsx', 
                    icon=r':material/download:', 
                    width='stretch', 
                    on_click='rerun'
                )

        ## FILTROS
        with col2.expander('FILTROS', icon='🔍', width='stretch'):
            filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍')
            filter_bunit = st.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
            filter_alert = st.radio('ALERT', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=False)
        
        ## VISTA
        vista = col3.selectbox('PEDIDOS VISTA', options=['TABLA', 'SELECTBOX'], index=0, label_visibility='collapsed')

        # with col1.popover('TABLE OPTIONS', icon='🔧', width='stretch'):
        #     tbl_height = st.slider(label='TAMAÑO TABLA', label_visibility='visible', min_value=100, max_value=1000, value=150)

            # st.write('FILTROS')
            # with st.container(border=True):
            #     filter_bunit = st.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
            #     filter_alert = st.radio('ALERT', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
            # # btn_update = st.button('UPDATE FROM *.xlsx', icon='🧷', width='content', on_click=update_cosas, help=f'Actualizar los datos de pedidos desde el fichero <{file_name}>', use_container_width=True)
            # # st.file_uploader("ACTUALIZAR DATOS DESDE .xlsx")

        # with col3:
        #     filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍')

        ## DATAFRAME
        df_filter1 = df[pedidos_columns]
        if filter_bunit:
            df_filter2 = df_filter1[df_filter1['bu_id']==filter_bunit]
        else:
            df_filter2 = df_filter1
        colores = Alarmas.colors()
        colores.insert(0, None)
        if filter_alert != 'All':
            df_filter3 = df_filter2[df_filter2['#']==filter_alert]
        else:
            df_filter3 = df_filter2
        if filter_str and filter_str != '':
            # mask = df_filtered1.apply(lambda col: col.str.contains(df_filter_str, na=False)).any(axis=1)
            mask = df_filter3.select_dtypes(include=['object']).apply(
                    lambda col: col.str.contains(filter_str, na=False)
                ).any(axis=1)
            df_filter4 = df_filter3[mask]
        else: 
            df_filter4 = df_filter3
        
        ## DATA
        data_holder = st.empty()
        col4, _, _ = st.columns(3)
        height_holder = col4.empty()

        if vista == 'TABLA':
            columns_config = {
                'info': st.column_config.Column('INFO', width='large', pinned=True),
                'id': st.column_config.Column('ID', width='small'),
                'bu_id': st.column_config.Column('BUS. UNIT', width='small'),
                '#': st.column_config.Column('#', width=50, pinned=False),
                'hitos': st.column_config.NumberColumn('∑ Hitos', width=50),
                'fecha_ini': st.column_config.DatetimeColumn('fecha_ini', format="YYYY-MM-DD", width='small'),
                'fecha_fin': st.column_config.DatetimeColumn('fecha_fin', format="YYYY-MM-DD", width='small'),
            }
            # tbl_height = height_holder.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)
            tbl = data_holder.dataframe(
                df_filter4,
                hide_index=True,
                width='stretch',
                selection_mode='single-row',
                on_select='rerun',
                # height=tbl_height,
                row_height=40,
                column_config=columns_config
            )
            tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
            df_loc = df_filter4.index[tbl_iloc] if tbl_iloc != None else None
            
        if vista == 'SELECTBOX':
            pedido_id: str = st.selectbox('SELECT GPI', options=df_filter4['id'].to_list(), index=None, label_visibility='collapsed')
            df_loc = df_filter4.loc[df_filter4['id']==pedido_id].index[0] if pedido_id else None

        if df_loc != None:
            pedido = Pedidos.Pedido.from_dict(df.loc[df_loc].to_dict())
            edit_holder.button('EDITAR', width='stretch', icon=':material/edit_square:', key='gpi_options_edit', on_click=Pedidos.edit_pedido, kwargs={'pedido': pedido}) # on_click=Pedidos.edit_pedido / edit_square / , disabled=st.session_state.pedido_selection

        return df_loc

class Hitos:
    @dataclass
    class Hito:
        id: int
        pedido_id: str
        grupo: str
        info: str
        fecha_ini: datetime
        fecha_fin: datetime
        responsable: str
        alarma: int = None
        estado: int = None
        DB: dict = None
        firm: str = None

        def to_dict(self):
            return asdict(self)
        
        def to_sql(self) -> Dict[str, Any]:
            '''
            Devuelve un diccionario de valores para INSERT / UPDATE 
            '''
            if isinstance(self.fecha_ini, datetime):
                self.fecha_ini = self.fecha_ini.strftime(r'%Y-%m-%d')
            if isinstance(self.fecha_fin, datetime):
                self.fecha_fin = self.fecha_fin.strftime(r'%Y-%m-%d')
            if not self.DB:
                self.DB = {}
            for k, v in self.DB.items():
                if isinstance(v, datetime):
                    self.DB[k] = v.strftime(r'%Y-%m-%d %H:%M')
            self.DB = json.dumps(self.DB)
            if not self.firm:
                self.firm = f'{st.session_state.login.id} / {datetime.now().strftime(r'%Y-%m-%d %H:%M')}'
            return asdict(self)

        @classmethod
        def from_dict(cls, values: Dict[str, Any]) -> 'Pedidos.Pedido':
            cls_fields = {f.name for f in fields(cls)}
            data = {k: v for k, v in values.items() if k in cls_fields}
            if isinstance(data['fecha_ini'], str):
                data['fecha_ini'] = datetime.strptime(data['fecha_ini'], r'%Y-%m-%d')
            if isinstance(data['fecha_fin'], str):
                data['fecha_fin'] = datetime.strptime(data['fecha_fin'], r'%Y-%m-%d')
            return cls(**data)

    class nivel1(Enum):
        DISEÑO = 'Diseño'
        PPI = 'PPI' 
        INDUSTRIALIZACION = 'Industrialización'
        PRODUCCION = 'Producción'
        ENTREGA = 'Entrega'

    @st.dialog('➕ NUEVO HITO', width='medium')
    def new_hito(pedido_id: str) -> None:
        col_alert, col_bu, col_user = st.columns(3)
        alarma          = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, label_visibility='visible', width='content', horizontal=True)
        departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
        responsable      = col_user.selectbox('RESPONSABLE', options=get_usuarios_by_dept(departamento), index=None, accept_new_options=False)

        info = st.text_area('INFO / DESCRIPCIÓN', value=None)
        grupo = st.text_input('GRUPO')
        fecha_ini = st.date_input('FECHA INICIO', value=None, min_value=datetime(2024,1,1), format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=None, min_value=datetime(2024,1,1), format='YYYY-MM-DD')


        if st.button('AÑADIR HITO', icon='🔄️', width='stretch'):
            if not info or not grupo or not fecha_ini or not fecha_ini or not fecha_fin or not responsable:
                st.warning("RELLENA TODOS LOS DATOS", icon='⚠️')
            elif fecha_ini > fecha_fin:
                st.warning("FECHA DE FIN TIENE QUE SER MAYOR QUE FECHA DE INICIO", icon='⚠️')
            else:
                values = {
                    'pedido_id': pedido_id,
                    'grupo': grupo,
                    'info': info,
                    'fecha_ini': fecha_ini.strftime(r'%Y-%m-%d'),
                    'fecha_fin': fecha_fin.strftime(r'%Y-%m-%d'),
                    'responsable': responsable,
                    'alarma': alarma,
                    'estado': 1,
                    'firm': st.session_state.login.get_firm(),
                }
                DB.insert('hitos', values=values)
                st.session_state.hitos += 1
                st.rerun()

    @st.dialog('➕ NUEVO HITO', width='medium')
    def template(pedido_id: str, template: str) -> None:
        st.write(pedido_id)
        st.write(template)

    # def tbl_hitos(df: pd.DataFrame) -> int:
    def tbl_hitos(pedido_id: str) -> int:
        # columns = ['#', 'grupo', 'info', 'responsable', 'estado', 'Δ'] # 'fecha_ini', 'fecha_fin', 

        # ## OPTIONS
        # col1, col2, col3 = st.columns(3)

        # with col1.popover('TABLE OPTIONS', icon='🔧', width='stretch'):
        #     tbl_height = st.slider(label='HEIGHT', label_visibility='visible', min_value=200, max_value=1000, key='hitos')

        # ## DATAFRAME
        # df_filter = df[columns]
        # # styled_df = df.style.applymap(Alarmas.color_cells, subset=['Δ'])
        # # df['Δ'].map(Alarmas.color_cells)
        # # df_filter.style.apply(UI.color_cells, subset=['Δ'])
        # df_styled = df_filter.style.map(UI.color_cells, subset=['Δ']).hide(axis='index')
        # st.write(df_styled)

        ## TABLE
        # columns_config = {
        #     '#': st.column_config.Column('#', width=10),
        #     'Δ': st.column_config.Column('Δ', width=10),
        # }
        # tbl = st.dataframe(
        #     df_filter,
        #     hide_index=True,
        #     width='stretch',
        #     selection_mode='single-row',
        #     on_select='rerun',
        #     # height=tbl_height,
        #     row_height=40,
        #     column_config=columns_config
        # )

        ## LOC
        # if tbl_iloc == None:
        #     return None
        # else:
        #     df_serie = df_filter4.iloc[tbl_iloc].to_dict()
        #     if col2.button('EDITAR PEDIDO', icon='✏️', width='stretch'):
        #         edit_pedido(df_serie)
        #     return df_filter4.index[tbl_iloc]

        ## NEW 
        ## ____________________________________________________________________________________________________________________________

        col_hitos_options, col_hitos_filtros, col_hitos_vista = st.columns(3)

        with col_hitos_options.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Hitos.new_hito, kwargs={'pedido_id': pedido_id})
            # st.button('EDITAR', width='stretch', icon=':material/edit_square:', disabled=opt_edit) # edit_square
            edit_holder = st.empty()
            template = st.selectbox('TEMPLATE', options=['FABRICACIÓN', 'DESARROLLO SOFT'], index=None)
            if template:
                st.button('TEMPLATE', width='stretch', icon=':material/add_box:', on_click=Hitos.template, kwargs={'pedido_id': pedido_id, 'template': template})

        with col_hitos_filtros.expander('FILTROS', icon='🔍', width='stretch'):
            fltr_hitos_str = st.text_input('fltr_hitos_str', label_visibility='collapsed', icon='🔍')
            st.write('ALERTAS')
            col_r, col_y, col_g = st.columns(3)
            # filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
            col_r.checkbox('🟥', value=1) # 🟥🟨🟩
            col_y.checkbox('🟨', value=1) # 🟥🟨🟩
            col_g.checkbox('🟩', value=1) # 🟥🟨🟩
            st.write('ESTADO')
            col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            # filter_alert = st.radio('ALERTA', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
            col_e1.checkbox('⏳', value=1) # ⏳🔍⏫✅
            col_e2.checkbox('🔍', value=1) 
            col_e3.checkbox('⏫', value=1)
            col_e4.checkbox('✅', value=0)

        vistas: list = [
            'GANTT', 
            'TABLA', 
            # 'CALENDARIO'
        ]
        vista = col_hitos_vista.selectbox('VISTA', options=vistas, index=0, accept_new_options=False, label_visibility='collapsed')

        ## DATAFRAME
        df = get_hitos(pedido_id)
        # st.write(df)

        if vista == 'GANTT':
            data = [
                UI.Timeline(texto=pedido.id, grupo='GPI', fecha_ini=pedido.fecha_ini, fecha_fin=pedido.fecha_fin, color=pedido.alarma)
            ]
            ## Hitos
            for idx, row in df.iterrows():
                tl = UI.Timeline(
                    texto=row['info'],
                    grupo=row['grupo'],
                    fecha_ini=safe_datetime(row['fecha_ini']),
                    fecha_fin=safe_datetime(row['fecha_fin']),
                    color=row['alarma']
                )
                # if not tl.fecha_ini or pd.isna(tl.fecha_ini): 
                #     tl.fecha_ini = fecha_ini
                # if not tl.fecha_fin or pd.isna(tl.fecha_fin): 
                #     tl.fecha_fin = fecha_fin
                data.append(tl)
            df_gantt = pd.DataFrame(data)
            # st.write(df_gantt)
            with st.container(border=True): 
                tl_hitos = UI.my_timeline(df_gantt)
                # tl_hitos.selection
                # st.write(tl_hitos.selection['points'])
                if len(tl_hitos.selection['points']) == 1:
                    hito_indx = tl_hitos.selection['points'][0]['curve_number']
                    # data[hito_indx].texto
                    st.write(data[hito_indx].texto)

        if vista == 'TABLA':
            data_holder = st.empty()
            columns_hitos = ['info', 'grupo', 'responsable', '#', 'estado', 'fecha_ini', 'fecha_fin']

            # st.slider(label='con altura', min_value=100, max_value=500, value=150, label_visibility='collapsed', width='')
            columns_config = {
                
                'info': st.column_config.Column('info', width='medium'),
                'grupo': st.column_config.Column('id', width='medium'),
                '#': st.column_config.Column('#', width=20),
                'estado': st.column_config.Column('#', width=20),
                'fecha_ini': st.column_config.DatetimeColumn('fecha_ini', format="YYYY-MM-DD", width='small'),
                'fecha_fin': st.column_config.DatetimeColumn('fecha_fin', format="YYYY-MM-DD", width='small'),
            }
            # tbl_height = height_holder.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)
            tbl = data_holder.dataframe(
                df[columns_hitos],
                hide_index=True,
                width='stretch',
                selection_mode='single-row',
                on_select='rerun',
                # height=tbl_height,
                row_height=40,
                column_config=columns_config
            )

        if vista == 'CALENDARIO':
            pass

class Acciones:
    @dataclass
    class Accion:
        id: str

        def to_dict(self):
            return asdict(self)
        
        def to_sql(self) -> Dict[str, Any]:
            '''
            Devuelve un diccionario de valores para INSERT / UPDATE 
            '''
            if isinstance(self.fecha_ini, datetime):
                self.fecha_ini = self.fecha_ini.strftime(r'%Y-%m-%d')
            if isinstance(self.fecha_fin, datetime):
                self.fecha_fin = self.fecha_fin.strftime(r'%Y-%m-%d')
            if not self.DB:
                self.DB = {}
            for k, v in self.DB.items():
                if isinstance(v, datetime):
                    self.DB[k] = v.strftime(r'%Y-%m-%d %H:%M')
            self.DB = json.dumps(self.DB)
            if not self.firm:
                self.firm = f'{st.session_state.login.id} / {datetime.now().strftime(r'%Y-%m-%d %H:%M')}'
            return asdict(self)

        @classmethod
        def from_dict(cls, values: Dict[str, Any]) -> 'Pedidos.Pedido':
            cls_fields = {f.name for f in fields(cls)}
            data = {k: v for k, v in values.items() if k in cls_fields}
            if isinstance(data['fecha_ini'], str):
                data['fecha_ini'] = datetime.strptime(data['fecha_ini'], r'%Y-%m-%d')
            if isinstance(data['fecha_fin'], str):
                data['fecha_fin'] = datetime.strptime(data['fecha_fin'], r'%Y-%m-%d')
            return cls(**data)
    
    @st.dialog('NUEVA ACCIÓN', width='medium')
    def form_accion(pedido_id: str):
        # st.file_uploader('pedidosPorPosicion.xlsx', type=['.xlsx'], accept_multiple_files=False)
        # st.file_uploader('Seguimiento plan de entregas_ING_Navales.xlsx', type=['.xlsx'], accept_multiple_files=False)
        
        col_alert, col_bu, col_user = st.columns(3)
        alarma          = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
        departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
        responsable      = col_user.selectbox('RESPONSABLE', options=get_usuarios_by_dept(departamento), index=None, accept_new_options=False)
        
        causa           = st.selectbox('CAUSA TIPO', options=[c.value for c in Causas], index=None, label_visibility='visible', )
        info            = st.text_area('INFO', value='', width='stretch') # height=1, 
        accion          = st.text_area('ACCIÓN', value='', height=1, width='stretch')
        fecha           = st.date_input('FECHA REQUERIDA', min_value=datetime.now().date(), value=None)
        # file            = st.file_uploader('INSERT FILE (PHOTO/PDF/etc)', disabled=True)
        # st.camera_input('INSERT PHOTO')

        st.container(border=False, height=20) ## Separador

        if st.button('UPDATE DATA', icon='🔄️', width='stretch'):
            if not responsable \
                or not causa \
                or not info \
                or not accion \
                or not fecha:
                st.warning('RELLENA TODOS LOS CAMPOS', icon='⚠️')
            # st.write('ALARMA', color_indx)
            # st.write('b_unit', b_unit)
            # st.write('responsable', responsable)
            # st.write('causa', [c.value for c in Causas].index(causa))
            
            else:
                alarma_indx = list(Alarmas.colors()).index(alarma)+1
                causa_indx = [c.value for c in Causas].index(causa)
                causa_id = [c.name for c in Causas][causa_indx]
                fecha_ts = datetime(year=fecha.year, month=fecha.month, day=fecha.day).timestamp()
                values = {
                    'pedido_id': pedido_id,
                    'causa': causa_id,
                    'alarma': alarma_indx,
                    'info': info,
                    'accion': accion,
                    'planificador': st.session_state.login.id, 
                    'responsable': responsable,
                    'fecha_accion': datetime.today().timestamp(),
                    'fecha_req': fecha_ts,
                    'estado': 1,
                    'firm': st.session_state.login.get_firm()
                }
                DB.insert('acciones', values=values)
                DB.update_json('pedidos', 'DB', 'id', pedido, {causa_id: alarma_indx})
                st.session_state.pedidos += 1
                st.rerun()

    @st.dialog('DETALLE ACCIÓN', width='medium')
    def detalle_accion(x):
        st.write(x)

    def tbl_acciones(df: pd.DataFrame) -> int:
        columns = ['#', 'causa', 'info', 'accion', 'fecha_accion', 'fecha_req', 'planificador', 'responsable', 'estado']
        
        ## OPTIONS
        col1, col2, col3 = st.columns(3)
        with col1.popover('PDCA OPTIONS', icon='🔧', width='stretch'):
            pass
        if col2.button('AÑADIR ACCION', width='stretch', icon='➕'):
            form_accion(pedido)

        ## DATAFRAME
        # df_acciones = get_acciones(pedido)
        df_filter1 = df[columns]

        ## TABLE
        columns_config = {
            '#': st.column_config.Column('#', width=10),
            'info': st.column_config.Column('info', width=30),
            'accion': st.column_config.Column('accion', width=30),
            'fecha_accion': st.column_config.DatetimeColumn('fecha_accion', format="YYYY-MM-DD", width='small'),
            'fecha_req': st.column_config.DatetimeColumn('fecha_req', format="YYYY-MM-DD", width='small'),
        }

        tbl = st.dataframe(
            df_filter1, #  'pedido_id', '🏁'
            width='stretch', hide_index=True, selection_mode='single-row', on_select='rerun',
            column_config=columns_config
        )

        tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None

        return tbl_iloc



## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

## PEDIDOS

df_pedidos = get_pedidos(st.session_state.pedidos)
pedido_loc: int = Pedidos.tbl_pedidos(df_pedidos)

if pedido_loc != None:
    pedido = Pedidos.Pedido.from_dict(df_pedidos.loc[pedido_loc].to_dict())

    st.container(border=False, height=20) # Separador
    tab_hitos, tab_acciones, tab_gpilog = st.tabs(['HITOS', "PDCA's", 'GPI Log', ])

    ## HITOS
    with tab_hitos:
        # df_hitos = get_hitos(pedido.id)
        # hito_loc = Hitos.tbl_hitos(df_hitos)

        hito_loc = Hitos.tbl_hitos(pedido.id)
        # st.write(hito_loc)

    ## PDCAs
    pass

    ## GPI Log
    with tab_gpilog:
        # st.write(pedido.DB)
        modificaciones = pedido.DB.get('modificaciones', None)
        if modificaciones:
            for mod in modificaciones:
                # st.write(mod)
                fecha = mod.get('fecha', None)
                info = mod.get('info', None)
                user = mod.get('user', None)
                title = f'{fecha} / {user}'

                st.write(title)
                with st.container(border=True):
                    st.caption(info)
                    data = mod.get('data', None)
                    if data:
                        rows = []
                        for key, values in data.items():
                            rows.append({
                                "PARAMETRO": key,
                                "ANTERIOR": str(values.get("old")),
                                "NUEVO": str(values.get("new"))
                            })
                        df = pd.DataFrame(rows)
                        st.dataframe(pd.DataFrame(rows), hide_index=True)


## OLD 2025 09 18
## ___________________________________________________________________________________________________________________________

    # # pedido = df_pedidos.loc[pedido_loc]['id']
    # # info = df_pedidos.loc[pedido_loc]['info']
    # # fecha_ini = df_pedidos.loc[pedido_loc]['fecha_ini']
    # # fecha_fin = df_pedidos.loc[pedido_loc]['fecha_fin']
    # # alarma = df_pedidos.loc[pedido_loc]['alarma']
    # # db_data = df_pedidos.loc[pedido_loc]['DB']
    # # xlsx_data = db_data.get('xlsx', None)

    # pedido = Pedidos.Pedido.from_dict(df_pedidos.loc[pedido_loc].to_dict())

    # tab_bi, tab_portada, tab_pdca, tab_xlsx  = st.tabs(['📈 BI', 'PORTADA', 'PLAN DE ACCION', 'XLSX DATA'])

    # df_hitos = get_hitos(pedido_id=pedido.id)
    # # df_acciones = get_acciones(pedido_id=pedido)

    # with tab_bi:
    #     # bi_pedidos()
    #     col_estado, col_alarma, col_3 = st.columns(3)
    #     col_estado.selectbox('ESTADO', options=Estados.get_estados(), index=None, label_visibility='visible')
    #     col_alarma.selectbox('ALARMAS', options=Alarmas.colors(), index=None, label_visibility='visible')
    #     data = [
    #         UI.Timeline(texto=pedido.id, grupo='PEDIDO', fecha_ini=pedido.fecha_ini, fecha_fin=pedido.fecha_fin, color=pedido.alarma)
    #     ]
    #     ## Acciones
    #     # for idx, row in df_acciones.iterrows():
    #     #     time_str = f'ACCION {idx} / {row['causa']}'
    #     #     tl = UI.Timeline(
    #     #         hito=time_str,
    #     #         grupo=None,
    #     #         # fecha_ini=safe_datetime(row['fecha_accion']),
    #     #         # fecha_fin=safe_datetime(row['fecha_req']),
    #     #         texto=time_str,
    #     #         color=row['alarma']
    #     #     )
    #     #     if not tl.fecha_ini or pd.isna(tl.fecha_ini): 
    #     #         tl.fecha_ini = fecha_ini
    #     #     if not tl.fecha_fin or pd.isna(tl.fecha_fin): 
    #     #         tl.fecha_fin = fecha_fin
    #     #     data.append(tl)

    #     ## Hitos
    #     for idx, row in df_hitos.iterrows():
    #         tl = UI.Timeline(
    #             texto=row['info'],
    #             grupo=row['grupo'],
    #             fecha_ini=safe_datetime(row['fecha_ini']),
    #             fecha_fin=safe_datetime(row['fecha_fin']),
    #             color=row['alarma']
    #         )
    #         # if not tl.fecha_ini or pd.isna(tl.fecha_ini): 
    #         #     tl.fecha_ini = fecha_ini
    #         # if not tl.fecha_fin or pd.isna(tl.fecha_fin): 
    #         #     tl.fecha_fin = fecha_fin
    #         data.append(tl)
    #     df_gantt = pd.DataFrame(data)
    #     # st.write(df_gantt)
    #     with st.container(border=True): 
    #         UI.my_timeline(df_gantt)

        
    # #     fechas_xlsx = [
    # #         'Fecha aceptación',
    # #         'Fecha de emisión',
    # #         'Fecha entrega',
    # #         'Fecha fin planificada',
    # #         'Fecha fin requerida',
    # #         'Fecha inicio planificada',
    # #         'Fecha inicio requerida',
    # #         'Fecha planificada',
    # #         'Fecha seguimiento',
    # #         'Fecha última revisión',
    # #     ]

    # #     if xlsx_data:
    # #         data = [{"hito": f, "fecha": xlsx_data.get(f, None)} for f in fechas_xlsx if xlsx_data.get(f)]
    # #         df_fechas = pd.DataFrame(data)
    # #         df_fechas['fecha'].apply(safe_datetime)
    # #         # st.write(df_fechas)
    # #         # print(df_fechas.info())
    # #         UI.my_hitoline(df_fechas)

    # with tab_portada:
    # #     # get_portadas(pedido=pedido, info=info, df_acciones=df_acciones)
    # #     # st.write(df_hitos)
    #     Hitos.tbl_hitos(df_hitos)

    # # with tab_pdca:
    # #     accion_iloc = tbl_acciones(df_acciones)

    # #     if accion_iloc is not None: pass
    #         # if col_pdca_detalle.button('DETALLE', width='stretch', icon='🔍'):
    #         #     detalle_accion(df_acciones.iloc[iloc_accion])
    #         # st.text_area('INFO', value='', width='stretch', ed)
    #         # with st.container(border=True):
    #         #     col_accion1, col_accion2 = st.columns(2)
    #         #     with col_accion1:
    #         #         causa = df_acciones['causa'].iloc[accion_iloc]
    #         #         st.write('CAUSA:')
    #         #         st.caption(Causas[causa].value, width='stretch')
    #         #         st.text_area('INFO', value=df_acciones['info'].iloc[accion_iloc], width='stretch', height=1, disabled=True)
    #         #     with col_accion2:
    #         #         st.write('ESTADO:')
    #         #         estado_id = df_acciones['estado_id'].iloc[accion_iloc]
    #                 # st.write(Estados.id_by_estado()[estado_id], Estados.get_estados()[estado_id-1])
    #                 # st.text_area('accion', value=df_acciones['accion'].iloc[accion_iloc], width='stretch', height=1, disabled=True)
                
    #             # st.write('INFO:')
    #             # st.caption(df_acciones['info'].iloc[accion_iloc], width='stretch')
    #             # st.write('ACCION:')
    #             # st.caption(df_acciones['accion'].iloc[accion_iloc], width='stretch')

    # with tab_xlsx:
    #     if xlsx_data:
    #         df_xlsx = pd.DataFrame(
    #             [(k, str(v) if v is not None else "") for k, v in xlsx_data.items()],
    #             columns=["key", "value"]
    #         )
    #         st.write(df_xlsx)
