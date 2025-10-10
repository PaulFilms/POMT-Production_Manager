import pandas as pd

import streamlit as st
from frontend import *
from functions import *

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, ColumnsAutoSizeMode
license_key = "For_Trialing_ag-Grid_Only-Not_For_Real_Development_Or_Production_Projects-Valid_Until-18_March_2021_[v2]_MTYxNjAyNTYwMDAwMA==948d8f51e73a17b9d78e03e12b9bf934"


session_state_start()

df = get_pedidos(st.session_state.pedidos)
for f in ['DB', 'firm']:
    del df[f]

df['fecha_fin'] = pd.to_datetime(df['fecha_fin'])

columns_config = {
    'id': st.column_config.Column('GPI', width=None, pinned=None),
    'info': st.column_config.Column('DESCRIPCIÓN GPI', width=None, pinned=None),
    '#': st.column_config.Column('#', width=50, pinned=False),
    'bu_id': st.column_config.Column('BUS. UNIT', width='small'),
    'planificador': st.column_config.Column('IP', width='small'),
    'fecha_ini': st.column_config.DatetimeColumn('FECHA INICIO', format="YYYY-MM-DD", width='small'),
    'fecha_fin': st.column_config.DatetimeColumn('FECHA FIN', format="YYYY-MM-DD", width='small'),
    '∑_hitos': st.column_config.NumberColumn('∑ HITOS', width=50),
    '∑_acciones': st.column_config.NumberColumn('∑ ACCIONES', width=50),
    'pde_retraso_dias': st.column_config.NumberColumn('PDE RETRASO (Días)', width='small'),
    'pde_material_critico': st.column_config.Column('PDE MATERIAL CRÍTICO', width='small'),
    'pde_description': st.column_config.Column('PDE DESCRIPCIÓN', width='small'),
    'pde_actualizado': st.column_config.DatetimeColumn('PDE ACTUALIZACIÓN', format="YYYY-MM-DD", width='small'),
    'pde_usuario': st.column_config.Column('PDE USUARIO', width='small'),
}

# st.dataframe(
#     df,
#     row_height=50
# )

# st.write(df['alarma'].iloc[0], str(type(df['alarma'].iloc[0])))
## 

# gb = GridOptionsBuilder.from_dataframe(df)
# grid_options = gb.build()

headerStyle = {
    "fontFamily": "Neo Sans, sans-serif",
    "fontSize": "18px",
    "fontWeight": "bold",  # opcional
    # "color": "#E9D5D5"     # opcional
}

# Estilo para filas según alarma
row_style_js = JsCode("""
    function(params) {
        if (params.data.alarma == 1) {
            return { backgroundColor: '#4a1e1e', color: 'white' };
        } 
        //    else if (params.data.alarma == 2) {
        //    return { backgroundColor: '#4a3b1e', color: 'white' };
        //}
        return null;
    }
""")

cell_style = {
    "fontSize": "15px",
    "fontFamily": "Neo Sans, sans-serif",
    "display": "flex",
    "alignItems": "center",
}

cell_style_dias = JsCode("""
function(params) {
    if (params.value >= 0) {
        return { fontWeight: 'bold', color: 'green', "fontSize": "18px", "display": "flex", "alignItems": "center",};
    } else {
        return { fontWeight: 'bold', color: 'red', "fontSize": "18px", "display": "flex", "alignItems": "center", };
    }
}
""")

cell_style_truncate = JsCode("""
function(params) {
  return {
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    "fontFamily": "Neo Sans, sans-serif",
    "fontSize": "15px", 
    "display": "flex", "alignItems": "center",
  }
}
""")

checkbox_col = {
    "headerName": "",
    "field": "checkbox",
    "checkboxSelection": True,
    "headerCheckboxSelection": True,  # checkbox en el header para seleccionar todo
    "pinned": "left",
    "width": 40,
    "maxWidth": 40,
    "sortable": False,
    "filter": False,
    "resizable": False,
}

fecha_params = {
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

valueFormatter = JsCode("""
    function(params) {
        if (params.value) {
            const date = new Date(params.value);
            const year = date.getFullYear();
            const month = ('0' + (date.getMonth() + 1)).slice(-2);
            const day = ('0' + date.getDate()).slice(-2);
            return year + '-' + month + '-' + day;
        } else {
            return '';
        }
    }
""")

comparator =  JsCode("""
    function(filterLocalDateAtMidnight, cellValue) {
        var parts = cellValue.split('-');
        var cellDate = new Date(parts[0], parts[1] - 1, parts[2]);
        if (cellDate < filterLocalDateAtMidnight) return -1;
        if (cellDate > filterLocalDateAtMidnight) return 1;
        return 0;
    }
""")

column_defs = [
    checkbox_col,
    {"field": 'id', 'filter': 'agTextColumnFilter', 'headerStyle': headerStyle, "headerName": "GPI"}, # , 'cellStyle': cell_style_truncate
    {
        "headerName": "INFO",
        "children": [
            {"pinned": "true", "field": 'info', 'filter': 'agTextColumnFilter', "headerName": "DESCRIPCIÓN"},
            {"columnGroupShow": "open", "field": 'bu_id', 'filter': 'agTextColumnFilter',  "headerName": "BUSINESS UNIT"},
            {"columnGroupShow": "open", "field": 'planificador', 'filter': 'agTextColumnFilter',  "headerName": "PLANIFICADOR"},
        ]
    },
    {
        "headerName": "FECHAS",
        "children": [
            # {"field": 'fecha_ini', "columnGroupShow": "open", "filter": "agDateColumnFilter", "type":["dateColumnFilter"]}, 
            {
                "field": 'fecha_ini', 
                "width": 130, "minWidth": 130, "maxWidth": 130,
                "columnGroupShow": "open", 
                "filter": 'agTextColumnFilter',  # "agDateColumnFilter", 
                "filterParams": {"customFormatString": "yyyy-MM-dd"}, 
                "type":["agTextColumnFilter", "customDateTimeFormat"], # agTextColumnFilter
                "valueFormatter": valueFormatter 
            }, 
            {
                "field": 'fecha_fin', 
                "width": 130, "minWidth": 130, "maxWidth": 130,
                "pinned": "true", 
                "filter": 'agTextColumnFilter', # "agDateColumnFilter", "filterParams": {"customFormatString": "yyyy-MM-dd", "browserDatePicker": True, "comparator": comparator}, 
                # "type":["dateColumnFilter", "customDateTimeFormat"], 
                "valueFormatter": valueFormatter 
            }, 
            
            # {"field": 'DT', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            # {"field": 'PL', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            # {"field": 'PR', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            # {"field": 'EM', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            # {"field": 'CA', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50},
        ]
    },
    {"field": '∑_hitos', "headerName": "∑ HITOS", "width": 100,},
    {"field": '∑_acciones', "headerName": "∑ ACCIONES", "width": 100,},
    {
        "headerName": "ALARMAS",
        "children": [
            {"field": '#', "pinned": "true" }, 
            {"field": 'LM', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            {"field": 'DT', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            {"field": 'PL', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            {"field": 'PR', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            {"field": 'EM', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50}, 
            {"field": 'CA', "columnGroupShow": "open", "width": 50, "minWidth": 50, "maxWidth": 50},
        ]
    },
    {
        "headerName": "CAMINOS CRÍTICOS",
        "children": [
            {"field": "pde_retraso_dias", 'cellStyle': cell_style_dias},  # Visible cuando el grupo está cerrado
            {"field": "pde_material_critico", "columnGroupShow": "open"},    # Visible cuando el grupo está abierto
            {"field": "pde_description", "columnGroupShow": "open"},      # También visible solo cuando está abierto
            {"field": 'pde_actualizado', "columnGroupShow": "open"},  
            {"field": 'pde_usuario', "columnGroupShow": "open"},  
        ]
    },
    {"field": 'Alarma', "hide": "true"},
]
# Forzar el checkbox
# column_defs[0]['checkboxSelection'] = True
# column_defs[0]['headerCheckboxSelection'] = True




gb = GridOptionsBuilder.from_dataframe(df)

gb.configure_side_bar(filters_panel=True)
gb.configure_default_column(floatingFilter=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)

# gb.configure_side_bar(
#     filters_panel=True,
#     columns_panel=True
# )

grid_options = gb.build()

grid_options['defaultColDef']["cellStyle"] = cell_style
# grid_options['getRowStyle'] = row_style_js  # gb.configure_grid_options(getRowStyle=row_style_js)
grid_options['columnDefs'] = column_defs
grid_options['suppressMovableColumns'] = True # Bloquear reordenar columnas
grid_options['rowHeight'] = 50 # Definir altura fija de filas
grid_options['columnDefs'][0]['checkboxSelection'] = True
# grid_options['columnDefs'][0]['headerCheckboxSelection'] = True
# grid_options['defaultColDef']['wrapText'] = True
# grid_options['defaultColDef']['autoHeight'] = True

# Opcional: abrir sidebar de columnas por defecto
# grid_options['sideBar'] = {
#     "toolPanels": [
#         {
#             "id": "columns",
#             "labelDefault": "Columns",
#             "labelKey": "columns",
#             "iconKey": "columns",
#             "toolPanel": "agColumnsToolPanel",
#             "toolPanelParams": {
#                 "suppressRowGroups": True,
#                 "suppressValues": True,
#                 "suppressPivots": True,
#                 "suppressPivotMode": True
#             }
#         },
#         {
#             "id": "filters",
#             "labelDefault": "Filters",
#             "labelKey": "filters",
#             "iconKey": "filter",
#             "toolPanel": "agFiltersToolPanel"
#         }
#     ],
#     "defaultToolPanel": "columns"
# }

headers = []
for e in column_defs:
    if isinstance(e, dict):
        if e.get('field', None):
            headers.append(e['field'])
        elif e.get("children", None):
            for ch in e['children']:
                if ch.get('field', None):
                    headers.append(ch['field'])

with st.popover('HEADERS'):
    for h in headers:
        st.checkbox(h, value=True)

response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    allow_unsafe_jscode=True,
    # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
    height=None,  # opcional, ignora alto fijo
    # fit_columns_on_grid_load=True,
    domLayout="autoHeight",  # <-- clave
    license_key=license_key,
)

selected = response['selected_rows']
st.write(str(type(selected)))
# if selected != None:
if selected is not None and len(selected) > 0:
    
    st.dataframe(
        selected,
        hide_index=True
    )