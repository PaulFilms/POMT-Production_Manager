import os, json
from typing import List, Dict, Any, get_type_hints
# from typing import TypedDict
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import pandas as pd
from pyreports.xlsx import DF_REPORT
from mysqlite import *

import streamlit as st
import plotly.graph_objects as go
# import plotly.express as px # https://python-charts.com/es/evolucion/diagrama-gantt-plotly/
# import numpy as np



## DB
## ____________________________________________________________________________________________________________________________________________________________________

SQLITE: bool = 1
LOCAL: bool = 1
if SQLITE:
    path_file = 'POMT_production_manager.db'
    path_net = r"\\madtornas01\TorTGP$\PPD\POMT"
    if os.path.exists(path_net) and not LOCAL:
        path_db = os.path.join(path_net, path_file)
        DB = SQL(path_db=path_db)
    else:
        DB = SQL(path_db=path_file)

# SUPABASE: bool = 0
# if SUPABASE:
#     from supabase import create_client, Client
#     from supabase.client import ClientOptions
#     url: str = st.secrets.connections.supabase.SUPABASE_URL
#     key: str = st.secrets.connections.supabase.SUPABASE_KEY
#     supabase: Client = create_client(
#         url,
#         key,
#         options=ClientOptions(
#             postgrest_client_timeout=10,
#             storage_client_timeout=10,
#             schema="public",
#         )
#     )


## DB
## ____________________________________________________________________________________________________________________________________________________________________



    # # @staticmethod
    # def get_firm(self) -> str:
    #     return f'{self.id} / {datetime.now()}'

class Alarmas(Enum):
    red     = ("🟥", 1)
    yellow  = ("🟨", 2)
    green   = ("🟩", 3)
    grey    = ("⬜", 4)

    @classmethod
    def id_by_color(cls):
        return {a.value[1]: a.value[0] for a in cls}
    
    @classmethod
    def colors(cls):
        return [c.value[0] for c in cls]

    @classmethod
    def get_color(cls, value: int) -> str:
        if not value:
            return None
        if not 0 < value < 4:
            return None
        return cls.colors()[value-1]
    
    @classmethod
    def get_int(cls, value: str) -> int:
        if value not in cls.colors():
            return None
        else:
            return cls.colors().index(value) + 1

class Estados(Enum):
    pendiente = ('⏳', 1)
    revisar = ('🔍', 2)
    escalar = ('⏫', 3)
    completo = ('✅', 4)

    def __init__(self, icon: str, id: int):
        self.icon = icon
        self.id = id

    @classmethod
    def get_estado(cls, estado: int) -> str:
        if not isinstance(estado, int):
            return None
        if estado not in [e.id for e in cls]:
            return None
        else:
            return [e.icon for e in cls][estado-1]
    
    @classmethod
    def get_id(cls, estado: str) -> int:
        if not estado or not isinstance(estado, str):
            return None
        if estado not in [e.icon for e in cls]:
            return None
        else:
            return [e.icon for e in cls].index(estado) + 1

    @classmethod
    def get_estados(cls) -> List[str]:
        return [e.name for e in cls]
    
    @classmethod
    def get_estados_icon(cls) -> List[str]:
        return [e.icon for e in cls]
    

    @classmethod
    def id_by_estado(cls):
        return {a.id: a.value[0] for a in cls}

class Causas(Enum):
    LM = 'LM  |  LISTA DE MATERIALES'
    DT = 'DT  |  DOCUMENTACIÓN TÉCNICA'
    PL = 'PL  |  PEDIDOS LANZADOS'
    PR = 'PR  |  PEDIDOS EN RETRASO'
    EM = 'EM  |  ENTREGA MANUFACTURING EN RIESGO'
    CA = 'CA  |  CAMBIO DE ALCANCE'

    def get_ids() -> List[str]:
        return [c.name for c in Causas]
    
    def get_values() -> List[str]:
        return [c.value for c in Causas]

@dataclass
class Modificacion:
    fecha: datetime
    info: str
    data: Dict[str, Any]
    user: str

    def to_dict(self):
        self.fecha = self.fecha.strftime(r'%Y-%m-%d %H:%M')
        return asdict(self)
    
    # def to_json(self):
    #     return json.dumps(self.to_dict())


## DATA
## ____________________________________________________________________________________________________________________________________________________________________

class ORM:
    '''
    Clases de datos:
    - Usuario
    - Pedido
    - Hito
    - Accion
    '''

    @dataclass
    class Usuario:
        '''
        `Args:`
        - id : str
        - nombre : str
        - apellidos : str
        - mail : str
        - info : str
        - password : str
        - DB : dict
        - firm : str
        
        `Functions:`
        - get_form_sql -> Usuario
        - get_form -> str
        '''
        id: str
        nombre: str
        apellidos: str
        mail: str
        info: str
        password: str
        DB: dict
        firm: str

        @classmethod
        def get_form_sql(cls, sql_data: tuple) -> 'ORM.Usuario':
            sql_data = list(sql_data)
            if sql_data[6] and isinstance(sql_data[6], str):
                sql_data[6] = json.loads(sql_data[6])
            return cls(*sql_data)

    @dataclass
    class BaseData:
        @classmethod
        def from_dict(cls, values: Dict[str, Any]) -> 'ORM.BaseData':
            cls_fields = {f.name for f in fields(cls)}
            type_hints = get_type_hints(cls)

            data = {}
            for k, v in values.items():
                if k in cls_fields:
                    expected_type = type_hints.get(k)

                    if expected_type is datetime and isinstance(v, str):
                        data[k] = datetime.strptime(v, '%Y-%m-%d')
                    elif isinstance(v, pd.Timestamp):
                        data[k] = v.to_pydatetime()
                    else:
                        data[k] = v
            return cls(**data)

        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)

        def to_sql(self) -> Dict[str, Any]:
            '''
            Devuelve un diccionario de valores para INSERT / UPDATE 
            '''
            data = asdict(self)
            for k, v in data.items():
                if isinstance(v, datetime):
                    data[k] = datetime.strftime(data[k], r'%Y-%m-%d')

            DB = data.get('DB', None)
            if not DB:
                DB = dict()
            for k, v in DB.items():
                if isinstance(v, datetime):
                    self.DB[k] = v.strftime(r'%Y-%m-%d %H:%M')
            DB = json.dumps(DB)
            data['DB'] = DB

            return data

    @dataclass
    class Pedido(BaseData):
        id: str
        info: str
        bu_id: str
        contraseña: str
        planificador: str
        fecha_ini: datetime
        fecha_fin: datetime
        alarma: int = None
        DB: dict = None
        firm: str = None

    @dataclass
    class Hito(BaseData):
        id: int
        pedido_id: str
        grupo: str
        nombre: str
        fecha_req: datetime
        fecha_plan: datetime
        departamento: str = None
        responsable: str = None
        alarma: int = None
        estado: int = None
        info: str = None
        DB: dict = None
        firm: str = None

    @dataclass
    class Accion(BaseData):
        id: str
        pedido_id: str
        hito_id: int
        causa: str
        alarma: int
        info: str
        accion: str
        planificador: str
        responsable: str
        fecha_accion: datetime
        fecha_req: datetime
        estado: int = 0
        DB: dict = None
        firm: str = None


def safe_json_loads(x):
    if pd.isna(x) or x == '' or x is None:
        return {}  # O {} o [] o lo que quieras devolver cuando esté vacío
    try:
        return json.loads(x)
    except json.JSONDecodeError:
        return {}  # Manejo en caso que el json esté mal formado

def safe_datetime(value) -> datetime:
    if value == None:
        return None
    elif isinstance(value, datetime):
        return value
    elif isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    elif isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    elif isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"No se pudo parsear la fecha string: {value}")
    else:
        raise TypeError(f"Tipo no soportado para conversión a datetime: {type(value)}")

def safe_int(x) -> int:
    try:
        return int(x)
    except:
        return 0

def safe_fromtimestamp(x):
    if x is None or pd.isna(x):
        # return pd.NaT  # Valor nulo para fechas en pandas
        return None  # Valor nulo para fechas en pandas
    else:
        return datetime.fromtimestamp(x)

def safe_contraseña(value: str) -> str:
    if not isinstance(value, str):
        return None
    if not value:
        return None
    if not '/' in value:
        return value
    partes = value.split('/')
    return f'7218|{partes[0]}_{partes[1]}'

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
    # if SUPABASE:
    #     data = supabase.table(table).select('*').execute().data
    #     return pd.DataFrame(data)

# @st.cache_data
def get_business_units(count: int = 0) -> 'pd.DataFrame':
    '''
    st.session_state.bu
    '''
    headers = DB.execute("SELECT * FROM view_business_unit LIMIT 0", fetch=4)
    data = DB.select('SELECT * FROM view_business_unit')
    df = pd.DataFrame(data, columns=headers)
    return df

@st.cache_data
def get_pedidos(count: int = 0) -> 'pd.DataFrame':
    '''
    st.session_state.pedidos
    '''
    table = 'view_pedidos'
    headers = DB.execute(f"SELECT * FROM {table} LIMIT 0", fetch=4)
    data = DB.select(f'SELECT * FROM {table}')
    df = pd.DataFrame(data, columns=headers)
    df['DB'] = df['DB'].apply(safe_json_loads)
    df['fecha_ini'] = df['fecha_ini'].apply(safe_datetime)  # pd.to_datetime(df['fecha_ini'].apply(datetime.fromtimestamp))
    df['fecha_fin'] = df['fecha_fin'].apply(safe_datetime)  # pd.to_datetime(df['fecha_fin'].apply(datetime.fromtimestamp))
    df['contraseña'] = df['contraseña'].apply(safe_contraseña)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    # df['pde_retraso_dias'] = df['pde_retraso_dias'].fillna(0)
    # df['pde_retraso_dias'] = df['pde_retraso_dias'].apply(lambda x: 0 if not x else x)
    # df['pde_retraso_dias'] = df['pde_retraso_dias'].apply(safe_int) # BUG
    for c in Causas:
        df[c.name] = df[c.name].map(Alarmas.id_by_color())

    return df

# @st.cache_data
# def get_pde_items(count: int = 0) -> 'pd.DataFrame':
#     '''
#     st.session_state.pde_items
#     '''
#     table = 'csv_pde_items'
#     if SQLITE:
#         headers = DB.execute(f"SELECT * FROM {table} LIMIT 0;", fetch=4)
#         data = DB.select('SELECT * FROM csv_pde_items ORDER BY id DESC;')
#         df = pd.DataFrame(data, columns=headers)
#         return df

def get_c_criticos(filename: str) -> 'pd.DataFrame':
    table = 'view_pde_items'
    sql = f"""
    WITH RECURSIVE tbl AS (
        SELECT * FROM {table}
        WHERE filename="{filename}"
    )\n
    """
    l = []
    for i in range(1,21):
        l.append(f'''SELECT * FROM (SELECT * FROM tbl WHERE "Camino Critico {i}" IS NOT NULL ORDER BY id DESC LIMIT 1)''')
    sql += '\nUNION ALL\n'.join(l)
    headers = DB.execute(f"SELECT * FROM {table} LIMIT 0;", fetch=4)
    # data = DB.select('SELECT * FROM csv_pde_items ORDER BY id DESC;')
    data = DB.select(sql)
    df = pd.DataFrame(data, columns=headers)
    return df

def get_usuarios_by_dept(departamento_id: str, count_usuarios: int = 0, count_departamentos: int = 0) -> List[str]:
    if not departamento_id:
        return get_usuarios(count_usuarios)['id'].to_list()
    df = get_departamentos(count_departamentos)
    df_DB = df.loc[df['id']==departamento_id, 'DB'].squeeze()
    if not df_DB:
        return None
    DB: dict = json.loads(df_DB)
    return DB.get('usuario_id', None)

def get_hitos(pedido_id: str = None) -> 'pd.DataFrame':
    '''
    st.session_state.hitos
    '''
    tabla = 'view_hitos'
    headers = DB.execute(f"SELECT * FROM {tabla} LIMIT 0;", fetch=4)
    if pedido_id:
        data = DB.select(f'SELECT * FROM {tabla} WHERE pedido_id="{pedido_id}";')
    else:
        data = DB.select(f'SELECT * FROM {tabla};')
    df = pd.DataFrame(data, columns=headers)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    for c in Causas:
        df[c.name] = df[c.name].map(Alarmas.id_by_color())
    df['fecha_req'] = df['fecha_req'].apply(safe_datetime) # pd.to_datetime(df['fecha_accion'].apply(datetime.fromtimestamp))
    df['fecha_plan'] = df['fecha_plan'].apply(safe_datetime) # pd.to_datetime(df['fecha_req'].apply(datetime.fromtimestamp))
    if not df.empty:
        df['Δ'] = (df["fecha_plan"] - pd.Timestamp(datetime.today().date())).dt.days
    else:
        df['Δ'] = pd.Series(dtype='int')
    df['estado_id'] = df['estado']
    df['estado'] = df['estado'].map(Estados.id_by_estado())
    df['DB'] = df['DB'].apply(safe_json_loads)
    return df

# @st.cache_data
def get_acciones(pedido_id: str = None, hito_id: int = None) -> 'pd.DataFrame':
    '''
    st.session_state.acciones
    '''
    headers = DB.execute("SELECT * FROM acciones LIMIT 0;", fetch=4)
    sql = 'SELECT * FROM acciones'
    filters = []
    if pedido_id:
        filters.append(f"pedido_id = '{pedido_id}'")
    if hito_id:
        filters.append(f"hito_id = {hito_id}")
    if filters:
        final_query = f"{sql} WHERE " + " AND ".join(filters)
    else:
        final_query = sql
    data = DB.select(final_query)
    df = pd.DataFrame(data, columns=headers)
    df['#'] = df['alarma'].map(Alarmas.id_by_color())
    df['fecha_accion'] = df['fecha_accion'].apply(safe_datetime) # pd.to_datetime(df['fecha_accion'].apply(datetime.fromtimestamp))
    df['fecha_req'] = df['fecha_req'].apply(safe_datetime) # pd.to_datetime(df['fecha_req'].apply(datetime.fromtimestamp))
    df['estado_id'] = df['estado']
    df['estado'] = df['estado'].map(Estados.id_by_estado())
    df['DB'] = df['DB'].apply(safe_json_loads)
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

def get_templates(count: int = 0) -> List[str]:
    data = DB.select("SELECT DISTINCT(template) FROM templates;")
    return [d[0] for d in data]


class UI:
    def color_cells(value: int):
        if not isinstance(value, int):
            return ''
        elif value > 0:
            return 'background-color: #d4edda'  # verde claro
        elif value <= 0:
            return 'background-color: #f8d7da'  # rojo claro
        else:
            return ''

    @dataclass
    class Timeline:
        texto: str
        grupo: str 
        fecha_ini: datetime
        fecha_fin: datetime
        color: int = None # 🟥 1 / 🟨 2 / 🟩 3

        @staticmethod
        def color_map() -> dict:
            return {
                1: "#F37C7C", # "red",
                2: "rgb(251,187,33)", # "orange",
                3: "rgb(91,174,146)", # "green",
            }
        
        def to_dict(self):
            return asdict(self)

    def my_timeline(df: pd.DataFrame):
        import streamlit as st # BUG

        # Convertir fechas
        df["fecha_ini"] = pd.to_datetime(df["fecha_ini"])
        df["fecha_fin"] = pd.to_datetime(df["fecha_fin"])

        # Convertir fechas a números para eje X
        df["start_num"] = df["fecha_ini"].map(datetime.toordinal)
        df["end_num"] = df["fecha_fin"].map(datetime.toordinal)
        df["duracion"] = df["end_num"] - df["start_num"]

        # Definir columna para agrupar en eje Y
        df["grupo_final"] = df["grupo"].fillna(df["texto"])

        # Preparar gráfico Gantt con barras horizontales (go.Bar)
        fig = go.Figure()

        for idx, row in df.iterrows():
            color = UI.Timeline.color_map().get(row['color'], "gray")
            fig.add_trace(go.Bar(
                x=[row["duracion"]],
                y=[row["grupo_final"]],
                base=row["start_num"],
                orientation='h',
                # name=row["hito"], # Testo de ayuda
                name=row["texto"], # Testo de ayuda
                text=row["texto"], # Texto de la barra
                textposition='inside', # inside / outside
                insidetextanchor='end', # start / end
                textfont=dict(color='white', size=12, family="Neo Sans, Neo Sans, Neo Sans",),
                # marker_color=px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)],
                marker_color=color,
                hovertemplate=(
                    f"{row['texto']}<br>INICIO: {row['fecha_ini'].date()}<br>FIN: {row['fecha_fin'].date()}"
                    f"<extra>{row["grupo_final"]}</extra>"
                ),
                showlegend=False,
            ))

        # Línea vertical "Hoy" en número ordinal
        hoy_num = datetime.today().toordinal()
        fig.add_vline(
            x=hoy_num,
            line_dash='solid', # "dash",
            line_color="blue",
            # annotation_text=" HOY",
            # annotation_position="top right",
            line_width=1,
            opacity=0.8,
        )

        # Suponiendo que tienes un rango de fechas:
        min_fecha = df["fecha_ini"].min().replace(day=1)
        max_fecha = df["fecha_fin"].max().replace(day=1)

        # Generar lista de meses entre min y max:
        meses = pd.date_range(min_fecha, max_fecha, freq='MS')  # MS = Month Start

        ticks = [d.toordinal() for d in meses]
        ticks_text = [d.strftime('%m.%Y') for d in meses]  # Ej: Sep 2025

        fig.update_xaxes(
            tickmode='array',
            tickvals=ticks,
            ticktext=ticks_text,
            rangeslider_visible=True,
        )

        fig.update_yaxes(
            autorange="reversed", 
            # title="Hitos"
        )

        fig.update_layout(
            height=500,
            # margin=dict(l=150, r=30, t=50, b=30),
            # title="Diagrama de Gantt con línea de hoy",
            barmode='stack',
        )

        # fig.update_layout(
        #     # height=200 * len(df["grupo_final"].unique()),  # 40px por barra, por ejemplo
        #     height=500,  # 40px por barra, por ejemplo
        #     barmode='stack',
        # )

        # fig.update_traces(marker_line_width=2)  # Da un borde visible y da impresión de mayor grosor

        plt = st.plotly_chart(fig, use_container_width=True, on_select='rerun', selection_mode='points')
        return plt

    def my_hitoline(df: pd.DataFrame, hito_col: str = "hito", fecha_col: str = "fecha"):
        import streamlit as st # BUG
        import matplotlib.pyplot as plt
        # Asegurarse que la columna de fecha sea datetime
        df[fecha_col] = pd.to_datetime(df[fecha_col])

        # Ordenar dataframe por fecha
        df = df.sort_values(by=fecha_col).reset_index(drop=True)

        # Alternar niveles fijos para alineación visual clara
        level_up = 3
        level_down = -3
        df["Level"] = [level_up if i % 2 == 0 else level_down for i in range(len(df))]
        df['position'] = [df[fecha_col].min() + timedelta(days=d) for d in range(len(df))]

        with plt.style.context("fivethirtyeight"):
            fig, ax = plt.subplots(figsize=(18, 6))

            # Línea base del tiempo
            # ax.plot(df[fecha_col], [0] * len(df), "-o", color="black", markerfacecolor="white")
            ax.plot(df['position'], [0] * len(df), "-o", color="black", markerfacecolor="white")

            # Etiquetas del eje x no necesarias
            ax.set_xticks([])
            ax.set_yticks([])
            # ax.set_ylim(-5, 5)
            ax.set_ylim(-7, 7)

            # Anotaciones
            for idx in range(len(df)):
                # dt = df[fecha_col].iloc[idx]
                dt = df['position'].iloc[idx]
                fecha = df[fecha_col].iloc[idx]
                hito = df[hito_col].iloc[idx]
                level = df["Level"].iloc[idx]
                text = f"{hito.upper()}\n{fecha.strftime('%Y-%m-%d')}"

                ax.annotate(
                    text,
                    xy=(dt, 0),
                    xytext=(dt, level),
                    arrowprops=dict(
                        arrowstyle="-", 
                        color="red", 
                        linewidth=0.8
                    ),
                    ha="center",
                    fontsize=10
                )

            # Quitar bordes
            ax.spines[["left", "top", "right", "bottom"]].set_visible(False)
            ax.spines["bottom"].set_position(("axes", 0.5))
            ax.grid(False)

            # ax.set_title("Timeline Detallado", pad=10, loc="left", fontsize=20, fontweight="bold")

        st.pyplot(fig)

    def st_timeline(dataframe: pd.DataFrame):
        '''
        Ejemplo de Gantt (Borrar)
        '''
        import streamlit as st # BUG
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

    def my_calendar():
        import streamlit as st # BUG
        import warnings
        warnings.filterwarnings("ignore", message="findfont: Font family 'Helvetica' not found.")
        from matplotlib import rcParams
        rcParams['font.family'] = 'Neo Sans'

        import calplot ## https://pypi.org/project/calplot/
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from dateutil.relativedelta import relativedelta
        
        # Cambiar la fuente globalmente a 'DejaVu Sans' (viene con matplotlib)
        
        # Tu DB
        columns = DB.execute('SELECT * FROM hitos LIMIT 0', fetch=4)
        data = DB.select('SELECT * FROM hitos')
        df = pd.DataFrame(data, columns=columns)

        # Convertir fecha_fin a datetime
        df['fecha_plan'] = pd.to_datetime(df['fecha_plan'])
        alarma_por_fecha = df.groupby('fecha_plan')['alarma'].min()

        # Calcular valores por defecto para date_input
        min_fecha = df['fecha_plan'].min()
        max_fecha = df['fecha_plan'].max()

        # Restar 1 mes al mínimo y sumar 1 mes al máximo usando relativedelta
        fecha_desde_def = min_fecha - relativedelta(months=1)
        fecha_hasta_def = max_fecha + relativedelta(months=1)

        # Widgets para seleccionar rango de fechas
        col_from, col_to = st.columns(2)
        fecha_desde = col_from.date_input('Desde', value=fecha_desde_def)
        fecha_hasta = col_to.date_input('Hasta', value=fecha_hasta_def)

        # Filtrar el rango
        alarma_filtrada = alarma_por_fecha.loc[fecha_desde:fecha_hasta]

        # Definir colormap
        colores = ['grey', 'red', 'yellow', 'green']
        cmap = ListedColormap(colores)

        # Crear gráfico calplot
        fig, ax = calplot.calplot(
            alarma_filtrada,
            cmap=cmap,
            suptitle='Alarma por fecha (1=Rojo, 2=Amarillo, 3=Verde)',
            colorbar=False
        )

        # Mostrar gráfico en Streamlit
        st.pyplot(fig)

    def df_calendar():
        pass


class HTML:
    def generar_card(titulo, contenido):
        return f"""
        <div style="
            background: linear-gradient(90deg, #ddd, #aaa);
            background-color:#fff; 
            border-radius:20px; 
            box-shadow:0 2px 8px rgba(0,0,0,0.1); 
            padding:20px; margin:12px 0; 
            max-width:600px; 
            font-family: Neo Sans, sans-serif; 
            line-height:1.5;
        ">
        <div style="font-weight:bold; margin-bottom:8px; font-size:18px; color:#333;">
            {titulo}
        </div>
        <div style="font-size:14px; color:#555; white-space: normal; margin: 0; padding: 0;">
            {contenido}
        </div>
        </div>
        """
    
    html_algo = '''
    <div style="width: 100%; font-family: Neo Sans, Neo Sans;padding:20px; margin:12px 0; ">
        <div style="display: inline-block; width: 48%; vertical-align: top; padding: 4px;">
            <b>PLANIFICADOR: </b> {fila['planificador']}<br>
            <b>RESPONSABLE: </b> {fila['responsable']}
        </div>
        <div style="display: inline-block; width: 48%; vertical-align: top; padding: 4px;">
            <b>ACCION ID:</b> {fila['id']}<br>
            <b>PEDIDO ID:</b> {fila['pedido_id']}
        </div>
    </div>
    '''

    html_table = """
<p>&nbsp;</p>
<p>ALARMA GPI: 🟥</p>
<p>&nbsp;</p>
<table style="width:100%; border-collapse: collapse;" border="1">
    <tbody>
    <tr style="background-color:#f2f2f2;">
    <td>ACCIONES</td>
    <td>ALARMA</td>
    <td>FECHA</td>
    </tr>
    <tr>
    <td>accion1</td>
    <td>🟥</td>
    <td>2028-03-03</td>
    </tr>
    <tr>
    <td>accion2</td>
    <td>🟩</td>
    <td>2028-03-03</td>
    </tr>
    <tr>
    <td>accion3</td>
    <td>🟨</td>
    <td>2028-03-03</td>
    </tr>
    </tbody>
</table>
<p>&nbsp;</p>
<table style="width:100%; border-collapse: collapse;" border="1">
    <tbody>
    <tr style="background-color:#f2f2f2;">
    <td>HITOS</td>
    <td>ALARMA</td>
    <td>FECHA</td>
    </tr>
    <tr>
    <td>hito1</td>
    <td>🟥</td>
    <td>2028-03-03</td>
    </tr>
    <tr>
    <td>hito2</td>
    <td>🟩</td>
    <td>2028-03-03</td>
    </tr>
    <tr>
    <td>hito3</td>
    <td>🟨</td>
    <td>2028-03-03</td>
    </tr>
    </tbody>
</table>
"""

def send_mail():
    print('ENVIAR MAIL:')