import os
import streamlit as st
from frontend import *
from functions import *

DEBUGGER: bool = 0

if __name__ == '__main__':

    st.set_page_config(
        page_title="PRODUCTION MNGR", # PODUCTION MANAGER
        page_icon=r'assets/logo.svg',
        layout="wide", # "centered",
        initial_sidebar_state= "auto" # "collapsed"
    )

    if DEBUGGER:
        import debugpy
        # Habilitar depuración sin bloquear
        try:
            if not debugpy.is_client_connected():
                debugpy.listen(("localhost", 5678))
                print("🪲 Debugger escuchando en localhost:5678 (modo no bloqueante)")
        except Exception as e:
            print(f"⚠️{e}")

    if not os.path.exists('temp'): os.mkdir('temp')

    ## LOGIN / ROLES

    # if not 'login' in st.session_state: st.session_state.login = None
    session_state_start()

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
                pg_entregas,
            ],
            'UNDER TEST': [
                # pg_chat_ia,
                # pg_productos,
                # pg_gantt,
                # pg_test,
            ]
        }

    # PG.run()
    st.navigation(page_config).run()