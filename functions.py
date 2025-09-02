import json
from enum import Enum
import pandas as pd
from mysqlite import *
import streamlit as st

path_db = r"PPI.db"
DB = SQL(path_db=path_db)

class Alarmas(Enum):
    red     = ("🟥", 1)
    yellow  = ("🟨", 2)
    green   = ("🟩", 3)

    @classmethod
    def id_by_color(cls):
        return {a.value[1]: a.value[0] for a in cls}
    
    @classmethod
    def colors(cls):
        return [c.value[0] for c in cls]

class Causas(Enum):
    LM = 'LM  |  LISTA DE MATERIALES'
    DT = 'DT  |  DOCUMENTACIÓN TÉCNICA'
    PL = 'PL  |  PEDIDOS LANZADOS'
    PR = 'PR  |  PEDIDOS EN RETRASO'
    EM = 'EM  |  ENTREGA MANUFACTURING EN RIESGO'
    CA = 'CA  |  CAMBIO DE ALCANCE'


## DATA
## ____________________________________________________________________________________________________________________________________________________________________

def session_state_start():
    if not 'login' in st.session_state: st.session_state.login = None
    if not 'pedidos' in st.session_state: st.session_state.pedidos = 1
    if not 'bu' in st.session_state: st.session_state.bu = 1
    if not 'action' in st.session_state: st.session_state.action = 1


@st.dialog('LOGIN', width='small')
def login():
    username = st.text_input('Id USUARIO')
    password = st.text_input('PASSWORD', type='password')
    st.container(border=False, height=10)
    if st.button('LOG IN', icon='🙋‍♂️', width='stretch', 
        # on_click=lambda: login(username, password)
        ):
        if not username or username == str(): #  or not password or password == str()
            st.warning('RELLENA LOS DATOS', icon='⚠️')
        elif DB.execute(f'SELECT COUNT (*) FROM usuarios WHERE id=?;', values=[username.lower()], fetch=1)[0] != 1:
            st.warning('LOGIN ERROR', icon='⚠️')
            st.session_state.login_count += 1
        else:
            data = DB.execute('SELECT * FROM usuarios WHERE id=?;', values=[username], fetch=1)
            st.session_state.login = data
            st.rerun()

def logout():
    st.session_state.login = None

def safe_json_loads(x):
    if pd.isna(x) or x == '' or x is None:
        return {}  # O {} o [] o lo que quieras devolver cuando esté vacío
    try:
        return json.loads(x)
    except json.JSONDecodeError:
        return {}  # Manejo en caso que el json esté mal formado

def get_alerta(blob, field: str):
    if blob is None:
        return None
    try:
        data: dict = json.loads(blob)
        val = data.get(field, None)
        return int(val) if val is not None else None
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return None

# @st.cache_data
def get_business_units(count: int = 0) -> 'pd.DataFrame':
    headers = DB.execute("SELECT * FROM business_unit LIMIT 0", fetch=4)
    data = DB.select('SELECT * FROM business_unit')

    df = pd.DataFrame(data, columns=headers)

    return df

# @st.cache_data
def get_pedidos(count: int = 0) -> 'pd.DataFrame':
    headers = DB.execute("SELECT * FROM pedidos LIMIT 1", fetch=4)
    data = DB.select('SELECT * FROM pedidos')

    df = pd.DataFrame(data, columns=headers)
    # df['#'] = df['alarma'].map(colores)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    # df['DB'] = df['DB'].apply(json.loads)
    df['DB'] = df['DB'].apply(safe_json_loads)
    # df['INFO'] = df['DB'].apply(lambda x: x.get('xlsx', {}).get('5@Título de pedido'))
    # df['FECHA_INI'] = pd.to_datetime(df['DB'].apply(lambda x: x.get('xlsx', {}).get('13@Fecha inicio requerida')))
    # df['FECHA_FIN'] = pd.to_datetime(df['DB'].apply(lambda x: x.get('xlsx', {}).get('14@Fecha fin requerida')))
    df['FECHA_INI'] = pd.to_datetime(df['fecha_ini'].apply(datetime.fromtimestamp))
    df['FECHA_FIN'] = pd.to_datetime(df['fecha_fin'].apply(datetime.fromtimestamp))
    # df['LM'] = "🟩"
    # df['DT'] = "🟩"
    for c in Causas:
        # df[c.name] = "🟩"
        # df[c.name] = df['DB'].apply(lambda blob: get_alerta(blob, c.name))
        df[c.name] = df['DB'].apply(lambda x: x.get(c.name))
        df[c.name] = df[c.name].map(Alarmas.id_by_color())

    return df

# @st.cache_data
def get_acciones(pedido_id: str) -> 'pd.DataFrame':
    headers = DB.execute("SELECT * FROM acciones LIMIT 0;", fetch=4)
    data = DB.select(f'SELECT * FROM acciones WHERE pedido_id="{pedido_id}";')
    df = pd.DataFrame(data, columns=headers)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    df['fecha'] = pd.to_datetime(df['fecha'].apply(datetime.fromtimestamp))
    df['🏁'] = df['completado'].map({1: True, 0: pd.NA, None: pd.NA}).astype("boolean")
    return df

# @st.cache_data
def get_productos(count: int = 0):
    headers = DB.execute("SELECT * FROM productos LIMIT 0;", fetch=4)
    data = DB.select(f'SELECT * FROM productos;')
    df = pd.DataFrame(data, columns=headers)
    return df