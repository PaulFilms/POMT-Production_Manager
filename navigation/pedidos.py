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
from app import session_state_start, get_firm
from functions import *

session_state_start()


## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

class Templates:

    class fabricacion(Enum):
        DISEÑO = 'Diseño', 20
        PPI = 'PPI', 40
        INDUSTRIALIZACION = 'Industrialización', 60
        PRODUCCION = 'Producción', 80
        ENTREGA = 'Entrega', 90
    
    class desarrollo_soft(Enum):
        REQUERIMIENTOS = 'Requerimientos', 0 
        ANALISIS = 'Análisis', 20 
        DISEÑO = 'Diseño', 40 
        DESARROLLO = 'Desarrollo', 60 
        VALIDACION = 'Validación', 80 
        ENTREGA = 'Entrega', 90

    # class templates(Enum):
    #     FABRICACION = Templates.fabricacion
    #     DESARROLLO_SOFT = Templates.desarrollo_soft

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
                self.firm = get_firm()
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
                values['firm'] = get_firm()
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

    def report(df: pd.DataFrame):
        # df = get_pedidos(st.session_state.pedidos)
        # df = df.drop(['DB', '∑', '#', 'fecha_ini', 'fecha_fin'], axis=1)
        path = r'temp/report_pedidos.xlsx'
        if os.path.exists(path):
            os.remove(path)
        DF_REPORT(path=path, dataFrame=df)
        with open(path, "rb") as f:
            archivo_bytes = f.read()
        return archivo_bytes

    def tbl_pedidos(df: pd.DataFrame) -> int:
        # pedidos_columns = ['info', 'id', 'bu_id', 'planificador', 'fecha_ini', 'fecha_fin', '#', '∑_hitos', '∑_acciones', 'LM', 'DT', 'PL', 'PR', 'EM', 'CA']
        pedidos_columns = ['#', 'info', 'id', 'bu_id', 'planificador', 'fecha_ini', 'fecha_fin', '∑_hitos', '∑_acciones', 'LM', 'DT', 'PL', 'PR', 'EM', 'CA']
        
        ## OPCIONES
        col1, col2, col3 = st.columns(3)
        with col1.expander('OPCIONES', icon='🔧', width='stretch'):
            # tbl_height = st.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)
            st.button('NUEVO', width='stretch', icon=':material/add_box:', key='gpi_options_new', on_click=Pedidos.new_pedido)
            edit_holder = st.empty() ## BOTON EDITAR
            # btn_edit = st.button('EDITAR', width='stretch', icon=':material/edit_square:', disabled=st.session_state.pedido_selection, key='gpi_options_edit', ) # on_click=Pedidos.edit_pedido / edit_square
            # st.write('REPORT')
            holder_report = st.empty() ## BOTON REPORT

        ## FILTROS
        with col2.expander('FILTROS', icon='🔍', width='stretch'):
            filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍')
            filter_bunit = st.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
            filter_user = st.selectbox('PLANIFICADOR (IP)', options=get_usuarios()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
            # st.write('ALARMA')
            # with st.container(border=True):
            filter_alert = st.radio(
                'ALARMA', 
                options=["All", "🟥","🟨","🟩"], 
                label_visibility='visible', width='content', 
                horizontal=True
            )
        
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
        df_filter1 = df[pedidos_columns] ## COLUMNS
        ## BUSINESS UNIT
        df_filter2 = df_filter1[df_filter1['bu_id']==filter_bunit] if filter_bunit != None else df_filter1
        ## ALERTA
        colores = Alarmas.colors()
        colores.insert(0, None)
        df_filter3 = df_filter2[df_filter2['#']==filter_alert] if filter_alert in colores else df_filter2 # df_filter2[df_filter2['#'].isna()]
        ## PLANIFICADOR
        df_filter4 = df_filter3[df_filter3['planificador']==filter_user] if filter_user != None else df_filter3
        
        ## TEXTO
        if filter_str and filter_str != '':
            mask = df_filter4.select_dtypes(include=['object']).apply(
                lambda col: col.str.contains(filter_str, case=False, na=False)
            ).any(axis=1)
            df_filter5 = df_filter4[mask]
        else: 
            df_filter5 = df_filter4

        btn_report = holder_report.button('REPORT .xlsx', icon=r':material/docs:', width='stretch') # , on_click=report_pedidos
        if btn_report:
            report_bytes = Pedidos.report(df_filter5)
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
        
        ## DATA
        data_holder = st.empty()
        col4, _, _ = st.columns(3)
        height_holder = col4.empty()

        if vista == 'TABLA':
            columns_config = {
                '#': st.column_config.Column('#', width=50, pinned=True),
                'info': st.column_config.Column('DESCRIPCIÓN GPI', width=None, pinned=True),
                'id': st.column_config.Column('GPI', width='small'),
                'bu_id': st.column_config.Column('BUS. UNIT', width='small'),
                'planificador': st.column_config.Column('IP', width='small'),
                'fecha_ini': st.column_config.DatetimeColumn('fecha_ini', format="YYYY-MM-DD", width='small'),
                'fecha_fin': st.column_config.DatetimeColumn('fecha_fin', format="YYYY-MM-DD", width='small'),
                '∑_hitos': st.column_config.NumberColumn('∑_hitos', width=50),
                '∑_acciones': st.column_config.NumberColumn('∑_acciones', width=50),
            }
            for c in Causas:
                columns_config[c.name] = st.column_config.TextColumn(c.name, width=50)
            # tbl_height = height_holder.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)
            tbl = data_holder.dataframe(
                df_filter5,
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
        nombre: str
        fecha_ini: datetime
        fecha_fin: datetime
        responsable: str
        alarma: int = None
        estado: int = None
        info: str = None
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
        def from_dict(cls, values: Dict[str, Any]) -> 'Hitos.Hito':
            cls_fields = {f.name for f in fields(cls)}
            data = {k: v for k, v in values.items() if k in cls_fields}
            if isinstance(data['fecha_ini'], str):
                data['fecha_ini'] = datetime.strptime(data['fecha_ini'], r'%Y-%m-%d')
            if isinstance(data['fecha_fin'], str):
                data['fecha_fin'] = datetime.strptime(data['fecha_fin'], r'%Y-%m-%d')
            return cls(**data)

    @st.dialog('➕ NUEVO HITO', width='medium')
    def new_hito(pedido_id: str) -> None:
        col_alert, col_bu, col_user = st.columns(3)
        alarma          = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, label_visibility='visible', width='content', horizontal=True)
        departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
        responsable      = col_user.selectbox('RESPONSABLE', options=get_usuarios_by_dept(departamento), index=None, accept_new_options=False)

        nombre = st.text_area('INFO / DESCRIPCIÓN', value=None)
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
                    'nombre': nombre,
                    'fecha_ini': fecha_ini.strftime(r'%Y-%m-%d'),
                    'fecha_fin': fecha_fin.strftime(r'%Y-%m-%d'),
                    'responsable': responsable,
                    'alarma': alarma,
                    'estado': 1,
                    'info': info,
                    'firm': get_firm(),
                }
                DB.insert('hitos', values=values)
                st.session_state.hitos += 1
                st.rerun()

    @st.dialog('ℹ️ INFO HITO', width='medium')
    def edit_hito(hito: 'Hitos.Hito') -> None:
        st.write(hito.pedido_id, '/', hito.grupo)
        st.write(hito.info)

        alarma_indx = pedido.alarma - 1 if isinstance(hito.alarma, int) else None
        alarma_color = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
        alarma = Alarmas.get_int(alarma_color)
        estado_icon = st.radio('ESTADO', options=Estados.get_estados_icon(), index=alarma_indx, horizontal=True)
        estado = Estados.get_id(estado_icon)
        fecha_ini = st.date_input('FECHA INICIO', value=hito.fecha_ini, format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=hito.fecha_fin, format='YYYY-MM-DD')
        # info = st.text_area('INFO / DESCRIPCIÓN', value=hito.info, height=1)
        btn_mod = st.button('MODIFICAR', width='stretch')
        info_mod = st.text_area('INFO MODIFICACIÓN', height=1)
        mail = st.checkbox('ENVIAR MAIL')
        fecha_mod = datetime.now().strftime(r'%Y-%m-%d %H:%M')

        if btn_mod:
            if fecha_fin < fecha_ini:
                st.warning("LA FECHA DE FIN ES MENOR QUE LA FECHA DE INICIO", icon='⚠️')
            elif not info_mod:
                st.warning("INDICA EL MOTIVO DE LA MODIFICACIÓN", icon='⚠️')
            else:
                fecha_ini = fecha_ini.strftime(r'%Y-%m-%d')
                fecha_fin = fecha_fin.strftime(r'%Y-%m-%d')
                mod = Modificacion(
                    fecha=datetime.now(),
                    info=info_mod,
                    data=dict(),
                    user=st.session_state.login.id
                )
                args = {
                    'fecha_ini': fecha_ini, 
                    'fecha_fin': fecha_fin, 
                    'alarma': alarma, 
                    'estado': estado, 
                    'info': info,
                }
                values = dict()
                for k, v in args.items():
                    old = getattr(hito, k)
                    new = v
                    if isinstance(old, datetime): old = old.strftime(r'%Y-%m-%d')
                    if isinstance(new, datetime): new = new.strftime(r'%Y-%m-%d')
                    if new != old:
                        mod.data[k] = {
                            'old': old,
                            'new': new,
                        }
                        values[k] = new
                
                values['firm'] = get_firm()
                values['DB'] = hito.DB
                if not values['DB'].get('modificaciones'):
                    values['DB']['modificaciones'] = []
                values['DB']['modificaciones'].append(mod.to_dict())
                values['DB'] = json.dumps(values['DB'])

                if mail:
                    send_mail()
                
                DB.update('hitos', values=values, where={'id': hito.id})
                st.session_state.hitos += 1
                st.rerun()


    # @st.dialog('➕ NUEVO HITO', width='medium')
    def template(pedido_id: str, template: str) -> None:
        # st.write(pedido_id)
        # st.write(template)
        # st.success(f'Creando Hitos desde template: {template}', icon='✅')
        pedido_fecha_ini = DB.execute('SELECT fecha_ini FROM pedidos WHERE id=?', [pedido_id], fetch=1)[0]
        pedido_fecha_fin = DB.execute('SELECT fecha_fin FROM pedidos WHERE id=?', [pedido_id], fetch=1)[0]
        pedido_fecha_ini = datetime.strptime(pedido_fecha_ini, r'%Y-%m-%d')
        pedido_fecha_fin = datetime.strptime(pedido_fecha_fin, r'%Y-%m-%d')
        duracion_total = (pedido_fecha_fin - pedido_fecha_ini).total_seconds()
        data = DB.execute('SELECT * FROM templates WHERE template=? ORDER BY orden;', [template])
        for i, hito in enumerate(data):
            per_ini = hito[4]
            if i + 1 < len(data):
                per_fin = data[i + 1][4]
            else:
                per_fin = 100  # Último tramo
            fecha_ini = pedido_fecha_ini + timedelta(seconds=duracion_total * per_ini / 100) + timedelta(days=1)
            fecha_fin = pedido_fecha_ini + timedelta(seconds=duracion_total * per_fin / 100)
            mod = Modificacion(
                    fecha=datetime.now(),
                    info='Creación desde template',
                    data=None,
                    user=st.session_state.login.id
                )
            hito = Hitos.Hito(
                id=None,
                pedido_id=pedido_id,
                grupo=hito[1],
                nombre=hito[2],
                fecha_ini=fecha_ini,
                fecha_fin=fecha_fin,
                responsable=None,
                alarma=1,
                estado=1,
                info=None,
                DB={
                    'modificaciones': [mod.to_dict()],
                },
                firm=None,
            )
            count = DB.execute('SELECT COUNT (*) FROM hitos WHERE pedido_id=? AND grupo=? AND nombre=?', [pedido_id, hito.grupo, hito.nombre], fetch=1)[0]
            if count == 0:
                DB.insert('hitos', values=hito.to_sql())
        st.session_state.hitos += 1
        st.rerun()

    # def tbl_hitos(df: pd.DataFrame) -> int:
    def tbl_hitos(pedido_id: str) -> 'Hitos.Hito':

        col_hitos_options, col_hitos_filtros, col_hitos_vista = st.columns(3)

        with col_hitos_options.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Hitos.new_hito, kwargs={'pedido_id': pedido_id})
            # st.button('EDITAR', width='stretch', icon=':material/edit_square:', disabled=opt_edit) # edit_square
            edit_holder = st.empty()
            templates = get_templates() # BUG: cache?
            template = st.selectbox('TEMPLATE', options=templates, index=None)
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
        hito_nombre: str = None
        # st.write(df)

        if vista == 'GANTT':
            data = [
                UI.Timeline(texto=pedido.id, grupo='GPI', fecha_ini=pedido.fecha_ini, fecha_fin=pedido.fecha_fin, color=pedido.alarma)
            ]
            ## Hitos
            for idx, row in df.iterrows():
                tl = UI.Timeline(
                    texto=row['nombre'],
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
                    hito_nombre = data[hito_indx].texto
                    # data[hito_indx].texto
                    # st.write(data[hito_indx].texto)


        if vista == 'TABLA':
            data_holder = st.empty()
            columns_hitos = ['nombre', 'grupo', 'responsable', '#', 'estado', 'fecha_ini', 'fecha_fin']

            # st.slider(label='con altura', min_value=100, max_value=500, value=150, label_visibility='collapsed', width='')
            columns_config = {
                'nombre': st.column_config.Column('NOMBRE', width='medium'),
                'grupo': st.column_config.Column('GRUPO', width='medium'),
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
            tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
            hito_nombre = df['nombre'].iloc[tbl_iloc] if tbl_iloc != None else None

        if vista == 'CALENDARIO':
            pass
        
        hito: Hitos.Hito = None
        
        if hito_nombre and hito_nombre != pedido_id:
            hito_dict = df[df['nombre']==hito_nombre].iloc[0].to_dict()
            hito = Hitos.Hito.from_dict(hito_dict)
            if hito.grupo != 'GPI':
                edit_holder.button('EDITAR', width='stretch', icon=':material/edit_square:', key='hito_options_edit', 
                    on_click=Hitos.edit_hito, kwargs={'hito': hito},
                )

        return hito

class Acciones:
    @dataclass
    class Accion:
        id: str
        pedido_id: str
        causa: str
        alarma: int
        info: str
        accion: str
        planificador: str
        responsable: str
        fecha_accion: datetime
        fecha_req: datetime
        estado: int = 0
        DB: dict = None
        firm: str = None

        def to_dict(self):
            return asdict(self)
        
        def to_sql(self) -> Dict[str, Any]:
            '''
            Devuelve un diccionario de valores para INSERT / UPDATE 
            '''
            if isinstance(self.fecha_accion, datetime):
                self.fecha_accion = self.fecha_accion.strftime(r'%Y-%m-%d')
            if isinstance(self.fecha_req, datetime):
                self.fecha_req = self.fecha_req.strftime(r'%Y-%m-%d')
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

    @st.dialog('➕ NUEVA ACCIÓN', width='medium')
    def new(pedido_id: str) -> None:
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

                accion = Acciones.Accion(
                    id=None,
                    pedido_id=pedido_id,
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

    def tbl_acciones(pedido_id: str) -> int:
        col_options, col_filtros, col_vista = st.columns(3)

        with col_options.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Acciones.new, kwargs={'pedido_id': pedido_id}, key='accion_options_new')
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
        df = get_acciones(pedido_id)

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

df_pedidos = get_pedidos(st.session_state.pedidos)
pedido_loc: int = Pedidos.tbl_pedidos(df_pedidos)

if pedido_loc != None:
    pedido = Pedidos.Pedido.from_dict(df_pedidos.loc[pedido_loc].to_dict())

    st.container(border=False, height=20) # Separador
    tab_hitos, tab_acciones, tab_gpilog = st.tabs(['HITOS', "PDCA", 'GPI Log', ])

    ## HITOS
    with tab_hitos:
        # df_hitos = get_hitos(pedido.id)
        # hito_loc = Hitos.tbl_hitos(df_hitos)

        hito: Hitos.Hito = Hitos.tbl_hitos(pedido.id)
        # st.write(hito_loc)

        if hito and hito.grupo != 'GPI':
            st.container(border=False, height=20) # Separador
            st.write('Log:')
            with st.container(border=True):
                modificaciones = hito.DB.get('modificaciones', None)
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

    ## PDCAs
    with tab_acciones:
        Acciones.tbl_acciones(pedido.id)

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

