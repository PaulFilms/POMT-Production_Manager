import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

data = {
    'Nombre': ['Ana', 'Luis', 'Carlos', 'Marta', 'Jorge'],
    'Categoría': ['A', 'B', 'A', 'C', 'B'],
    'Fecha': ['2025-10-01', '2025-10-03', '2025-10-05', '2025-09-30', '2025-10-02'],
    'Alarma': [1, 2, 3, 2, 1],
    'Valor': [100, 200, 150, 175, 130]
}

df = pd.DataFrame(data)
df['Fecha'] = pd.to_datetime(df['Fecha'])

st.title("Ejemplo tabla con filtros y colores por alarma (Dark Mode, Español)")

gb = GridOptionsBuilder.from_dataframe(df)

# gb.configure_column("Alarma", hide=True)
gb.configure_column("Alarma", filter='agSetColumnFilter')
gb.configure_column("Nombre", filter="agTextColumnFilter", header_name="Nombre (Texto)")
# gb.configure_column("Categoría", filter="agSetColumnFilter", header_name="Categoría (Selectbox)")
gb.configure_column(
    "Categoría",
    header_name="Categoría",
    filter="agSetColumnFilter",
    # floatingFilter=True,
    filterParams={
        "values": ['A', 'B', 'C']  # o lista dinámica: df['Categoría'].unique().tolist()
    }
)


df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%Y-%m-%d')  # Limpiar formato
gb.configure_column(
    "Fecha",
    header_name="Fecha",
    filter="agDateColumnFilter",
    filter_params={
        "comparator": JsCode("""
            function(filterLocalDateAtMidnight, cellValue) {
                var parts = cellValue.split('-');
                var cellDate = new Date(parts[0], parts[1] - 1, parts[2]);
                if (cellDate < filterLocalDateAtMidnight) return -1;
                if (cellDate > filterLocalDateAtMidnight) return 1;
                return 0;
            }
        """)
    }
)

gb.configure_columns(["Alarma", "Valor"])
# gb.configure_column_group(
#     "grupo",
#     children=["Alarma", "Valor"]
# )


row_style_js = JsCode("""
function(params) {
    if (params.data.Alarma == 1) {
        return { backgroundColor: '#4a1e1e', color: 'white' };
    } else if (params.data.Alarma == 2) {
        return { backgroundColor: '#4a3b1e', color: 'white' };
    } else if (params.data.Alarma == 3) {
        return { backgroundColor: '#1e4a2c', color: 'white' };
    }
    return null;
}
""")

gb.configure_grid_options(getRowStyle=row_style_js)
gb.configure_default_column(floatingFilter=True)
gb.configure_side_bar(filters_panel=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)
suppressColumnsToolPanel=True

# Localización Español
spanish_locale = {
    'page': 'Página',
    'more': 'Más',
    'to': 'a',
    'of': 'de',
    'next': 'Siguiente',
    'last': 'Último',
    'first': 'Primero',
    'previous': 'Anterior',
    'loadingOoo': 'Cargando...',
    'selectAll': 'Seleccionar todo',
    'searchOoo': 'Buscar...',
    'filterOoo': 'Filtrando...',
    'applyFilter': 'Aplicar',
    'equals': 'Igual',
    'notEqual': 'No igual',
    'lessThan': 'Menor que',
    'greaterThan': 'Mayor que',
    'lessThanOrEqual': 'Menor o igual',
    'greaterThanOrEqual': 'Mayor o igual',
    'inRange': 'En rango',
    'contains': 'Contiene',
    'notContains': 'No contiene',
    'startsWith': 'Empieza con',
    'endsWith': 'Termina con',
    'andCondition': 'Y',
    'orCondition': 'O',
    'noRowsToShow': 'No hay filas para mostrar',
    'filterSelectAll': 'Seleccionar todo',
    'filterClearButton': 'Limpiar',
    'applyFilterButton': 'Aplicar filtro',
}

grid_options = gb.build()
grid_options['localeText'] = spanish_locale

# Mostrar fuente Neo Sans (requiere que la fuente esté disponible)
st.markdown("""
<style>
.ag-theme-streamlit-dark {
    font-family: 'Neo Sans', Arial, sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    # theme='streamlit-dark',
    # theme="alpine-dark",
    height=None,  # opcional, ignora alto fijo
    fit_columns_on_grid_load=True,
    domLayout="autoHeight",  # <-- clave

)

selected = response['selected_rows']
# if selected and len(selected) > 0:
#     st.write("Fila seleccionada:", selected[0])
# else:
#     st.write("Selecciona una fila.")

st.write(selected)

# from st_aggrid import AgGrid
# import pandas as pd

# df = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/data/master/airline-safety/airline-safety.csv')
# AgGrid(df)