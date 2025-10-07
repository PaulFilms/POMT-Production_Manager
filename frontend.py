from time import sleep
from datetime import date, datetime
from typing import TYPE_CHECKING

import streamlit as st
from functions import *

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator



## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

st_fecha_formato = r'DD/MM/YYYY'

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


class Caminos:
    def tbl(pedido_id: str):
        import pandas as pd
        import plotly.graph_objects as go
        import streamlit as st
        from estilos import style_metric_cards
        from functions import DB  # conexión global SQL definida en tu proyecto

        # --- 1️⃣ OBTENER EL ARCHIVO ASOCIADO AL PEDIDO ---
        sql_archivo = "SELECT pde_archivo FROM view_pedidos WHERE id = ?;"
        result = DB.execute(sql_archivo, values=[pedido_id], fetch=1)
        if not result:
            st.warning(f"No se encontró ningún archivo asociado al pedido '{pedido_id}'")
            return
        
        archivo = result[0]

        # --- 2️⃣ CONSTRUIR CONDICIÓN PARA LOS 20 CAMINOS CRÍTICOS ---
        columnas_cc = [f'"Camino Critico {i}"' for i in range(1, 21)]
        where_cond = " OR ".join([f"{col} GLOB '[0-9]*'" for col in columnas_cc])

        sql_items = f"""
            SELECT "CODIGO", "Estado MD4C"
            FROM csv_pde_items
            WHERE filename = ?
            AND ({where_cond})
            ORDER BY rowid DESC
            LIMIT 20;
        """

        data = DB.execute(sql_items, values=[archivo], fetch=2)
        headers = DB.execute("SELECT 'CODIGO', 'Estado MD4C' FROM csv_pde_items LIMIT 0;", fetch=4)
        df = pd.DataFrame(data, columns=["CODIGO", "Estado MD4C"])
        print(df.head())

        if df.empty:
            st.warning(f"No hay registros en csv_pde_items con 'Camino Critico 1' = 1 para el archivo '{archivo}'")
            return

        # --- 3️⃣ LIMPIAR DATOS ---
        # Eliminar filas con Estado MD4C vacío o nulo
        df = df[df["Estado MD4C"].notna() & (df["Estado MD4C"] != "")]
        if df.empty:
            st.warning("No hay valores válidos en la columna 'Estado MD4C'.")
            return

        # --- 4️⃣ AGRUPACIÓN POR ESTADO ---
        conteo = df["Estado MD4C"].value_counts().to_dict()
        total = sum(conteo.values())

        # --- 5️⃣ COLORES PERSONALIZADOS ---
        # Puedes ajustar los colores según los estados reales que devuelva tu BD
        palette = [
            "#FFEB3B", "#03A9F4", "#9C27B0", "#03A9F4", "#9C27B0", "#FF9800", "#607D8B"
        ]
        estados_unicos = list(conteo.keys())
        colores = {estado: palette[i % len(palette)] for i, estado in enumerate(estados_unicos)}

        # --- 6️⃣ VISUALIZACIÓN ---
        st.subheader(f"📦 Caminos Críticos — {pedido_id}", divider='orange')

        # --- Gráfico Doughnut ---
        col_graf, col_tabla = st.columns([0.6, 0.4])
        with col_graf:
            fig = go.Figure(
                data=[go.Pie(
                    labels=list(conteo.keys()),
                    values=list(conteo.values()),
                    hole=0.6,
                    textinfo="label+percent",
                    marker=dict(colors=[colores[k] for k in conteo.keys()])
                )]
            )
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=10, r=10),
                showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- Tabla con las columnas reales ---
        with col_tabla:
            st.markdown(f"### Codigos Retrasados")
            st.dataframe(
                df[["CODIGO", "Estado MD4C"]],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "CODIGO": st.column_config.Column("Código", width="small"),
                    "Estado MD4C": st.column_config.Column("Estado MD4C", width="medium"),
                }
            )

        # --- Métricas debajo ---
        st.container(border=False, height=10)
        cols = st.columns(len(estados_unicos))
        for i, estado in enumerate(estados_unicos):
            valor = conteo[estado]
            porcentaje = valor / total * 100
            cols[i].metric(estado, f"{valor}", f"{porcentaje:.1f}%", label_visibility="visible")

        style_metric_cards(border_left_color="#ff9800")



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
                    firm=get_firm(),
                )
                DB.insert('pedidos', values=pedido.to_sql())
                st.session_state.pedidos += 1
                if mail:
                    send_mail()
                st.rerun()

    @st.dialog('✏️ INFO/EDIT GPI', width='medium')
    def edit(pedido: ORM.Pedido) -> None:
        st.header(pedido.id, divider='blue')
        info = st.text_area('INFO / DESCRIPCIÓN', value=pedido.info, height=1)
        contraseña = st.text_input('CONTRASEÑA', value=pedido.contraseña)
        # b_units = get_business_units(st.session_state.bu)['id'].to_list()
        # bu_id = st.selectbox('BUSINESS UNIT', options=b_units, index=b_units.index(pedido.bu_id), accept_new_options=False)
        fecha_ini = st.date_input('FECHA INICIO', value=pedido.fecha_ini, format='YYYY-MM-DD')
        fecha_fin = st.date_input('FECHA FIN', value=pedido.fecha_fin, format='YYYY-MM-DD')
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        planificador = st.selectbox('PLANIFICADOR', options=usuarios, index=usuarios.index(pedido.planificador), accept_new_options=False)
        alarma_indx = pedido.alarma - 1 if isinstance(pedido.alarma, int) else None
        alarma_color = st.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
        alarma_id = Alarmas.get_int(alarma_color)
        btn_mod = st.button('MODIFICAR', width='stretch', icon='✏️')
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
                args = {
                    'info': info,
                    'contraseña': contraseña,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin, 
                    'planificador': planificador, 
                    'alarma': alarma_id, 
                }
                values = dict()
                for k, v in args.items():
                    old = getattr(pedido, k)
                    new = v
                    if isinstance(old, datetime) or isinstance(old, date): old = old.strftime(r'%Y-%m-%d')
                    if isinstance(new, datetime) or isinstance(new, date): new = new.strftime(r'%Y-%m-%d')
                    if new != old:
                        mod.data[k] = {
                            'old': old,
                            'new': new,
                        }
                        values[k] = new
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

    def report(df: pd.DataFrame) -> bool:
        columns_df = df.columns.to_list()
        for col in ['DB', 'film']: columns_df.remove(col)
        file_name = r'report_pedidos.xlsx'
        path_file = os.path.join('temp', file_name)
        if os.path.exists(path_file):
            os.remove(path_file)
        return True

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
        btn_report = holder_report.button('REPORT .xlsx', icon=r':material/docs:', width='stretch', key='btn_pedidos_report') # , on_click=report_pedidos
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

            columns = ['id', 'info', '#', 'bu_id', 'planificador', 'fecha_ini', 'fecha_fin', '∑_hitos', '∑_acciones', 'LM', 'DT', 'PL', 'PR', 'EM', 'CA',
                'pde_retraso_dias',
                'pde_material_critico',
                'pde_description',
                'pde_actualizado',
                'pde_usuario',
            ]
            columns_config = {
                'id': st.column_config.Column('GPI', width=None, pinned=True),
                'info': st.column_config.Column('DESCRIPCIÓN GPI', width=None, pinned=True),
                '#': st.column_config.Column('#', width=50, pinned=False),
                'bu_id': st.column_config.Column('BUS. UNIT', width='small'),
                'planificador': st.column_config.Column('IP', width='small'),
                'fecha_ini': st.column_config.DatetimeColumn('FECHA INICIO', format="YYYY-MM-DD", width='small'),
                'fecha_fin': st.column_config.DatetimeColumn('FECHA FIN', format="YYYY-MM-DD", width='small'),
                '∑_hitos': st.column_config.NumberColumn('∑ HITOS', width=50),
                '∑_acciones': st.column_config.NumberColumn('∑ ACCIONES', width=50),
                'pde_retraso_dias': st.column_config.NumberColumn('PDE RETRASO (Días)', width='small'),
                'pde_material_critico': st.column_config.Column('PDE MATERIAL CRÍTICO', width='small'),
                'pde_description': st.column_config.Column('PDE DESCRIPCIÓN', width='small'),
                'pde_actualizado': st.column_config.DatetimeColumn('PDE ACTUALIZACIÓN', format="YYYY-MM-DD", width='small'),
                'pde_usuario': st.column_config.Column('PDE USUARIO', width='small'),
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
    def new(pedido_id: str) -> None:
        col_alert, col_bu, col_user = st.columns(3)
        alarma_color = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, horizontal=True)
        alarma_id = Alarmas.get_int(alarma_color)        
        departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
        responsable      = col_user.selectbox('RESPONSABLE', options=get_usuarios(st.session_state.usuarios), index=None, accept_new_options=False)

        nombre = st.text_area('DESCRIPCIÓN DEL HITO', value=None)
        grupo = st.text_input('GRUPO')
        fecha_req = st.date_input('FECHA REQUERIDA', value=None, min_value=datetime(2024,1,1), format='YYYY-MM-DD')
        fecha_plan = st.date_input('FECHA PLANIFICADA', value=None, min_value=datetime(2024,1,1), format='YYYY-MM-DD')
        cantidad = st.number_input('CANTIDAD', min_value=1, max_value=None, value=1, label_visibility='visible')

        if st.button('AÑADIR HITO', icon='🔄️', width='stretch'):
            if not grupo or not nombre or not fecha_req or not fecha_plan or not responsable:
                st.warning("RELLENA TODOS LOS DATOS", icon='⚠️')
            else:
                mod = Modificacion(
                    fecha=datetime.now(),
                    info='Creación de hito',
                    data=None,
                    user=st.session_state.login.id
                )
                hito = ORM.Hito(
                    id=None,
                    pedido_id=pedido_id,
                    grupo=grupo,
                    nombre=nombre,
                    fecha_req=fecha_req,
                    fecha_plan=fecha_plan,
                    departamento=departamento,
                    responsable=responsable,
                    alarma=alarma_id,
                    estado=1,
                    info=None,
                    DB={
                        'modificaciones': [mod.to_dict()],
                        'cantidad': cantidad
                    },
                    firm=get_firm()
                )
                DB.insert('hitos', values=hito.to_sql())
                st.session_state.hitos += 1
                st.rerun()

    @st.dialog('✏️ INFO/EDIT HITO', width='medium')
    def edit(hito: ORM.Hito) -> None:
        st.write(hito.pedido_id, '/', hito.grupo)

        col_alert, col_bu, col_user = st.columns(3)

        alarma_indx = hito.alarma - 1 if isinstance(hito.alarma, int) else None
        alarma_color = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
        alarma_id = Alarmas.get_int(alarma_color)
        departamentos = get_departamentos(st.session_state.departamentos)['id'].tolist()
        departamento_indx = departamentos.index(hito.departamento)
        departamento = col_bu.selectbox('DEPARTAMENTO', options=departamentos, index=departamento_indx, accept_new_options=False)
        
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        usuario_indx = usuarios.index(hito.responsable)
        responsable = col_user.selectbox('RESPONSABLE', options=usuarios, index=usuario_indx, accept_new_options=False)

        grupo = st.text_input('GRUPO', value=hito.grupo)
        nombre = st.text_area('DESCRIPCIÓN DEL HITO', value=hito.nombre)
        fecha_req = st.date_input('FECHA REQUERIDA', value=hito.fecha_req, format='YYYY-MM-DD')
        fecha_plan = st.date_input('FECHA PLANIFICADA', value=hito.fecha_plan, format='YYYY-MM-DD')
        old_cantidad = hito.DB.get('cantidad', None)
        cantidad = st.number_input('CANTIDAD', min_value=1, max_value=None, value=old_cantidad, label_visibility='visible')
        # info = st.text_area('INFO / DESCRIPCIÓN', value=hito.info, height=1)

        estados = Estados.get_estados_icon()
        estado_indx = estados.index(hito.estado) if hito.estado in estados else None
        estado_icon = st.radio('ESTADO', options=estados, index=estado_indx, horizontal=True)
        estado_id = Estados.get_id(estado_icon)

        btn_mod = st.button('MODIFICAR', width='stretch', icon='✏️')
        info_mod = st.text_area('INFO MODIFICACIÓN', height=1)
        mail = st.checkbox('ENVIAR MAIL')

        if btn_mod:
            if not info_mod:
                st.warning("INDICA EL MOTIVO DE LA MODIFICACIÓN", icon='⚠️')
            else:

                mod = Modificacion(
                    fecha=datetime.now(),
                    info=info_mod,
                    data=dict(),
                    user=st.session_state.login.id
                )
                args = {
                    'alarma': alarma_id, 
                    'departamento': departamento,
                    'responsable': responsable,
                    'grupo': grupo,
                    'nombre': nombre,
                    'fecha_req': fecha_req,
                    'fecha_plan': fecha_plan, 
                    # 'cantidad': cantidad,
                    'estado': estado_id,  
                }
                values = dict()
                for k, v in args.items():
                    old = getattr(hito, k)
                    new = v
                    if isinstance(old, datetime) or isinstance(old, date): old = old.strftime(r'%Y-%m-%d')
                    if isinstance(new, datetime) or isinstance(new, date): new = new.strftime(r'%Y-%m-%d')
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
                values['DB']['cantidad'] = cantidad
                values['DB'] = json.dumps(values['DB'])

                if mail:
                    send_mail()
                
                DB.update('hitos', values=values, where={'id': hito.id})
                st.session_state.hitos += 1
                st.rerun()

    @st.dialog('📄 HISTORICO', width='medium')
    def log(hito: ORM.Hito) -> None:
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
                        st.dataframe(pd.DataFrame(rows), hide_index=True)

    def report(df: pd.DataFrame) -> None:
        pass

    def tbl(pedido_id: str = None) -> ORM.Hito:

        ## OPCIONES TABLA
        col_opciones, col_filtros, col_vista = st.columns(3)
        vistas = ['TABLA', 'GANTT']

        with col_opciones.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', key='btn_hitos_new', on_click=Hitos.new, kwargs={'pedido_id': pedido_id})
            holder_report = st.empty() ## BOTON REPORT
            holder_select = st.empty() ## LABEL SELECCION
            holder_edit = st.empty() ## BOTON EDITAR
            holder_accion = st.empty() ## BOTON ACCION
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
        btn_report = holder_report.button('REPORT .xlsx', icon=r':material/docs:', width='stretch', key='btn_hitos_report') # , on_click=report_pedidos
        if btn_report:
            columns_df = df.columns.to_list()
            for col in ['DB', 'firm']: columns_df.remove(col)
            file_name = r'report_hitos.xlsx'
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
        
        df_loc: int = None

        if vista == 'TABLA':
            tbl_holder = st.empty()
            col_height, _, _ = st.columns(3)
            height_holder = col_height.empty()

            columns = [
                'nombre', '#', 'estado', 'id', 'responsable', 'fecha_req', 'fecha_plan', 'Δ', 
                '∑_acciones', 'LM', 'DT', 'PL', 'PR', 'EM', 'CA',
            ]
            
            columns_config = {
                'nombre': st.column_config.Column('DESCRIPCIÓN HITO', width=300, pinned=True),
                '#': st.column_config.Column('#', width=50, pinned=False),
                'estado': st.column_config.Column('ESTADO', width=50, pinned=False),
                'id': st.column_config.Column('id', width=30),
                'responsable': st.column_config.Column('RESPONSABLE', width=None),
                'fecha_req': st.column_config.DatetimeColumn('FECHA REQUERIDA', format="YYYY-MM-DD", width='small'),
                'fecha_plan': st.column_config.DatetimeColumn('FECHA PLANIFICADA', format="YYYY-MM-DD", width='small'),
                'Δ': st.column_config.NumberColumn('Δ Días', width=None),
                '∑_acciones': st.column_config.NumberColumn('∑ ACCIONES', width=50),
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
                # height=tbl_height,
                row_height=40,
                column_config=columns_config
            )
            tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
            df_loc = df.index[tbl_iloc] if tbl_iloc != None else None

        if vista == 'GANNT':
            df_loc = None

        hito: ORM.Hito = None
        if df_loc != None:
            hito = ORM.Hito.from_dict(df.loc[df_loc].to_dict())
            holder_select.write('SELECCIÓN')
            holder_edit.button('EDITAR', width='stretch', icon=':material/edit_square:', key='btn_hitos_edit', on_click=Hitos.edit, kwargs={'hito': hito})
            holder_accion.button('NUEVA ACCION', width='stretch', icon=':material/add_box:', key='btn_hitos_new_action', on_click=Acciones.new, kwargs={'pedido_id': pedido_id, 'hito_id': hito.id})
            holder_historico.button('HISTORICO', width='stretch', icon=':material/history_toggle_off:', key='btn_hitos_log', on_click=Hitos.log, kwargs={'hito': hito})

        return hito

class Acciones:
    @st.dialog('➕ NUEVA ACCIÓN', width='medium')
    def new(pedido_id: str, hito_id: int = None) -> None:
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
                    pedido_id=pedido_id,
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

    @st.dialog('✏️ INFO/EDIT ACCIÓN', width='medium')
    def edit(accion: ORM.Accion) -> None:
        # causa_indx = Causas.get_ids().index(accion.causa) if accion.causa in Causas.get_ids() else None
        # causa = st.selectbox('CAUSA', options=Causas.get_values(), index=causa_indx, accept_new_options=False)
        # causa_id = Causas.get_ids()[Causas.get_values().index(causa)] if causa else None
        # info = st.text_area('INFO / DESCRIPCIÓN', value=accion.info, height=1)
        accion_info = st.text_area('ACCIÓN', value=accion.accion, height=1)
        fecha_req = st.date_input('FECHA REQUERIDA', value=accion.fecha_req, format='YYYY-MM-DD')
        usuarios = get_usuarios(st.session_state.usuarios)['id'].to_list()
        usuario_indx = usuarios.index(accion.responsable) if accion.responsable in usuarios else None
        responsable = st.selectbox('RESPONSABLE', options=usuarios, index=usuario_indx, accept_new_options=False)

        col_ala, col_est = st.columns(2)

        alarma_indx = accion.alarma - 1 if isinstance(accion.alarma, int) else None
        alarma_color = col_ala.radio('ALARMA', options=["🟥","🟨","🟩"], index=alarma_indx, horizontal=True)
        alarma_id = Alarmas.get_int(alarma_color)

        estados = Estados.get_estados_icon()
        estado_indx = estados.index(accion.estado) if accion.estado in estados else None
        estado_icon = col_est.radio('ESTADO', options=estados, index=estado_indx, horizontal=True)
        estado_id = Estados.get_id(estado_icon)

        btn_mod = st.button('MODIFICAR', width='stretch', icon='✏️')
        info_mod = st.text_area('INFO MODIFICACIÓN', height=1)
        mail = st.checkbox('ENVIAR MAIL')

        if btn_mod:
            if not info_mod:
                st.warning("INDICA EL MOTIVO DE LA MODIFICACIÓN", icon='⚠️')
            else:
                mod = Modificacion(
                    fecha=datetime.now(),
                    info=info_mod,
                    data=dict(),
                    user=st.session_state.login.id
                )
                args = {
                    # 'alarma': alarma_id, 
                    # 'departamento': departamento,
                    # 'responsable': responsable,
                    # 'grupo': grupo,
                    # 'nombre': nombre,
                    # 'fecha_req': fecha_req,
                    # 'fecha_plan': fecha_plan, 
                    # # 'cantidad': cantidad,
                    # 'estado': estado_id,  
                }
        #         values = dict()
        #         for k, v in args.items():
        #             old = getattr(hito, k)
        #             new = v
        #             if isinstance(old, datetime) or isinstance(old, date): old = old.strftime(r'%Y-%m-%d')
        #             if isinstance(new, datetime) or isinstance(new, date): new = new.strftime(r'%Y-%m-%d')
        #             if new != old:
        #                 mod.data[k] = {
        #                     'old': old,
        #                     'new': new,
        #                 }
        #                 values[k] = new
        #         values['firm'] = get_firm()
        #         values['DB'] = hito.DB
        #         if not values['DB'].get('modificaciones'):
        #             values['DB']['modificaciones'] = []
        #         values['DB']['modificaciones'].append(mod.to_dict())
        #         values['DB']['cantidad'] = cantidad
        #         values['DB'] = json.dumps(values['DB'])

        #         if mail:
        #             send_mail()
                
        #         DB.update('hitos', values=values, where={'id': hito.id})
        #         st.session_state.hitos += 1
        #         st.rerun()

    @st.dialog('📄 HISTORICO', width='medium')
    def log(accion: ORM.Accion) -> None:
        modificaciones = accion.DB.get('modificaciones', None)
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

    def report(df: pd.DataFrame) -> None:
        pass

    def tbl(pedido_id: str = None, hito_id: int = None, f_key: str = None) -> ORM.Accion:

        col_options, col_filtros, col_vista = st.columns(3)

        with col_options.expander('OPCIONES', icon='🔧', width='stretch'):
            st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Acciones.new, kwargs={'pedido_id': pedido_id, 'hito_id': hito_id}, key=f'accion_options_new_{f_key}')
            holder_report = st.empty() ## BOTON REPORT
            holder_select = st.empty() ## LABEL SELECCION
            holder_edit = st.empty() ## BOTON EDITAR
            holder_historico = st.empty() ## BOTON HISTORICO
            st.write('TABLA')
            with st.container(border=True):
                height = st.slider(label='ALTO TABLA', label_visibility='visible', min_value=40, max_value=1000, value=40, key=f'sl_acciones_tbl_{f_key}')
                row_height = st.slider(label='ALTO FILA', label_visibility='visible', min_value=40, max_value=300, value=40, key=f'sl_acciones_row_{f_key}')

        with col_filtros.expander('FILTROS', icon='🔍', width='stretch'):
            filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍', key=f'tx_acciones_filter_{f_key}')
            # filter_user = st.selectbox('PLANIFICADOR (IP)', options=get_usuarios()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False, key='filter_user_hitos')
            filter_alert = st.radio(
                'ALARMA', 
                options=["All", "🟥","🟨","🟩"], 
                label_visibility='visible', width='content', 
                horizontal=True,
                key=f'rad_acciones_alert_{f_key}'
            )
            filter_estado = st.radio(
                'ESTADO', 
                options=["All"] + Estados.get_estados_icon(), 
                label_visibility='visible', width='content', 
                horizontal=True,
                key=f'rad_acciones_estado_{f_key}'
            )

        df = get_acciones(pedido_id=pedido_id, hito_id=hito_id)
        if filter_str != str():
            mask = df.select_dtypes(include=['object']).apply(
                lambda col: col.str.contains(filter_str, case=False, na=False)
            ).any(axis=1)
            df = df[mask]
        df = df[df['alarma']==Alarmas.get_int(filter_alert)] if filter_alert in Alarmas.colors() else df
        df = df[df['estado']==filter_estado] if filter_estado in Estados.get_estados_icon() else df


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
            height=height if height > 40 else 'auto',
            row_height=row_height,
            column_config=columns_config,
            key=f'df_acciones_{f_key}'
        )
        tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None
        df_loc = df.index[tbl_iloc] if tbl_iloc != None else None


        accion: ORM.Accion = None
        if df_loc != None:
            accion = ORM.Accion.from_dict(df.loc[df_loc].to_dict())
            holder_select.write('SELECCIÓN')
            holder_edit.button('EDITAR', width='stretch', icon=':material/edit_square:', key=f'btn_acciones_edit_{f_key}', on_click=Acciones.edit, kwargs={'accion': accion})
            holder_historico.button('HISTORICO', width='stretch', icon=':material/history_toggle_off:', key=f'btn_acciones_log_{f_key}', on_click=Acciones.log, kwargs={'accion': accion})

        return accion
