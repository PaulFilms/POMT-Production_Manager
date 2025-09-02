import streamlit as st
from functions import *

if not 'login_count' in st.session_state: st.session_state.login_count = 0

@st.dialog('LOGIN', width='medium')
def login(username, password) -> tuple:
    # if DB.execute(f'SELECT COUNT (*) FROM usuarios WHERE id=? or mail=?;', values=[username.lower(), username.lower()], fetch=1)[0] != 1:
    #     return False
    
    # data = DB.execute('SELECT * FROM usuarios WHERE id=? or mail=?;', values=[username.lower(), username.lower()], fetch=1)[0]
    # return data

    if not username or username == str() or not password or password == str():
        st.warning('RELLENA LOS DATOS', icon='⚠️')
        return
    
    if DB.execute(f'SELECT COUNT (*) FROM usuarios WHERE id=? or mail=?;', values=[username.lower(), username.lower()], fetch=1)[0] != 1:
        st.warning('LOGIN ERROR', icon='⚠️')
        st.session_state.login_count += 1


_, col, _ = st.columns(3)

with col:

    username = st.text_input('Id USUARIO / MAIL')
    password = st.text_input('PASSWORD', type='password')
    st.container(border=False, height=10)
    st.button('LOG IN', icon='🙋‍♂️', width='stretch', on_click=lambda: login(username, password))
        

        # if 
        # else:


        
        # if login_(username, password)
        # elif not login_(username, password):
        #     st.warning('LOGIN ERROR', icon='⚠️')
        #     st.session_state.login_count += 1
        
        # st.session_state.login = {'usuario_id': }

