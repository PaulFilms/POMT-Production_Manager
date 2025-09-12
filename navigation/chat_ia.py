import streamlit as st

if not 'conver' in st.session_state:
    st.session_state.conver = list()

st.write(st.session_state.conver)

col1, col2, col3 = st.columns(3)

# with col1:


prompt = st.chat_input('EN QUE TE PUEDO AYUDAR ?', accept_file=True)
# st.write(prompt)

if prompt:
    # st.write(f"*ADMIN: {prompt}")
    st.session_state.conver.append(prompt)