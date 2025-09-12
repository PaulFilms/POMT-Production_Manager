import json
# from typing import TypedDict
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import pandas as pd
from mysqlite import *
from supabase import create_client, Client
from supabase.client import ClientOptions
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt


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
    def get_estado(cls, estado: int) -> str:
        if not isinstance(estado, int):
            return None
        if estado not in [e.value[1] for e in cls]:
            return None
        else:
            return [e.value[0] for e in cls][estado-1]

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

def safe_fromtimestamp(x):
    if x is None or pd.isna(x):
        # return pd.NaT  # Valor nulo para fechas en pandas
        return None  # Valor nulo para fechas en pandas
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




class UI:
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

    @dataclass
    class Timeline:
        hito: str
        fecha_ini: datetime
        fecha_fin: datetime
        texto: str
        color: int # 🟥 1 / 🟨 2 / 🟩 3

        @staticmethod
        def color_map() -> dict:
            return {
                1: "red",
                2: "orange",
                3: "green"
            }
        
        def to_dict(self):
            return asdict(self)

    def my_timeline(df: pd.DataFrame):
        # df["fecha_ini"] = pd.to_datetime(df["fecha_ini"])
        # df["fecha_fin"] = pd.to_datetime(df["fecha_fin"])

        # Convertir fechas a números para eje X
        df["start_num"] = df["fecha_ini"].map(datetime.toordinal)
        df["end_num"] = df["fecha_fin"].map(datetime.toordinal)
        df["duracion"] = df["end_num"] - df["start_num"]

        # Preparar gráfico Gantt con barras horizontales (go.Bar)
        fig = go.Figure()

        for idx, row in df.iterrows():
            color = UI.Timeline.color_map().get(row['color'], "gray")
            fig.add_trace(go.Bar(
                x=[row["duracion"]],
                y=[row["hito"]],
                base=row["start_num"],
                orientation='h',
                name=row["hito"],
                text=[row["texto"]],
                textposition='inside',
                insidetextanchor='start',
                textfont=dict(color='white', size=12, family="Neo Sans, Arial, sans-serif",),
                # marker_color=px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)],
                marker_color=color,
                hovertemplate=(
                    f"{row['hito']}<br>Inicio: {row['fecha_ini'].date()}<br>Fin: {row['fecha_fin'].date()}"
                    "<extra></extra>"
                ),
                showlegend=False,
            ))

        # Línea vertical "Hoy" en número ordinal
        hoy_num = datetime.today().toordinal()
        fig.add_vline(
            x=hoy_num,
            line_dash="dash",
            line_color="blue",
            # annotation_text=" HOY",
            # annotation_position="top right",
            opacity=0.8,
        )


        # Suponiendo que tienes un rango de fechas:
        min_fecha = df["fecha_ini"].min().replace(day=1)
        max_fecha = df["fecha_fin"].max().replace(day=1)

        # Generar lista de meses entre min y max:
        meses = pd.date_range(min_fecha, max_fecha, freq='MS')  # MS = Month Start

        ticks = [d.toordinal() for d in meses]
        # ticks_text = [d.strftime('%b %Y') for d in meses]  # Ej: Sep 2025
        ticks_text = [d.strftime('%m.%Y') for d in meses]  # Ej: Sep 2025

        fig.update_xaxes(
            tickmode='array',
            tickvals=ticks,
            ticktext=ticks_text,
            rangeslider_visible=True,
        )

        # # Convertir a ordinal (para ticks en x):
        # ticks = [d.toordinal() for d in meses]
        # ticks_text = [d.strftime('%Y-%m') for d in meses]

        # # Ajustar ejes para mostrar fechas legibles
        # fig.update_xaxes(
        #     tickmode='array',
        #     tickvals=ticks,
        #     # ticktext=ticks_text,
        #     # tickvals=[d for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],  # cada semana
        #     ticktext=[(datetime.fromordinal(d)).strftime("%d %b") for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],

        #     # title="Mes",
        #     rangeslider_visible=True,
        # )

        # fig.update_xaxes(
        #     tickmode="array",
        #     tickvals=[d for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],  # cada semana
        #     ticktext=[(datetime.fromordinal(d)).strftime("%d %b") for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],
        #     # title="Fecha (Semanas)",
        #     rangeslider_visible=True,
        # )

        fig.update_yaxes(
            autorange="reversed", 
            # title="Hitos"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=150, r=30, t=50, b=30),
            # title="Diagrama de Gantt con línea de hoy",
            barmode='stack',
        )

        plt = st.plotly_chart(fig, use_container_width=True, on_select='rerun')
        # st.write(plt)

    def my_hitoline(df: pd.DataFrame, hito_col: str = "hito", fecha_col: str = "fecha"):
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