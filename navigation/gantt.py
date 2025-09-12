import streamlit as st
from functions import *
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date

# st.set_page_config(layout="wide")
st.title("📊 DIAGRAMA DE GANTT")

# # Datos de hitos
# data = [
#     {"Tarea": "Inicio Proyecto", "Inicio": "2025-01-01", "Fin": "2025-01-14"},
#     {"Tarea": "Fase de Diseño", "Inicio": "2025-01-15", "Fin": "2025-02-15"},
#     {"Tarea": "Desarrollo", "Inicio": "2025-02-16", "Fin": "2025-04-30"},
#     {"Tarea": "Desarrollo", "Inicio": "2025-04-16", "Fin": "2025-08-30"},
#     {"Tarea": "Pruebas", "Inicio": "2025-05-01", "Fin": "2025-06-01"},
#     {"Tarea": "Entrega", "Inicio": "2025-06-15", "Fin": "2025-06-30"},
# ]

# df = pd.DataFrame(data)
# df["Inicio"] = pd.to_datetime(df["Inicio"])
# df["Fin"] = pd.to_datetime(df["Fin"])

# # Convertir fechas a números para eje X
# df["start_num"] = df["Inicio"].map(datetime.toordinal)
# df["end_num"] = df["Fin"].map(datetime.toordinal)
# df["duracion"] = df["end_num"] - df["start_num"]

# # Preparar gráfico Gantt con barras horizontales (go.Bar)
# fig = go.Figure()

# for idx, row in df.iterrows():
#     fig.add_trace(go.Bar(
#         x=[row["duracion"]],
#         y=[row["Tarea"]],
#         base=row["start_num"],
#         orientation='h',
#         name=row["Tarea"],
#         marker_color=px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)],
#         hovertemplate=f"{row['Tarea']}<br>Inicio: {row['Inicio'].date()}<br>Fin: {row['Fin'].date()}<extra></extra>",
#         showlegend=False,
#     ))

# # Línea vertical "Hoy" en número ordinal
# hoy_num = datetime.today().toordinal()
# hoy_num = datetime(2025,3,1).toordinal()

# fig.add_vline(
#     x=hoy_num,
#     line_dash="dash",
#     line_color="blue",
#     annotation_text=" HOY",
#     annotation_position="top right",
#     opacity=0.8,
# )

# # Ajustar ejes para mostrar fechas legibles
# fig.update_xaxes(
#     tickmode="array",
#     tickvals=[d for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],  # cada semana
#     ticktext=[(datetime.fromordinal(d)).strftime("%d %b") for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],
#     # title="Fecha (Semanas)",
#     rangeslider_visible=True,
# )

# fig.update_yaxes(
#     autorange="reversed", 
#     # title="Hitos"
# )

# fig.update_layout(
#     height=500,
#     margin=dict(l=150, r=30, t=50, b=30),
#     # title="Diagrama de Gantt con línea de hoy",
#     barmode='stack',
# )

# st.plotly_chart(fig, use_container_width=True)


# ## OTRO

# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime

# st.set_page_config(layout="wide")
# st.title("📊 Diagrama de Gantt con texto dentro de barra")

# # Datos de hitos con fechas
# data = [
#     {"Tarea": "Inicio Proyecto", "Inicio": "2025-01-01", "Fin": "2025-01-14", "Texto": "Comienzo"},
#     {"Tarea": "Fase de Diseño", "Inicio": "2025-01-15", "Fin": "2025-02-15", "Texto": ""},
#     {"Tarea": "Desarrollo", "Inicio": "2025-02-16", "Fin": "2025-04-30", "Texto": "En progreso"},
#     {"Tarea": "Pruebas", "Inicio": "2025-05-01", "Fin": "2025-06-01", "Texto": ""},
#     {"Tarea": "Entrega", "Inicio": "2025-06-15", "Fin": "2025-06-30", "Texto": "Final"},
# ]

# df = pd.DataFrame(data)
# df["Inicio"] = pd.to_datetime(df["Inicio"])
# df["Fin"] = pd.to_datetime(df["Fin"])

# # Convertir fechas a números ordinales para el eje X
# df["start_num"] = df["Inicio"].map(datetime.toordinal)
# df["end_num"] = df["Fin"].map(datetime.toordinal)
# df["duracion"] = df["end_num"] - df["start_num"]

# fig = go.Figure()

# for idx, row in df.iterrows():
#     fig.add_trace(go.Bar(
#         x=[row["duracion"]],
#         y=[row["Tarea"]],
#         base=row["start_num"],
#         orientation='h',
#         name=row["Tarea"],
#         text=[row["Texto"]],
#         textposition='inside',
#         textfont=dict(color='white', size=12),
#         marker_color=px.colors.qualitative.Set3[idx % len(px.colors.qualitative.Set3)],
#         hovertemplate=(
#             f"{row['Tarea']}<br>Inicio: {row['Inicio'].date()}<br>Fin: {row['Fin'].date()}"
#             "<extra></extra>"
#         ),
#         showlegend=False,
#     ))

# # Añadir línea vertical para hoy
# hoy_num = datetime.today().toordinal()
# fig.add_vline(
#     x=hoy_num,
#     line_dash="dash",
#     line_color="red",
#     annotation_text="Hoy",
#     annotation_position="top right",
#     opacity=0.8,
# )

# fig.update_xaxes(
#     tickmode="array",
#     tickvals=[d for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],
#     ticktext=[(datetime.fromordinal(d)).strftime("%d %b") for d in range(df["start_num"].min() - 10, df["end_num"].max() + 10, 7)],
#     title="Fecha",
#     rangeslider_visible=True,
# )

# fig.update_yaxes(autorange="reversed", title="Hitos")

# fig.update_layout(
#     height=500,
#     margin=dict(l=150, r=30, t=50, b=30),
#     title="Diagrama de Gantt con texto en barras",
# )

# st.plotly_chart(fig, use_container_width=True)


# data = [
#     {"Tarea": "Inicio Proyecto", "Inicio": "2025-01-01", "Fin": "2025-01-14"},
#     {"Tarea": "Fase de Diseño", "Inicio": "2025-01-15", "Fin": "2025-02-15"},
#     {"Tarea": "Desarrollo", "Inicio": "2025-02-16", "Fin": "2025-04-30"},
#     {"Tarea": "Desarrollo", "Inicio": "2025-04-16", "Fin": "2025-08-30"},
#     {"Tarea": "Pruebas", "Inicio": "2025-05-01", "Fin": "2025-06-01"},
#     {"Tarea": "Entrega", "Inicio": "2025-06-15", "Fin": "2025-06-30"},
# ]

data = [
    UI.Timeline(hito='PEDIDO', fecha_ini=datetime(2025, 1, 1), fecha_fin=datetime(2026, 1, 1), texto='PEDIDO XXXX', color=1),
    UI.Timeline(hito='HITOS', fecha_ini=datetime(2025, 1, 1), fecha_fin=datetime(2025, 3, 1), texto='HITO1', color=2),
    UI.Timeline(hito='HITOS', fecha_ini=datetime(2025, 3, 1), fecha_fin=datetime(2025, 6, 1), texto=None, color=3),
    UI.Timeline(hito='HITOS', fecha_ini=datetime(2025, 6, 1), fecha_fin=datetime(2025, 7, 1), texto='HITO3', color=None),
    UI.Timeline(hito='Evento 1', fecha_ini=datetime(2025, 3, 1), fecha_fin=datetime(2025, 7, 1), texto='Evento 1', color=3),
    UI.Timeline(hito='Evento 2', fecha_ini=datetime(2025, 2, 1), fecha_fin=datetime(2025, 8, 1), texto='Evento 2', color=2),
]

df = pd.DataFrame(data)
with st.container(border=True):
    UI.my_timeline(df)