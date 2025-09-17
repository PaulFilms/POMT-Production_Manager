import streamlit as st

if not 'conver' in st.session_state:
    st.session_state.conver = list()

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________


# st.write(st.session_state.conver)

# col1, col2, col3 = st.columns(3)

# # with col1:


# prompt = st.chat_input('EN QUE TE PUEDO AYUDAR ?', accept_file=True)
# # st.write(prompt)

# if prompt:
#     # st.write(f"*ADMIN: {prompt}")
#     st.session_state.conver.append(prompt)


## TEST
## ____________________________________________________________________________________________________________________________________________________________________

import streamlit as st
import ollama

# Inicializa la conversación si no existe
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("Asistente IA - Demo con Ollama (Mistral)")

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input del usuario
prompt = st.chat_input("Escribe tu pregunta...")

if prompt:
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtener respuesta del modelo local
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = ollama.chat(
                model="mistral",  # puedes cambiar por llama3, gemma, etc.
                messages=st.session_state.messages,
            )
            message = response["message"]["content"]
            st.markdown(message)

    # Guardar respuesta
    st.session_state.messages.append({"role": "assistant", "content": message})
