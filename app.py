import os
import streamlit as st
from functions import *

st.set_page_config(
    page_title="PPI Project (⚠️ Under Contruction)",
    # page_icon='🎛️',
    page_icon=r'assets\logo.svg',
    layout="wide", # "centered",
    initial_sidebar_state= "auto" # "collapsed"
)

def session_state_start():
    if not 'login' in st.session_state: st.session_state.login = None
    if not 'login_count' in st.session_state: st.session_state.login_count = 1
    if not 'dialog' in st.session_state: st.session_state.dialog = 'ℹ️ INFO'
    if not 'usuarios' in st.session_state: st.session_state.usuarios = 1
    if not 'pedidos' in st.session_state: st.session_state.pedidos = 1
    if not 'hitos' in st.session_state: st.session_state.hitos = 1
    if not 'bu' in st.session_state: st.session_state.bu = 1
    if not 'departamentos' in st.session_state: st.session_state.departamentos = 1
    if not 'action' in st.session_state: st.session_state.action = 1
    if not 'productos' in st.session_state: st.session_state.productos = 1

if not os.path.exists('temp'): os.mkdir('temp')

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
            st.session_state.login = Usuario.get_form_sql(data)
            st.rerun()

def logout():
    st.session_state.login = None


if __name__ == '__main__':

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


    ## LOGIN / ROLES

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
            ],
            'WORK': [
                pg_bi_dashboards,
                pg_business_unit,
                pg_pedidos,
            ],
            'UNDER TEST': [
                pg_chat_ia,
                pg_productos,
                pg_gantt,
            ]
        }

    # PG.run()
    st.navigation(page_config).run()