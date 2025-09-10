import json
from enum import Enum
import pandas as pd
from mysqlite import *
from supabase import create_client, Client
from supabase.client import ClientOptions
import streamlit as st



## DB
## ____________________________________________________________________________________________________________________________________________________________________

SQLITE: bool = 1
if SQLITE:
    path_db = r"PPI.db"
    DB = SQL(path_db=path_db)

SUPABASE: bool = 0
if SUPABASE:
    url: str = st.secrets.connections.supabase.SUPABASE_URL
    key: str = st.secrets.connections.supabase.SUPABASE_KEY
    supabase: Client = create_client(
        url,
        key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
        )
    )

## DB
## ____________________________________________________________________________________________________________________________________________________________________

@dataclass
class Usuario:
    id: str
    nombre: str
    apellidos: str
    mail: str
    info: str
    password: str
    DB: dict
    firm: str

    @classmethod
    def get_form_sql(cls, sql_data: tuple) -> 'Usuario':
        if sql_data[6] and isinstance(sql_data[6], str):
            sql_data[6] = json.loads(sql_data[6])
        return cls(*sql_data)

    # @staticmethod
    def get_firm(self) -> str:
        return f'{self.id} / {datetime.now()}'

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

class Estados(Enum):
    pendiente = ('⏳', 1)
    revisar = ('🔍', 2)
    escalar = ('⏫', 3)
    completo = ('✅', 4)

    @classmethod
    def get_estados(cls) -> List[str]:
        return [e.name for e in cls]

    @classmethod
    def id_by_estado(cls):
        return {a.value[1]: a.value[0] for a in cls}

class Causas(Enum):
    LM = 'LM  |  LISTA DE MATERIALES'
    DT = 'DT  |  DOCUMENTACIÓN TÉCNICA'
    PL = 'PL  |  PEDIDOS LANZADOS'
    PR = 'PR  |  PEDIDOS EN RETRASO'
    EM = 'EM  |  ENTREGA MANUFACTURING EN RIESGO'
    CA = 'CA  |  CAMBIO DE ALCANCE'

def session_state_start():
    if not 'login' in st.session_state: st.session_state.login = None
    if not 'login_count' in st.session_state: st.session_state.login_count = 1
    if not 'usuarios' in st.session_state: st.session_state.usuarios = 1
    if not 'pedidos' in st.session_state: st.session_state.pedidos = 1
    if not 'bu' in st.session_state: st.session_state.bu = 1
    if not 'departamentos' in st.session_state: st.session_state.departamentos = 1
    if not 'action' in st.session_state: st.session_state.action = 1
    if not 'productos' in st.session_state: st.session_state.productos = 1

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


## DATA
## ____________________________________________________________________________________________________________________________________________________________________

def safe_json_loads(x):
    if pd.isna(x) or x == '' or x is None:
        return {}  # O {} o [] o lo que quieras devolver cuando esté vacío
    try:
        return json.loads(x)
    except json.JSONDecodeError:
        return {}  # Manejo en caso que el json esté mal formado

def safe_fromtimestamp(x):
    if x is None or pd.isna(x):
        return pd.NaT  # Valor nulo para fechas en pandas
    else:
        return datetime.fromtimestamp(x)

def get_alerta(blob, field: str):
    '''
    Alertas para causas standard
    '''
    if blob is None:
        return None
    try:
        data: dict = json.loads(blob)
        val = data.get(field, None)
        return int(val) if val is not None else None
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        return None


# @st.cache_data
def get_departamentos(count: int = 0) -> 'pd.DataFrame':
    '''
    st.session_state.departamentos
    '''
    headers = DB.execute("SELECT * FROM departamentos LIMIT 0", fetch=4)
    data = DB.select('SELECT * FROM departamentos')
    df = pd.DataFrame(data, columns=headers)
    return df

# @st.cache_data
def get_usuarios(count: int = 0) -> 'pd.DataFrame':
    '''
    st.session_state.usuarios
    '''
    table = 'usuarios'
    if SQLITE:
        headers = DB.execute(f"SELECT * FROM {table} LIMIT 0", fetch=4)
        data = DB.select('SELECT * FROM usuarios')
        df = pd.DataFrame(data, columns=headers)
        return df
    if SUPABASE:
        data = supabase.table(table).select('*').execute().data
        return pd.DataFrame(data)

def get_usuarios_by_dept(departamento_id: str):
    if not departamento_id:
        return get_usuarios(st.session_state.usuarios)['id'].to_list()
    df = get_departamentos(st.session_state.departamentos)
    df_DB = df.loc[df['id']==departamento_id, 'DB'].squeeze()
    if not df_DB:
        return None
    DB: dict = json.loads(df_DB)
    return DB.get('usuario_id', None)


# @st.cache_data
def get_business_units(count: int = 0) -> 'pd.DataFrame':
    '''
    st.session_state.bu
    '''
    headers = DB.execute("SELECT * FROM view_bunit_count LIMIT 0", fetch=4)
    data = DB.select('SELECT * FROM view_bunit_count')
    df = pd.DataFrame(data, columns=headers)
    df['🟥'] = df['alarma_1']
    df['🟨'] = df['alarma_2']
    df['🟩'] = df['alarma_3']
    return df

# @st.cache_data
def get_pedidos(count: int = 0) -> 'pd.DataFrame':
    '''
    st.session_state.pedidos
    '''
    headers = DB.execute("SELECT * FROM view_pedidos_count LIMIT 0", fetch=4)
    data = DB.select('SELECT * FROM view_pedidos_count')

    df = pd.DataFrame(data, columns=headers)
    # df['#'] = df['alarma'].map(colores)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    # df['DB'] = df['DB'].apply(json.loads)
    df['DB'] = df['DB'].apply(safe_json_loads)
    # df['INFO'] = df['DB'].apply(lambda x: x.get('xlsx', {}).get('5@Título de pedido'))
    # df['FECHA_INI'] = pd.to_datetime(df['DB'].apply(lambda x: x.get('xlsx', {}).get('13@Fecha inicio requerida')))
    # df['FECHA_FIN'] = pd.to_datetime(df['DB'].apply(lambda x: x.get('xlsx', {}).get('14@Fecha fin requerida')))
    df['FECHA_INI'] = df['fecha_ini'].apply(safe_fromtimestamp)  # pd.to_datetime(df['fecha_ini'].apply(datetime.fromtimestamp))
    df['FECHA_FIN'] = df['fecha_fin'].apply(safe_fromtimestamp)  # pd.to_datetime(df['fecha_fin'].apply(datetime.fromtimestamp))
    df['∑'] = df['total_acciones']
    for c in Causas:
        # df[c.name] = df['DB'].apply(lambda x: x.get(c.name))
        df[c.name] = df[c.name].map(Alarmas.id_by_color())

    return df

# @st.cache_data
def get_acciones(pedido_id: str) -> 'pd.DataFrame':
    '''
    st.session_state.action
    '''
    headers = DB.execute("SELECT * FROM acciones LIMIT 0;", fetch=4)
    data = DB.select(f'SELECT * FROM acciones WHERE pedido_id="{pedido_id}";')
    df = pd.DataFrame(data, columns=headers)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    df['fecha_accion'] = df['fecha_accion'].apply(safe_fromtimestamp) # pd.to_datetime(df['fecha_accion'].apply(datetime.fromtimestamp))
    df['fecha_req'] = df['fecha_req'].apply(safe_fromtimestamp) # pd.to_datetime(df['fecha_req'].apply(datetime.fromtimestamp))
    # df['estado'] = df['estado'].map({1: True, 0: pd.NA, None: pd.NA}).astype("integer")
    df['estado_id'] = df['estado']
    df['estado'] = df['estado'].map(Estados.id_by_estado())
    return df

# @st.cache_data
def get_productos(count: int = 0):
    '''
    st.session_state.productos
    '''
    headers = DB.execute("SELECT * FROM productos LIMIT 0;", fetch=4)
    data = DB.select(f'SELECT * FROM productos;')
    df = pd.DataFrame(data, columns=headers)
    return df