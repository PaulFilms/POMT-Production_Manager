from time import sleep

import streamlit as st
from functions import *



## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

def session_state_start():
    if not 'login' in st.session_state: st.session_state.login = None
    if not 'login_count' in st.session_state: st.session_state.login_count = 1
    if not 'dialog' in st.session_state: st.session_state.dialog = 'ℹ️ INFO'
    if not 'usuarios' in st.session_state: st.session_state.usuarios = 1
    if not 'pedidos' in st.session_state: st.session_state.pedidos = 1
    if not 'hitos' in st.session_state: st.session_state.hitos = 1
    if not 'bu' in st.session_state: st.session_state.bu = 1
    if not 'departamentos' in st.session_state: st.session_state.departamentos = 1
    if not 'acciones' in st.session_state: st.session_state.acciones = 1
    if not 'productos' in st.session_state: st.session_state.productos = 1

def get_firm():
    return f"{st.session_state.login.id} [{datetime.now().strftime(r'%Y-%m-%d / %H:%M')}]"



## PAGES
## ____________________________________________________________________________________________________________________________________________________________________

@st.dialog('LOGIN', width='small')
def login():
    username = st.text_input('Id USUARIO')
    password = st.text_input('PASSWORD', type='password')
    st.container(border=False, height=10)
    if st.button('LOG IN', icon='🙋‍♂️', width='stretch', ): # on_click=lambda: login(username, password)
        if not username or username == str(): #  or not password or password == str()
            st.warning('RELLENA LOS DATOS', icon='⚠️')
        elif DB.execute(f'SELECT COUNT (*) FROM usuarios WHERE id=?;', values=[username.lower()], fetch=1)[0] != 1:
            st.warning('LOGIN ERROR', icon='⚠️')
            st.session_state.login_count += 1
        else:
            data = DB.execute('SELECT * FROM usuarios WHERE id=?;', values=[username], fetch=1)
            st.session_state.login = ORM.Usuario.get_form_sql(data)
            st.rerun()

def logout():
    st.session_state.login = None

# pg_login = st.Page(r'navigation/login.py', title='Log-in', icon=':material/login:')
pg_login = st.Page(login, title='Log-in', icon=':material/login:', default=False)
pg_logout = st.Page(logout, title='Log-out', icon=':material/logout:', default=False)
pg_home = st.Page(r'navigation/home.py', title='HOME', icon=':material/home:', default=True)
pg_user = st.Page(r'navigation/user.py', title='USER', icon=':material/account_circle:', default=True)
pg_pedidos = st.Page(r'navigation/pedidos.py', title='GPI', icon=':material/box:')
pg_entregas = st.Page(r'navigation/entregas.py', title='PLAN ENTREGAS', icon=':material/delivery_truck_speed:')
pg_productos = st.Page(r'navigation/productos.py', title='PRODUCTOS', icon=':material/barcode_reader:')
pg_business_unit = st.Page(r'navigation/busines_unit.py', title='BUSINESS UNIT', icon=':material/business_center:')
pg_bi_dashboards = st.Page(r'navigation/bi_dashboards.py', title='BI / DASHBOARDS', icon=':material/monitoring:')
# pg_chat_ia = st.Page(r'navigation/chat_ia.py', title='ARTIFICIAL INTELLIGENCE', icon=':material/smart_toy:')
# pg_gantt = st.Page(r'navigation/gantt.py', title='GANTT', icon=':material/smart_toy:')



## UX
## ____________________________________________________________________________________________________________________________________________________________________

class Pedidos:
    @st.dialog('➕ NUEVA GPI', width='medium')
    def new() -> None:
        pedido_id = st.text_input('PEDIDO Id', value=None)
        contraseña = st.text_input('CONTRASEÑA', value=None)
        info = st.text_area('INFO / DESCRIPCIÓN', value=None, height=1)
        fecha_ini = st.date_input('FECHA INICIO', value=None, format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=None, format='YYYY-MM-DD')
        b_units = get_business_units(st.session_state.bu)['id'].to_list()
        bu_id = st.selectbox('BUSINESS UNIT', options=b_units, index=None, accept_new_options=False)
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        planificador = st.selectbox('PLANIFICADOR', options=usuarios, index=None, accept_new_options=False)
        alarma_color = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, horizontal=True)
        alarma_id = Alarmas.get_int(alarma_color)
        btn = st.button('CREAR PEDIDO', width='stretch', icon='⚠️')
        mail = st.checkbox('ENVIAR MAIL')

        if btn:
            count = DB.execute('SELECT COUNT (*) FROM pedidos WHERE id=?', [pedido_id], fetch=1)[0]

            if not pedido_id or not info or not fecha_ini or not fecha_fin or not bu_id or not planificador:
                st.warning("RELLENA LOS DATOS DEL PEDIDOS", icon='⚠️')
            elif fecha_fin <= fecha_ini:
                st.warning("FECHA DE FIN TIENE QUE SER MAYOR QUE FECHA DE INICIO", icon='⚠️')
            elif count != 0:
                st.warning("ESTE PEDIDO YA EXISTE", icon='⚠️')
            else:
                mod = Modificacion(
                    fecha=datetime.now(),
                    info='Creación de pedido',
                    data=None,
                    user=st.session_state.login.id
                )
                pedido = ORM.Pedido(
                    id=pedido_id.upper(),
                    info=info,
                    bu_id=bu_id,
                    planificador=planificador,
                    fecha_ini=fecha_ini,
                    fecha_fin=fecha_fin,
                    contraseña=contraseña,
                    alarma=alarma_id,
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

    @st.dialog('➕ INFO/EDIT GPI', width='medium')
    def edit(pedido: ORM.Pedido) -> None:
        st.header(pedido.id, divider='blue')
        info = st.text_area('INFO / DESCRIPCIÓN', value=pedido.info, height=1)
        b_units = get_business_units(st.session_state.bu)['id'].to_list()
        bu_id = st.selectbox('BUSINESS UNIT', options=b_units, index=b_units.index(pedido.bu_id), accept_new_options=False)
        fecha_ini = st.date_input('FECHA INICIO', value=pedido.fecha_ini, format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=pedido.fecha_fin, format='YYYY-MM-DD')
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        planificador = st.selectbox('PLANIFICADOR', options=usuarios, index=usuarios.index(pedido.planificador), accept_new_options=False)
        alarma_indx = pedido.alarma - 1 if isinstance(pedido.alarma, int) else None
        alarma_color = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
        alarma = Alarmas.get_int(alarma_color)
        btn_mod = st.button('MODIFICAR', width='stretch')
        info_mod = st.text_area('INFO MODIFICACIÓN', height=1)
        mail = st.checkbox('ENVIAR MAIL')

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

    @st.dialog('📄 HISTORICO', width='medium')
    def log(pedido: ORM.Pedido) -> None:
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
                        st.dataframe(pd.DataFrame(rows), hide_index=True)

    def tbl() -> ORM.Pedido:

        ## OPCIONES TABLA
        col_opciones, col_filtros, col_vista = st.columns(3)
        vistas = ['TABLA', 'SELECTBOX']

        with col_opciones.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', key='gpi_options_new', on_click=Pedidos.new)
            holder_report = st.empty() ## BOTON REPORT
            holder_select = st.empty() ## LABEL SELECCION
            holder_edit = st.empty() ## BOTON EDITAR
            holder_historico = st.empty() ## BOTON HISTORICO
        
        with col_filtros.expander('FILTROS', icon='🔍', width='stretch'):
            filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍')
            filter_bunit = st.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
            filter_user = st.selectbox('PLANIFICADOR (IP)', options=get_usuarios()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
            filter_alert = st.radio(
                'ALARMA', 
                options=["All", "🟥","🟨","🟩"], 
                label_visibility='visible', width='content', 
                horizontal=True
            )
        
        vista = col_vista.selectbox('PEDIDOS VISTA', options=vistas, index=0, label_visibility='collapsed')


        ## DATAFRAME
        df = get_pedidos(st.session_state.pedidos)
        if filter_str != str():
            mask = df.select_dtypes(include=['object']).apply(
                lambda col: col.str.contains(filter_str, case=False, na=False)
            ).any(axis=1)
            df = df[mask]
        df = df[df['bu_id']==filter_bunit] if filter_bunit != None else df
        df = df[df['planificador']==filter_user] if filter_user != None else df
        df = df[df['alarma']==Alarmas.get_int(filter_alert)] if filter_alert in Alarmas.colors() else df
        
        ## OPCIÓN REPORT
        btn_report = holder_report.button('REPORT .xlsx', icon=r':material/docs:', width='stretch') # , on_click=report_pedidos
        if btn_report:
            columns_df = df.columns.to_list()
            for col in ['DB', ]: columns_df.remove(col)
            file_name = r'report_pedidos.xlsx'
            path_file = os.path.join('temp', file_name)
            if os.path.exists(path_file):
                os.remove(path_file)
            DF_REPORT(path=path_file, dataFrame=df[columns_df])
            with open(path_file, "rb") as f:
                archivo_bytes = f.read()
            p_bar = holder_report.progress(0, 'Creando Report...')
            for percent_complete in range(100):
                sleep(0.01)
                p_bar.progress(percent_complete + 1, text='Creando Report...')
            holder_report.download_button(
                'Download', 
                data=archivo_bytes, 
                file_name=file_name, 
                icon=r':material/download:', 
                width='stretch', 
                on_click='rerun'
            )
            if os.path.exists(path_file):
                os.remove(path_file)
        
        if vista == 'TABLA':
            tbl_holder = st.empty()
            col_height, _, _ = st.columns(3)
            height_holder = col_height.empty()

            columns = ['#', 'info', 'id', 'bu_id', 'planificador', 'fecha_ini', 'fecha_fin', '∑_hitos', '∑_acciones', 'LM', 'DT', 'PL', 'PR', 'EM', 'CA']
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

            if df.shape[0] < 10:
                tbl_height = 'auto'
            else:
                tbl_height = height_holder.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)

            tbl = tbl_holder.dataframe(
                df[columns],
                hide_index=True,
                width='stretch',
                selection_mode='single-row',
                on_select='rerun',
                height=tbl_height,
                row_height=40,
                column_config=columns_config
            )
            tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
            df_loc = df.index[tbl_iloc] if tbl_iloc != None else None

        if vista == 'SELECTBOX':
            pedido_id: str = st.selectbox('SELECT GPI', options=df['id'].to_list(), index=None, label_visibility='collapsed')
            df_loc = df.loc[df['id']==pedido_id].index[0] if pedido_id else None

        pedido: ORM.Pedido = None
        if df_loc != None:
            pedido = ORM.Pedido.from_dict(df.loc[df_loc].to_dict())
            holder_select.write('SELECCIÓN')
            holder_edit.button('EDITAR', width='stretch', icon=':material/edit_square:', key='gpi_options_edit', on_click=Pedidos.edit, kwargs={'pedido': pedido})
            holder_historico.button('HISTORICO', width='stretch', icon=':material/history_toggle_off:', key='gpi_options_log', on_click=Pedidos.log, kwargs={'pedido': pedido})

        return pedido

class Hitos:
    @st.dialog('➕ NUEVO HITO', width='medium')
    def new() -> None:
        pass

    @st.dialog('➕ INFO/EDIT HITO', width='medium')
    def edit(hito: ORM.Hito) -> None:
        pass

    def tbl(pedido_id: str = None) -> ORM.Hito:

        ## OPCIONES TABLA
        col_opciones, col_filtros, col_vista = st.columns(3)
        vistas = ['TABLA', 'GANTT']

        with col_opciones.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', key='btn_hitos_new', on_click=Hitos.new)
            holder_report = st.empty() ## BOTON REPORT
            holder_select = st.empty() ## LABEL SELECCION
            holder_edit = st.empty() ## BOTON EDITAR
            holder_historico = st.empty() ## BOTON HISTORICO
        
        with col_filtros.expander('FILTROS', icon='🔍', width='stretch'):
            filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍', key='filter_str_hitos')
            # filter_user = st.selectbox('PLANIFICADOR (IP)', options=get_usuarios()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False, key='filter_user_hitos')
            filter_alert = st.radio(
                'ALARMA', 
                options=["All", "🟥","🟨","🟩"], 
                label_visibility='visible', width='content', 
                horizontal=True,
                key='filter_alert_hitos'
            )
        
        vista = col_vista.selectbox('PEDIDOS VISTA', options=vistas, index=0, label_visibility='collapsed')

        ## DATAFRAME
        df = get_hitos(pedido_id=pedido_id)
        if filter_str != str():
            mask = df.select_dtypes(include=['object']).apply(
                lambda col: col.str.contains(filter_str, case=False, na=False)
            ).any(axis=1)
            df = df[mask]
        # df = df[df['bu_id']==filter_bunit] if filter_bunit != None else df
        # df = df[df['planificador']==filter_user] if filter_user != None else df
        df = df[df['alarma']==Alarmas.get_int(filter_alert)] if filter_alert in Alarmas.colors() else df
        
        ## OPCIÓN REPORT
        # btn_report = holder_report.button('REPORT .xlsx', icon=r':material/docs:', width='stretch') # , on_click=report_pedidos
        # if btn_report:
        #     columns_df = df.columns.to_list()
        #     for col in ['DB', ]: columns_df.remove(col)
        #     file_name = r'report_hitos.xlsx'
        #     path_file = os.path.join('temp', file_name)
        #     if os.path.exists(path_file):
        #         os.remove(path_file)
        #     DF_REPORT(path=path_file, dataFrame=df[columns_df])
        #     with open(path_file, "rb") as f:
        #         archivo_bytes = f.read()
        #     p_bar = holder_report.progress(0, 'Creando Report...')
        #     for percent_complete in range(100):
        #         sleep(0.01)
        #         p_bar.progress(percent_complete + 1, text='Creando Report...')
        #     holder_report.download_button(
        #         'Download', 
        #         data=archivo_bytes, 
        #         file_name=file_name, 
        #         icon=r':material/download:', 
        #         width='stretch', 
        #         on_click='rerun'
        #     )
        #     if os.path.exists(path_file):
        #         os.remove(path_file)
        
        if vista == 'TABLA':
            tbl_holder = st.empty()
            col_height, _, _ = st.columns(3)
            height_holder = col_height.empty()

#             columns_hitos = ['nombre', 'grupo', 'responsable', '#', 'fecha_req', 'fecha_plan', 'Δ', 'estado']

            columns = ['#', 'nombre', 'responsable', 'fecha_req', 'fecha_plan', 'Δ', 'estado', '∑_acciones', 'LM', 'DT', 'PL', 'PR', 'EM', 'CA', 'id', ]
            columns_config = {
                'id': st.column_config.Column('id', width=0),
                '#': st.column_config.Column('#', width=50, pinned=True),
                'nombre': st.column_config.Column('DESCRIPCIÓN HITO', width='medium', pinned=True),
                
                # 'bu_id': st.column_config.Column('BUS. UNIT', width='small'),
                # 'planificador': st.column_config.Column('IP', width='small'),
                'fecha_req': st.column_config.DatetimeColumn('FECHA REQUERIDA', format="YYYY-MM-DD", width='small'),
                'fecha_plan': st.column_config.DatetimeColumn('FECHA PLANIFICADA', format="YYYY-MM-DD", width='small'),
                # '∑_hitos': st.column_config.NumberColumn('∑_hitos', width=50),
                # '∑_acciones': st.column_config.NumberColumn('∑_acciones', width=50),
            }
            for c in Causas:
                columns_config[c.name] = st.column_config.TextColumn(c.name, width=50)

            if df.shape[0] < 10:
                tbl_height = 'auto'
            else:
                tbl_height = height_holder.slider(label='TAMAÑO TABLA', label_visibility='collapsed', min_value=100, max_value=1000, value=150)

            tbl = tbl_holder.dataframe(
                df[columns],
                hide_index=True,
                width='stretch',
                selection_mode='single-row',
                on_select='rerun',
                height=tbl_height,
                row_height=40,
                column_config=columns_config
            )
            tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
            df_loc = df.index[tbl_iloc] if tbl_iloc != None else None

        if vista == 'SELECTBOX':
            pedido_id: str = st.selectbox('SELECT GPI', options=df['id'].to_list(), index=None, label_visibility='collapsed')
            df_loc = df.loc[df['id']==pedido_id].index[0] if pedido_id else None

        pedido: ORM.Pedido = None
        if df_loc != None:
            pedido = ORM.Pedido.from_dict(df.loc[df_loc].to_dict())
            holder_select.write('SELECCIÓN')
            holder_edit.button('EDITAR', width='stretch', icon=':material/edit_square:', key='gpi_options_edit', on_click=Pedidos.edit, kwargs={'pedido': pedido})
            holder_historico.button('HISTORICO', width='stretch', icon=':material/history_toggle_off:', key='gpi_options_log', on_click=Pedidos.log, kwargs={'pedido': pedido})

        return pedido