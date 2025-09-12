'''
## ⚠️ WARNINGS:
- BUG: update_xlsx / El caso cuando ya existe el pedido 
'''
import tempfile, json
from enum import Enum
from datetime import datetime, date
from typing import Any, List, Dict
import pandas as pd
from pyreports.xlsx import *
# from mysqlite import SQL

import streamlit as st
from streamlit_timeline import timeline # https://pypi.org/project/streamlit-timeline/
from functions import *

session_state_start()


## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

file_name = "pedidosPorPosicion.xlsx"

if not 'iloc' in st.session_state: st.session_state.iloc = None

def update_xlsx(path_xlsx):
    xlsx = XLSREPORT(path_xlsx, 'Pedidos')
    max_row = xlsx.wb.active.max_row
    max_col = xlsx.wb.active.max_column

    header_row = 9
    headers: list[str] = [f"{col+1}@{xlsx.rd(row=9, column=col+1)}" for col in range(max_col)]

    for row in range(header_row, max_row): 
        row_data = dict()
        for h in headers:
            value = xlsx.rd(row=row+1, column=headers.index(h)+1)
            if isinstance(value, datetime):
                value = value.strftime(r'%Y-%m-%d')
            row_data[h] = value

        id = row_data['1@Código de pedido']
        db_data = json.dumps({'xlsx': row_data})

        count = DB.execute('SELECT COUNT (*) FROM pedidos WHERE id=?',values=[id], fetch=1)[0]
        if count == 0:
            values = {'id': id, 'firm': st.session_state.login.get_firm(), 'DB': db_data}
            DB.insert('pedidos', values)
            st.session_state.pedidos += 1
        else:
            ## BUG
            print('Ya existe:', id)
            # db_data = DB.select(f'SELECT DB FROM pedidos WHERE id="{id}"')
            # db_data = json.loads(db_data)
            # print(db_data, type(db_data))
            # if db_data != row_data:
            #     st.warning("⚠️ MODIFICAR")
                # st.write(row_data)
            DB.update_json('pedidos', 'DB', 'id', id, db_data)
            DB.update(table='pedidos', values={'firm': st.session_state.login.get_firm()}, where={'id': id})
    
    st.rerun()

def st_timeline(dataframe: pd.DataFrame):

    # # CSS para ocultar el encabezado de Streamlit (y filas de menú)
    # hide_style = """
    # <style>
    # header {visibility: hidden;}
    # #MainMenu {visibility: hidden;}
    # </style>
    # """

    # st.markdown(hide_style, unsafe_allow_html=True)
    # timeline(json.dumps(time_data))

    # svg_size = 250, 63
    # svg_str = f'''
    # <svg width="{svg_size[0]}" height="{svg_size[1]}" viewBox="0 0 250 63" fill="none" xmlns="http://www.w3.org/2000/svg">
    # <path d="M17.3076 0.5H232.689L233.133 0.501953V0.50293C237.749 0.561458 241.885 1.53666 244.849 3.05469C247.84 4.58692 249.5 6.5903 249.5 8.65625V54.3438C249.5 56.4428 247.786 58.4777 244.707 60.0176C241.658 61.5425 237.411 62.5 232.692 62.5H17.3076C12.5891 62.5 8.34195 61.5425 5.29297 60.0176C2.21422 58.4777 0.50013 56.4428 0.5 54.3438V8.66895L0.505859 8.44531L0.504883 8.44434C0.616465 6.38925 2.37587 4.40684 5.43652 2.91211C8.47494 1.42827 12.6632 0.50001 17.3076 0.5Z" fill="#004254" stroke="#004254"/>
    # <path d="M46.541 26.4385C46.541 29.2542 45.9062 31.5329 44.6367 33.2744C43.3672 35.016 41.6501 36.2692 39.4854 37.0342C37.3206 37.7829 34.8792 38.1572 32.1611 38.1572C31.8844 38.1572 31.2985 38.141 30.4033 38.1084C29.5081 38.0596 28.9222 38.027 28.6455 38.0107C28.3688 37.9945 28.0514 37.9782 27.6934 37.9619V50.999C27.6934 51.292 27.5957 51.5361 27.4004 51.7314C27.2214 51.9105 27.0016 52 26.7412 52H21.7607C21.484 52 21.248 51.9023 21.0527 51.707C20.8574 51.5117 20.7598 51.2757 20.7598 50.999V16.5996C20.7598 15.7695 21.2887 15.2731 22.3467 15.1104C25.1136 14.6709 28.3851 14.4512 32.1611 14.4512C34.1794 14.4512 36.0511 14.6465 37.7764 15.0371C39.5016 15.4277 41.0153 16.0706 42.3174 16.9658C43.6357 17.8447 44.6693 19.041 45.418 20.5547C46.1667 22.0684 46.541 23.8831 46.541 25.999V26.4385ZM39.6562 26.4385V25.999C39.6562 23.932 39.0459 22.4508 37.8252 21.5557C36.6208 20.6442 34.7327 20.1885 32.1611 20.1885C31.5101 20.1885 30.68 20.221 29.6709 20.2861C28.6618 20.335 28.0026 20.3757 27.6934 20.4082V32.2979C29.3047 32.3955 30.7939 32.4443 32.1611 32.4443C33.9515 32.4443 35.3919 32.2327 36.4824 31.8096C37.5729 31.3701 38.3704 30.7109 38.875 29.832C39.3958 28.9531 39.6562 27.8219 39.6562 26.4385ZM74.1045 50.6572C74.1045 51.2757 73.7708 51.6257 73.1035 51.707C72.7129 51.7559 72.2409 51.8291 71.6875 51.9268C71.1504 52.0081 70.361 52.0895 69.3193 52.1709C68.2939 52.2523 67.4557 52.3092 66.8047 52.3418C66.1536 52.3743 65.0876 52.3906 63.6064 52.3906C61.2139 52.3906 59.1794 52.1139 57.5029 51.5605C55.8265 50.9909 54.5 49.9574 53.5234 48.46C52.5469 46.9463 52.0586 44.8467 52.0586 42.1611V24.7051C52.0586 22.0195 52.5469 19.9199 53.5234 18.4062C54.5 16.8926 55.8265 15.859 57.5029 15.3057C59.1794 14.736 61.2139 14.4512 63.6064 14.4512C66.2594 14.4512 68.1963 14.5163 69.417 14.6465C70.654 14.7604 71.8828 14.9313 73.1035 15.1592C73.4941 15.208 73.7546 15.3057 73.8848 15.4521C74.0312 15.5986 74.1045 15.8509 74.1045 16.209V19.4072C74.1045 19.6514 73.9987 19.8792 73.7871 20.0908C73.5755 20.3024 73.3477 20.4082 73.1035 20.4082H62.8984C61.4336 20.4082 60.4082 20.7174 59.8223 21.3359C59.2363 21.9544 58.9434 23.0775 58.9434 24.7051V30.1006H72.4932C72.8024 30.1006 73.0465 30.1901 73.2256 30.3691C73.4046 30.5482 73.4941 30.7923 73.4941 31.1016V34.6904C73.4941 34.9834 73.3965 35.2275 73.2012 35.4229C73.0059 35.6019 72.7699 35.6914 72.4932 35.6914H58.9434V42.1611C58.9434 43.7725 59.2363 44.8955 59.8223 45.5303C60.4082 46.1488 61.4336 46.458 62.8984 46.458H73.1035C73.3802 46.458 73.6162 46.5557 73.8115 46.751C74.0068 46.9463 74.1045 47.1823 74.1045 47.459V50.6572ZM107.698 37.1074C107.698 39.5977 107.348 41.7868 106.648 43.6748C105.965 45.5628 104.956 47.1579 103.621 48.46C102.303 49.7458 100.659 50.7223 98.6895 51.3896C96.7201 52.057 94.4902 52.3906 92 52.3906C90.6491 52.3906 88.8669 52.3255 86.6533 52.1953C84.4561 52.0651 82.9587 51.9349 82.1611 51.8047C81.2985 51.6582 80.8672 51.1374 80.8672 50.2422V16.5996C80.8672 15.7207 81.2985 15.208 82.1611 15.0615C82.8936 14.915 84.2526 14.7767 86.2383 14.6465C88.2402 14.5163 90.1608 14.4512 92 14.4512C94.4902 14.4512 96.7201 14.7848 98.6895 15.4521C100.659 16.1195 102.303 17.1042 103.621 18.4062C104.956 19.6921 105.965 21.279 106.648 23.167C107.348 25.0387 107.698 27.236 107.698 29.7588V37.1074ZM100.813 37.1074V29.7588C100.813 27.3662 100.439 25.4782 99.6904 24.0947C98.958 22.695 97.9408 21.7184 96.6387 21.165C95.3366 20.5954 93.7904 20.3105 92 20.3105C91.235 20.3105 90.7223 20.3187 90.4619 20.335C90.2178 20.335 89.8271 20.3512 89.29 20.3838C88.7529 20.4001 88.2565 20.4245 87.8008 20.457V46.4092C89.9004 46.5068 91.3001 46.5557 92 46.5557C94.7832 46.5557 96.9479 45.8558 98.4941 44.4561C100.04 43.0563 100.813 40.6068 100.813 37.1074ZM121.15 50.999C121.15 51.292 121.053 51.5361 120.857 51.7314C120.662 51.9105 120.426 52 120.149 52H115.218C114.941 52 114.705 51.9023 114.51 51.707C114.314 51.5117 114.217 51.2757 114.217 50.999V15.7939C114.217 15.5335 114.306 15.3138 114.485 15.1348C114.681 14.9395 114.925 14.8418 115.218 14.8418H120.149C120.442 14.8418 120.678 14.9313 120.857 15.1104C121.053 15.2731 121.15 15.501 121.15 15.7939V50.999ZM155.501 37.1074C155.501 39.5977 155.151 41.7868 154.451 43.6748C153.768 45.5628 152.758 47.1579 151.424 48.46C150.105 49.7458 148.462 50.7223 146.492 51.3896C144.523 52.057 142.293 52.3906 139.803 52.3906C138.452 52.3906 136.67 52.3255 134.456 52.1953C132.259 52.0651 130.761 51.9349 129.964 51.8047C129.101 51.6582 128.67 51.1374 128.67 50.2422V16.5996C128.67 15.7207 129.101 15.208 129.964 15.0615C130.696 14.915 132.055 14.7767 134.041 14.6465C136.043 14.5163 137.964 14.4512 139.803 14.4512C142.293 14.4512 144.523 14.7848 146.492 15.4521C148.462 16.1195 150.105 17.1042 151.424 18.4062C152.758 19.6921 153.768 21.279 154.451 23.167C155.151 25.0387 155.501 27.236 155.501 29.7588V37.1074ZM148.616 37.1074V29.7588C148.616 27.3662 148.242 25.4782 147.493 24.0947C146.761 22.695 145.743 21.7184 144.441 21.165C143.139 20.5954 141.593 20.3105 139.803 20.3105C139.038 20.3105 138.525 20.3187 138.265 20.335C138.021 20.335 137.63 20.3512 137.093 20.3838C136.556 20.4001 136.059 20.4245 135.604 20.457V46.4092C137.703 46.5068 139.103 46.5557 139.803 46.5557C142.586 46.5557 144.751 45.8558 146.297 44.4561C147.843 43.0563 148.616 40.6068 148.616 37.1074ZM189.51 36.79C189.51 40.3382 188.908 43.2842 187.703 45.6279C186.499 47.9554 184.822 49.6644 182.674 50.7549C180.525 51.8454 178.051 52.3906 175.252 52.3906C172.436 52.3906 169.954 51.8454 167.806 50.7549C165.674 49.6481 164.005 47.931 162.801 45.6035C161.613 43.2598 161.019 40.3219 161.019 36.79V30.0518C161.019 26.5199 161.613 23.5902 162.801 21.2627C164.005 18.9189 165.674 17.2018 167.806 16.1113C169.954 15.0046 172.436 14.4512 175.252 14.4512C178.051 14.4512 180.525 14.9964 182.674 16.0869C184.822 17.1774 186.499 18.8945 187.703 21.2383C188.908 23.5658 189.51 26.5036 189.51 30.0518V36.79ZM182.503 36.79V30.0518C182.503 26.764 181.909 24.3551 180.721 22.8252C179.549 21.279 177.726 20.5059 175.252 20.5059C172.794 20.5059 170.971 21.279 169.783 22.8252C168.595 24.3551 168.001 26.764 168.001 30.0518V36.79C168.001 40.0615 168.595 42.4785 169.783 44.041C170.971 45.5872 172.794 46.3604 175.252 46.3604C177.726 46.3604 179.549 45.5872 180.721 44.041C181.909 42.4785 182.503 40.0615 182.503 36.79ZM218.538 41.9414C218.538 44.8548 217.496 47.3288 215.413 49.3633C213.346 51.3815 210.009 52.3906 205.403 52.3906C202.099 52.3906 199.145 52.0977 196.541 51.5117C195.906 51.349 195.589 51.0153 195.589 50.5107V46.8975C195.589 46.637 195.678 46.4173 195.857 46.2383C196.053 46.043 196.281 45.9453 196.541 45.9453H196.639C197.55 46.043 198.567 46.1325 199.69 46.2139C200.813 46.279 201.888 46.3359 202.913 46.3848C203.938 46.4336 204.801 46.458 205.501 46.458C207.617 46.458 209.106 46.0918 209.969 45.3594C210.848 44.6107 211.287 43.4714 211.287 41.9414C211.287 40.9974 210.994 40.1917 210.408 39.5244C209.822 38.8571 208.699 38.0352 207.039 37.0586L200.447 33.1035C198.95 32.1921 197.762 31.2643 196.883 30.3203C196.004 29.36 195.394 28.359 195.052 27.3174C194.71 26.2757 194.539 25.1527 194.539 23.9482C194.539 21.9951 194.946 20.3268 195.76 18.9434C196.59 17.5436 197.933 16.445 199.788 15.6475C201.66 14.8499 204.077 14.4512 207.039 14.4512C208.634 14.4512 210.424 14.5488 212.41 14.7441C214.412 14.9395 215.82 15.1429 216.634 15.3545C217.236 15.4684 217.537 15.7858 217.537 16.3066V19.9932C217.537 20.2699 217.456 20.4896 217.293 20.6523C217.146 20.8151 216.943 20.8965 216.683 20.8965H216.585C212.923 20.571 209.643 20.4082 206.746 20.4082C203.247 20.4082 201.497 21.5882 201.497 23.9482C201.497 24.7783 201.774 25.5026 202.327 26.1211C202.897 26.7233 203.987 27.4801 205.599 28.3916L211.604 31.7607C214.225 33.193 216.032 34.723 217.024 36.3506C218.034 37.9619 218.538 39.8255 218.538 41.9414Z" fill="white"/>
    # </svg>
    # '''
    # st.markdown(svg_str, unsafe_allow_html=True)

    # st.container(border=False, height=10)


    # st.markdown(f"""
    # <div style="display: flex; align-items: center;">
    #     {svg_str}
    #     # <h1 style="margin-left: 10px;">Título con SVG desde cadena</h1>
    # </div>
    # """, unsafe_allow_html=True)


    ## PLOTLY

    # with st.expander("⌛TIMELINE", expanded=False):
    with st.container(border=True):

        import plotly.express as px # https://python-charts.com/es/evolucion/diagrama-gantt-plotly/

        # df = pd.DataFrame([
        #     dict(Task="Pedido 1", Start='2021-01-01', Finish='2021-03-01'),
        #     dict(Task="Pedido 2", Start='2021-02-15', Finish='2021-06-15'),
        #     dict(Task="Pedido 3", Start='2021-05-01', Finish='2021-09-30'),
        # ])

        df = dataframe # ['id', '#', 'INFO', 'FECHA_FIN_PLAN', 'FECHA_INI_REQ', 'FECHA_FIN_REQ']
        df['Start'] = df['FECHA_INI_REQ'].dt.strftime(r'%Y-%m-%d')
        df['Finish'] = df['FECHA_FIN_REQ'].dt.strftime(r'%Y-%m-%d')

        
        fig = px.timeline(
            df, 
            x_start="Start", x_end="Finish", y="id", 
            # x_start="FECHA_FIN_PLAN", x_end="FECHA_FIN_PLAN", y="id", 
            # title="⌛TIMELINE"
        )
        # fig = px.scatter(
        #     df,
        #     x='FECHA_FIN_PLAN', y='id',
        #     hover_data=['id'],  # muestra el id al pasar el ratón
        # )
        # fig.update_traces(marker=dict(size=10))
        fig.update_yaxes(autorange="reversed")  # Para que se vea de arriba hacia abajo
        # fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        # hoy = pd.Timestamp('today').normalize()

        # fig.add_vline(
        #     x=hoy,
        #     line_width=2,
        #     line_dash="dash",
        #     line_color="red",
        #     annotation_text="Hoy",
        #     annotation_position="top right"
        # )

        st.plotly_chart(fig, width='content')

def st_update():
    st.container(border=False, height=20)

    with st.expander('UPDATE DATA', expanded=False, icon='🧷'):

        xlsx_file = st.file_uploader(
            f'AÑADE EL FICHERO "{file_name}"',
            accept_multiple_files=False,
            label_visibility='visible',
            type=['xlsx']
        )

        if xlsx_file:
            if xlsx_file.name != file_name:
                st.warning(f'⚠️ USA EL FICHERO: {file_name}')
            else:
                if st.button('UPDATE', icon="🔄️", use_container_width=True):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                        tmp.write(xlsx_file.read())
                        tmp_path = tmp.name
                    update(tmp_path)
                    # st.success(f'DATOS ACTUALIZADOS: {datetime.now()}')

@st.dialog('EDITAR PEDIDO', width='medium')
def edit_pedido(x):
    st.radio('ALARMA', options=["🟥","🟨","🟩"], index=None, horizontal=True)
    st.text_area('INFO / DESCRIPCIÓN', value=x['info'], height=1)
    st.text_input('RESPONSABLE', value='')
    st.text_input('RESPONSABLE', value='')
    # st.write(x)

@st.dialog('NUEVA ACCIÓN', width='medium')
def form_accion(pedido_id: str):
    # st.file_uploader('pedidosPorPosicion.xlsx', type=['.xlsx'], accept_multiple_files=False)
    # st.file_uploader('Seguimiento plan de entregas_ING_Navales.xlsx', type=['.xlsx'], accept_multiple_files=False)
    
    col_alert, col_bu, col_user = st.columns(3)

    alarma          = col_alert.radio('ALARMA', options=["🟥","🟨","🟩"], label_visibility='visible', width='content', horizontal=True)
    departamento    = col_bu.selectbox('DEPARTAMENTO', options=get_departamentos(st.session_state.departamentos)['id'].tolist(), index=None, accept_new_options=False)
    usuario_id      = col_user.selectbox('RESPONSABLE', options=get_usuarios_by_dept(departamento), index=None, accept_new_options=False)
    causa           = st.selectbox('CAUSA TIPO', options=[c.value for c in Causas], index=None, label_visibility='visible', )
    info            = st.text_area('INFO', value='', width='stretch') # height=1, 
    accion          = st.text_area('ACCIÓN', value='', height=1, width='stretch')
    fecha           = st.date_input('FECHA REQUERIDA', min_value=datetime.now().date(), value=None)
    # file            = st.file_uploader('INSERT FILE (PHOTO/PDF/etc)', disabled=True)
    # st.camera_input('INSERT PHOTO')

    st.container(border=False, height=20) ## Separador

    if st.button('UPDATE DATA', icon='🔄️', width='stretch'):
        if not usuario_id \
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
                'usuario_id': usuario_id,
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

def tbl_pedidos(df: pd.DataFrame) -> int:
    pedidos_columns = ['id', '#', 'info', 'bu_id', 'FECHA_INI', 'FECHA_FIN', '∑']
    for c in Causas: pedidos_columns.append(c.name)

    ## OPTIONS
    col1, col2, col3 = st.columns(3)

    with col1.popover('TABLE OPTIONS', icon='🔧', width='stretch'):
        tbl_height = st.slider(label='HEIGHT', label_visibility='visible', min_value=200, max_value=1000)
        filter_bunit = st.selectbox('BUSINESS UNIT', options=get_business_units()['id'].tolist(), label_visibility='visible', index=None, accept_new_options=False )
        filter_alert = st.radio('ALERT', options=["All", "🟥","🟨","🟩"], label_visibility='visible', width='content')
        # btn_update = st.button('UPDATE FROM *.xlsx', icon='🧷', width='content', on_click=update_cosas, help=f'Actualizar los datos de pedidos desde el fichero <{file_name}>', use_container_width=True)
        # st.file_uploader("ACTUALIZAR DATOS DESDE .xlsx")
    
    with col3:
        filter_str = st.text_input('FILTER', label_visibility='collapsed', icon='🔍')

    ## DATAFRAME
    # df = get_pedidos(st.session_state.pedidos)
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
    
    ## TABLE
    columns_config = {
        '#': st.column_config.Column('#', width=10),
        'info': st.column_config.Column('info', width='small'),
        'FECHA_INI': st.column_config.DatetimeColumn('FECHA_INI', format="YYYY-MM-DD", width='small'),
        'FECHA_FIN': st.column_config.DatetimeColumn('FECHA_FIN', format="YYYY-MM-DD", width='small'),
        '∑': st.column_config.NumberColumn('∑', width=10)
    }
    for c in Causas:
        columns_config[c.name] = st.column_config.Column(c.name, width=10, help=c.value)
    
    tbl = st.dataframe(
        df_filter4,
        hide_index=True,
        width='stretch',
        selection_mode='single-row',
        on_select='rerun',
        height=tbl_height,
        row_height=40,
        column_config=columns_config
    )

    tbl_iloc: int = tbl.selection['rows'][0] if tbl.selection['rows'] != [] else None

    if tbl_iloc is not None:
        if col2.button('EDITAR PEDIDO', icon='✏️', width='stretch'):
            edit_pedido(df.iloc[tbl_iloc].to_dict())

    return tbl_iloc

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

def get_portadas(**kwargs):
    ## PEDIDO / PORTADA
    time_data = {
        # "title": {
        #     'start_date': {"year": 2025, "month": 1, "day": 1},
        #     'end_date': {"year": 2026, "month": 1, "day": 1},
        #     "text": {"headline": kwargs['pedido'], "text": kwargs['info']},
        #     'media': {
        #         'url': r'https://xtb.scdn5.secure.raxcdn.com/default/0103/99/screenshot-2025-02-05-130401.png',
        #         # 'caption': 'la caption'
        #     }
        # },
        "groups": [
            {"id": "pedido", "content": "Pedido"},
            {"id": "hitos", "content": "Hitos"},
            {"id": "acciones", "content": "Acciones"},
        ],
        'events': [
            {
                'start_date': {"year": 2025, "month": 1, "day": 1},
                'end_date': {"year": 2026, "month": 1, "day": 1},
                "text": {"headline": kwargs['pedido'], "text": kwargs['info']},
                'media': {'url': r'https://images.twinkl.co.uk/tw1n/image/private/t_630/u/ux/charts-wiki_ver_1.png'},
                "group": "pedido"
            },
            {
                'start_date': {"year": 2025, "month": 1, "day": 1},
                'end_date': {"year": 2025, "month": 3, "day": 1},
                "text": {"headline": '🟨 LISTA DE MATERIALES', "text": 'LISTA DE MATERIALES \ntexto del hito'},
                "group": "hitos"
            },
            {
                'start_date': {"year": 2025, "month": 3, "day": 2},
                'end_date': {"year": 2025, "month": 6, "day": 1},
                "text": {"headline": '🟩 DOCUMENTACIÓN TÉCNICA', "text": 'DOCUMENTACIÓN TÉCNICA \ntexto del hito'},
                "group": "hitos"
            },

        ]
    }

    ## ACCIONES / EVENTOS
    for idx, fila in kwargs['df_acciones'].iterrows():
        # headline = f'{fila['#']} {fila['estado']} {fila['causa']} | {fila['accion']}'

        fecha_ini: datetime = fila['fecha_accion']
        if fila['fecha_req'] == None:
            fecha_fin = datetime.now()
        else:
            fecha_fin: datetime = fila['fecha_req']

        headline = str()
        if fila['#']: headline += f'{fila['#']}'
        if fila['estado']: headline += f' {fila['estado']}'
        # if fila['causa']: 
        #     causa = Causas[fila['causa']].value
        #     headline += f' {causa}'
        if fila['causa']: headline += f' {fila['causa']}'

        ## HTML
        html_str = str()
        html_str += f'''
        <div style="width: 100%; font-family: Neo Sans, Neo Sans;padding:20px; margin:12px 0; ">
            <b>PEDIDO ID: </b> {fila['pedido_id']}<br>
            <b>PLANIFICADOR: </b> {fila['planificador']}<br>
            <b>RESPONSABLE: </b> {fila['responsable']}<br>
            <b>ACCION ID: </b> {fila['id']}<br>
        </div>
        '''
        # html_str += f"<p>{fila['info']}</p>"
        # html_str += f"<p>{fila['accion']}</p>"
        html_str += UI.generar_card('INFO', fila['info'])
        html_str += UI.generar_card('ACCION', fila['accion'])
        # html_str += UI.generar_card('PLANIFICADOR', fila['planificador'])
        # html_str += UI.generar_card('RESPONSABLE', fila['responsable'])

        html_str += f'''
        <div style="width: 100%; font-family: Neo Sans, Neo Sans; padding:20px; margin:12px 0; ">
            <b>RESPUESTAS</b>
        </div>'''

        for r in fila['DB'].get('respuestas', []):
            for k, v in r.items():
                html_str += UI.generar_card(k, v)

        time_dict = {
            'start_date': {"year": fecha_ini.year, "month": fecha_ini.month, "day": fecha_ini.day},
            'end_date': {"year": fecha_fin.year, "month": fecha_fin.month, "day": fecha_fin.day},
            'text': {
                'headline': headline, 
                # 'headline': f"<h1 style='font-size:24px; color: #333;'>{headline}</h1>", 
                'text': html_str
            },
            "group": "acciones"
        }
        time_data['events'].append(time_dict)

    with st.container(border=True):
        timeline(time_data)

def bi_pedidos():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LISTA MATERIALES", "25%", "+30 días", border=True)
    col2.metric("DOCUMENTACIÓN TECNICA", "12%", "-22 días", border=True)
    col3.metric("LISTA MATERIALES", "100%", "+30 días", border=True)
    col4.metric("LISTA MATERIALES", "25%", "+30 días", border=True)

    data = []



## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

with st.sidebar:
    gpi_view = st.radio("GPI's", options=['By GPI', 'By Table'], index=1)
    # st.write('OPTIONS:')
    # ck_table = st.checkbox('DATA TABLE', value=False)
    # ck_timeline = st.checkbox('TIMELINE', value=False)
    # ck_update = st.checkbox('UPDATE', value=False)
    # st.button('UPDATE', icon='🧷', use_container_width=True)
    # st.divider()

st.logo(r'assets\logo_extend.svg', size='large')

df_pedidos = get_pedidos(st.session_state.pedidos)

if gpi_view == 'By GPI':
    pedido: str = st.selectbox('SELECT GPI', options=df_pedidos['id'].to_list(), index=None)
    if pedido:
        pedido_loc = df_pedidos.loc[df_pedidos['id']==pedido]
        serie = pedido_loc.iloc[0]
        info = serie['info']
        fecha_ini = datetime.fromtimestamp(serie['fecha_ini'])
        fecha_fin = datetime.fromtimestamp(serie['fecha_fin'])
        db_data: dict = serie['DB']
        xlsx_data = db_data.get('xlsx')

if gpi_view == 'By Table':
    pedido_iloc = tbl_pedidos(df_pedidos)
    pedido: str = None

    if pedido_iloc is not None:
        pedido = df_pedidos['id'].iloc[pedido_iloc]
        info = df_pedidos['info'].iloc[pedido_iloc]
        fecha_ini = datetime.fromtimestamp(df_pedidos['fecha_ini'].iloc[pedido_iloc])
        fecha_fin = datetime.fromtimestamp(df_pedidos['fecha_fin'].iloc[pedido_iloc])
        db_data: dict = df_pedidos['DB'].iloc[pedido_iloc]
        xlsx_data = db_data.get('xlsx')

if pedido:
    st.container(border=False, height=10)
    tab_bi, tab_portada, tab_pdca, tab_xlsx  = st.tabs(['📈 BI', 'PORTADA', 'PLAN DE ACCION', 'XLSX DATA'])

    df_acciones = get_acciones(pedido_id=pedido)

    with tab_bi:
        bi_pedidos()
        data = [
            UI.Timeline(hito='PEDIDO', fecha_ini=fecha_ini, fecha_fin=fecha_fin, texto=pedido, color= None)
        ]
        for idx, row in df_acciones.iterrows():
            time_str = f'ACCION {idx} / {row['causa']}'
            tl = UI.Timeline(
                hito=time_str,
                fecha_ini=safe_datetime(row['fecha_accion']),
                fecha_fin=safe_datetime(row['fecha_req']),
                texto=time_str,
                color=row['alarma']
            )
            if not tl.fecha_ini or pd.isna(tl.fecha_ini): 
                tl.fecha_ini = fecha_ini
            if not tl.fecha_fin or pd.isna(tl.fecha_fin): 
                tl.fecha_fin = fecha_fin
            data.append(tl)
        df_gantt = pd.DataFrame(data)
        with st.container(border=True): UI.my_timeline(df_gantt)
        # UI.my_hitoline(df_gantt)
        
        fechas_xlsx = [
            'Fecha aceptación',
            'Fecha de emisión',
            'Fecha entrega',
            'Fecha fin planificada',
            'Fecha fin requerida',
            'Fecha inicio planificada',
            'Fecha inicio requerida',
            'Fecha planificada',
            'Fecha seguimiento',
            'Fecha última revisión',
        ]

        data = [{"hito": f, "fecha": xlsx_data.get(f, None)} for f in fechas_xlsx if xlsx_data.get(f)]
        df_fechas = pd.DataFrame(data)
        df_fechas['fecha'].apply(safe_datetime)
        # st.write(df_fechas)
        # print(df_fechas.info())
        UI.my_hitoline(df_fechas)

    with tab_portada:
        get_portadas(pedido=pedido, info=info, df_acciones=df_acciones)

    with tab_pdca:
        accion_iloc = tbl_acciones(df_acciones)

        if accion_iloc is not None: pass
            # if col_pdca_detalle.button('DETALLE', width='stretch', icon='🔍'):
            #     detalle_accion(df_acciones.iloc[iloc_accion])
            # st.text_area('INFO', value='', width='stretch', ed)
            # with st.container(border=True):
            #     col_accion1, col_accion2 = st.columns(2)
            #     with col_accion1:
            #         causa = df_acciones['causa'].iloc[accion_iloc]
            #         st.write('CAUSA:')
            #         st.caption(Causas[causa].value, width='stretch')
            #         st.text_area('INFO', value=df_acciones['info'].iloc[accion_iloc], width='stretch', height=1, disabled=True)
            #     with col_accion2:
            #         st.write('ESTADO:')
            #         estado_id = df_acciones['estado_id'].iloc[accion_iloc]
                    # st.write(Estados.id_by_estado()[estado_id], Estados.get_estados()[estado_id-1])
                    # st.text_area('accion', value=df_acciones['accion'].iloc[accion_iloc], width='stretch', height=1, disabled=True)
                
                # st.write('INFO:')
                # st.caption(df_acciones['info'].iloc[accion_iloc], width='stretch')
                # st.write('ACCION:')
                # st.caption(df_acciones['accion'].iloc[accion_iloc], width='stretch')

    with tab_xlsx:
        df_xlsx = pd.DataFrame(
            [(k, str(v) if v is not None else "") for k, v in xlsx_data.items()],
            columns=["key", "value"]
        )
        st.write(df_xlsx)
