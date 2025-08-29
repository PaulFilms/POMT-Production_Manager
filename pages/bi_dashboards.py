# import streamlit as st


# import pandas as pd
# import numpy as np

# dates = ["2007-6-29", "2008-7-11", "2009-6-29", "2010-9-21", "2011-10-14", "2012-9-21", "2013-9-20",
#     "2014-9-19", "2015-9-25", "2016-3-31", "2016-9-16", "2017-9-22", "2017-11-3", "2018-9-21",
#     "2018-10-26", "2019-9-20", "2020-11-13", "2021-9-24", "2022-9-16"
# ]
# phones = ["iPhone", "iPhone-3G", "iPhone-3GS", "iPhone 4", "iPhone 4S", "iPhone 5", "iPhone 5C/5S",
#     "iPhone 6/6 Plus", "iPhone 6S/6s Plus", "iPhone SE", "iPhone 7/7 Plus", "iPhone 8/8 Plus",
#     "iPhone X", "iPhone Xs/Max", "iPhone XR", "iPhone 11/Pro/Max", "iPhone 12 Pro", "iPhone 13 Pro",
#     "iPhone 14 Plus/Pro Max"
# ]

# iphone_df = pd.DataFrame(data={"Date": dates, "Product": phones})
# iphone_df["Date"] = pd.to_datetime(iphone_df["Date"])
# iphone_df["Level"] = [np.random.randint(-6,-2) if (i%2)==0 else np.random.randint(2,6) for i in range(len(iphone_df))]

# # iphone_df


# import matplotlib.pyplot as plt

# with plt.style.context("fivethirtyeight"):
#     fig, ax = plt.subplots(figsize=(18,9))

#     ax.plot(iphone_df.Date, [0,]* len(iphone_df), "-o", color="black", markerfacecolor="white");

#     ax.set_xticks(pd.date_range("2007-1-1", "2023-1-1", freq="ys"), range(2007, 2024));
#     ax.set_ylim(-7,7);

#     for idx in range(len(iphone_df)):
#         dt, product, level = iphone_df["Date"][idx], iphone_df["Product"][idx], iphone_df["Level"][idx]
#         dt_str = dt.strftime("%b-%Y")
#         ax.annotate(dt_str + "\n" + product, xy=(dt, 0.1 if level>0 else -0.1),xytext=(dt, level),
#             arrowprops=dict(arrowstyle="-",color="red", linewidth=0.8),
#             ha="center"
#         );

#     ax.spines[["left", "top", "right", "bottom"]].set_visible(False);
#     ax.spines[["bottom"]].set_position(("axes", 0.5));
#     ax.yaxis.set_visible(False);
#     ax.set_title("iPhone Release Dates", pad=10, loc="left", fontsize=25, fontweight="bold");
#     ax.grid(False)

# st.pyplot(fig)

## -------------------------------------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Crear datos para dos años con detalle mensual
dates = pd.date_range(start="2023-01-01", end="2024-12-31", freq='MS')  # primer día de cada mes
phones = [f"Hito {i+1}" for i in range(len(dates))]

iphone_df = pd.DataFrame({
    "Date": dates,
    "Product": phones
})
# Niveles alternos para flechas arriba/abajo
iphone_df["Level"] = [np.random.randint(-6,-2) if i % 2 == 0 else np.random.randint(2,6) for i in range(len(iphone_df))]

# Mostrar selectbox para seleccionar un hito
selected_hito = st.selectbox("Selecciona un hito", options=iphone_df["Product"])

# Mostrar información del hito seleccionado
info_hito = iphone_df[iphone_df["Product"] == selected_hito].iloc[0]
st.write(f"Fecha: {info_hito['Date'].strftime('%Y-%m-%d')}")
st.write(f"Hito: {info_hito['Product']}")

# Graficar timeline
with plt.style.context("fivethirtyeight"):
    fig, ax = plt.subplots(figsize=(18, 6))

    ax.plot(iphone_df.Date, [0]*len(iphone_df), "-o", color="black", markerfacecolor="white")

    # Ticks cada mes con formato mes-año
    ax.set_xticks(iphone_df.Date)
    ax.set_xticklabels(iphone_df.Date.dt.strftime('%b-%Y'), rotation=45, ha="right")

    ax.set_ylim(-7, 7)

    for idx in range(len(iphone_df)):
        dt, product, level = iphone_df["Date"].iloc[idx], iphone_df["Product"].iloc[idx], iphone_df["Level"].iloc[idx]
        dt_str = dt.strftime("%b-%Y")
        ax.annotate(dt_str + "\n" + product, xy=(dt, 0.1 if level > 0 else -0.1), xytext=(dt, level),
                    arrowprops=dict(arrowstyle="-", color="red", linewidth=0.8),
                    ha="center")

    ax.spines[["left", "top", "right", "bottom"]].set_visible(False)
    ax.spines[["bottom"]].set_position(("axes", 0.5))
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_title("Timeline Detallado Últimos 2 Años", pad=10, loc="left", fontsize=20, fontweight="bold")
    ax.grid(False)

st.pyplot(fig)



## -------------------------------------------------------------------------------------------------------------


# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go

# # Crear datos para dos años con detalle mensual
# dates = pd.date_range(start="2023-01-01", end="2024-12-31", freq='MS')  # primer día de cada mes
# phones = [f"Hito {i+1}" for i in range(len(dates))]

# df = pd.DataFrame({
#     "Date": dates,
#     "Product": phones
# })
# df["Level"] = [np.random.randint(-6,-2) if i % 2 == 0 else np.random.randint(2,6) for i in range(len(df))]

# # Selectbox para elegir hito
# selected_hito = st.selectbox("Selecciona un hito", options=df["Product"])

# # Obtener info del hito seleccionado
# info_hito = df[df["Product"] == selected_hito].iloc[0]
# st.write(f"Fecha: {info_hito['Date'].strftime('%Y-%m-%d')}")
# st.write(f"Hito: {info_hito['Product']}")

# # Crear figura Plotly
# fig = go.Figure()

# # Línea base
# fig.add_trace(go.Scatter(
#     x=df["Date"],
#     y=[0]*len(df),
#     mode="lines+markers",
#     line=dict(color="black"),
#     marker=dict(color="white", size=10, line=dict(color="black", width=2)),
#     hoverinfo="skip"
# ))

# # Flechas / Anotaciones
# for idx, row in df.iterrows():
#     fig.add_annotation(
#         x=row["Date"],
#         y=row["Level"],
#         ax=row["Date"],
#         ay=0,
#         axref='x',
#         ayref='y',
#         showarrow=True,
#         arrowhead=0,
#         arrowsize=1,
#         arrowwidth=1.5,
#         arrowcolor="red",
#         text=f"{row['Date'].strftime('%b-%Y')}<br>{row['Product']}",
#         font=dict(size=10),
#         xanchor="center",
#         yanchor="bottom" if row["Level"] > 0 else "top",
#     )

# fig.update_layout(
#     title="Timeline Detallado Últimos 2 Años",
#     yaxis=dict(visible=False, range=[-7,7]),
#     xaxis=dict(
#         tickformat="%b-%Y",
#         tickangle=45,
#         dtick="M1",
#         tickmode="linear",
#         showgrid=False,
#         showline=False,
#     ),
#     plot_bgcolor="white",
#     margin=dict(l=50, r=50, t=50, b=50)
# )

# st.plotly_chart(fig, use_container_width=True)
