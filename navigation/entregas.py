

import streamlit as st
from frontend import session_state_start, get_firm, Pedidos
from functions import *

session_state_start()

## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

class UI:

    @st.dialog('➕ NUEVO HITO', width='medium')
    def new(pedido_id: str) -> None:

        col_alert, col_bu, col_user = st.columns(3)
        alarma          = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, label_visibility='visible', width='content', horizontal=True)
        departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
        responsable      = col_user.selectbox('RESPONSABLE', options=get_usuarios_by_dept(departamento), index=None, accept_new_options=False)

        grupo = st.text_input('GRUPO')
        nombre = st.text_area('INFO / DESCRIPCIÓN', value=None)
        fecha_req = st.date_input('FECHA REQUERIDA', value=None, min_value=datetime(2025,1,1), format='YYYY-MM-DD')
        fecha_plan = st.date_input('FECHA PLANIFICADA', value=None, min_value=datetime(2025,1,1), format='YYYY-MM-DD')


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
    def tbl_hitos():

        ## OPTIONS
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

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

# col_hitos_options, col_hitos_filtros, col_hitos_vista = st.columns(3)

# with col_hitos_options:
#     st.button('NUEVO', width='stretch', icon=':material/add_box:', on_click=Hitos.new_hito, kwargs={'pedido_id': pedido_id})
#     # st.button('EDITAR', width='stretch', icon=':material/edit_square:', disabled=opt_edit) # edit_square
#     edit_holder = st.empty()

pedido = Pedidos.tbl()

print(pedido)