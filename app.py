import streamlit as st
from functions import login, logout

st.set_page_config(
    page_title="PPI Project (⚠️ Under Contruction)",
    # page_icon='🎛️',
    page_icon=r'assets\logo.svg',
    layout="wide", # "centered",
    initial_sidebar_state= "auto" # "collapsed"
)

## PAGES
# pg_login = st.Page(r'navigation\login.py', title='Log-in', icon=':material/login:')
pg_login = st.Page(login, title='Log-in', icon=':material/login:', default=False)
pg_logout = st.Page(logout, title='Log-out', icon=':material/logout:', default=False)
pg_home = st.Page(r'navigation\home.py', title='HOME', icon=':material/home:', default=True)
pg_user = st.Page(r'navigation\user.py', title='USER', icon=':material/account_circle:', default=True)
pg_pedidos = st.Page(r'navigation\pedidos.py', title='PEDIDOS', icon=':material/box:')
pg_productos = st.Page(r'navigation\productos.py', title='PRODUCTOS', icon=':material/barcode_reader:')
pg_business_unit = st.Page(r'navigation\busines_unit.py', title='BUSINESS UNIT', icon=':material/business_center:')
pg_bi_dashboards = st.Page(r'navigation\bi_dashboards.py', title='BI / DASHBOARDS', icon=':material/monitoring:')
pg_chat_ia = st.Page(r'navigation\chat_ia.py', title='ARTIFICIAL INTELLIGENCE', icon=':material/smart_toy:')
pg_gantt = st.Page(r'navigation\gantt.py', title='GANTT', icon=':material/smart_toy:')

# PG = st.navigation(
#     {
#         'USUARIO': [
#             pg_home,
#             pg_chat_ia,
#         ],
#         'DATOS': [
#             pg_bi_dashboards,
#             pg_business_unit,
#             pg_pedidos,
#             pg_productos,
#         ]
#     }
# )

if not 'login' in st.session_state: st.session_state.login = None

if st.session_state.login == None:
    page_config: dict | list = [
        pg_login,
        pg_home,
    ]
else:
    page_config = {
        '': [
            pg_logout,
            pg_user,
            pg_chat_ia,
        ],
        'WORK': [
            pg_bi_dashboards,
            pg_business_unit,
            pg_pedidos,
            pg_productos,
            pg_gantt,
        ]
    }
    # page_config['🙋‍♂️'].ap

# PG.run()
st.navigation(page_config).run()

# st.switch_page(pg_home)