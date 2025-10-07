from dataclasses import dataclass

import streamlit as st
from frontend import session_state_start, get_firm, Pedidos
from functions import *
from streamlit_calendar import calendar ## https://pypi.org/project/streamlit-calendar/


session_state_start()
if not "eventClick" in st.session_state:
    st.session_state.eventClick = None

## TOOLS
## ____________________________________________________________________________________________________________________________________________________________________

@dataclass
class cal_hito:
    fecha: datetime
    alarma: int # 🟥1,🟨2,🟩3

def colores(x):
    if x == 1: return 'red'
    if x == 2: return 'orange'
    else: return 'green'

hoy = datetime.now().strftime(r'%Y-%m-%d')

## PAGE
## ____________________________________________________________________________________________________________________________________________________________________

st.logo(r'assets\logo_extend.svg', size='large')

## PLAN ENTREGAS
col_opciones, col_filtros, col_vistas = st.columns(3)

with col_opciones.expander('OPCIONES', icon='🔧', width='stretch'):
    pass

with col_filtros.expander('FILTROS', icon='🔍', width='stretch'):
    pass

vistas = ['GANT ANUAL', 'MESES']
vista = col_vistas.selectbox("VISTAS", options=vistas, label_visibility='collapsed', accept_new_options=False, key='cb_entregas_view')

## DATOS
df = get_hitos()
df['color'] = df['alarma'].apply(colores)
# st.write(df)

calendar_events = []
for i in df.index:
    l = {
        "title": df['nombre'][i],
        "start": datetime.strftime(df['fecha_plan'][i], r'%Y-%m-%d'),
        "allDay": True,
        "backgroundColor": df['color'][i],
        "borderColor": df['color'][i],
        "resourceId": f'{df['bu_id'][i]}_ENTREGAS', # df['bu_id'][i],
        # "extendedProps": {
        #     "description": df['nombre'][i]
        # },
        # "titleAttr": df['nombre'][i]
    }
    calendar_events.append(l)

custom_css="""
    .fc {
        font-family: "Neo Sans", sans-serif !important;
    }
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
    /* Ancho de las cabeceras de las columnas (días) */
    .fc-col-header-cell {
        min-width: 80px !important;
        width: 80px !important;
    }
    .fc-event {
        font-size: 1rem !important;
        padding: 4px !important;
        cursor: pointer;
    }
"""

## GANT ANUAL
if vista == vistas[0]:
    calendar_options = {
        'locale': 'esLocale',
        "editable": False,
        "selectable": False,
        "height": "auto",
        "initialView": 'resourceTimelineYear', ## "resourceTimelineMonth",
        "duration": {"years": 1},
        "slotDuration": {"months": 1},   # Cada columna es 1 mes
        "slotLabelFormat": [
                # {'year': 'numeric', 'month': 'short'}, ## Nivel superior
                # {"day": "numeric"}, ## Nivel inferior
                {"month": "short"}, ## SOLO meses "short" = Jan, Feb etc
        ],
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": ""
        },
        "resourceGroupField": 'Business Unit',  
    }
    calendar_options['resourceAreaColumns'] = [
        {'field': 'title', "headerContent": calendar_options['resourceGroupField']},
        {'field': 'info', "headerContent": 'info'},
    ]
    calendar_options['resources'] = []
    for bu in df['bu_id'].unique():
        res = {
            'id': f'{bu}_ENTREGAS',
            calendar_options['resourceGroupField']: bu,
            "title": "ENTREGAS",
            'info': 'xxx',
        }
        calendar_options['resources'].append(res)


## MESES
if vista == vistas[1]:
    calendar_options = {
        'locale': 'esLocale',
        "editable": False,
        "selectable": False,
        "height": "auto",
        "initialView": "multiMonthYear",
        'duration': { 'months': 4 },
        "firstDay": 1,  # 0 = domingo, 1 = lunes, 2 = martes, ...
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": ""
        },
    }
    custom_css = '''
    /* Variable para la fuente */
    :root {
        --mi-fuente-calendario: 'Neo Sans, sans-serif';
    }

    /* Aplica la fuente al contenedor de multiMonthYear */
    .fc-multi-month-year {
        font-family: var(--mi-fuente-calendario) !important;
    }

    /* Oculta las cabeceras de columnas solo para multiMonthYear */
    .fc-multi-month-year .fc-col-header,
    .fc-multi-month-year .fc-col-header-cell {
        display: none !important;
    }

    '''


## VISTA
selected_event = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css
)

# Mostrar evento seleccionado
if selected_event:
    if selected_event.get("eventClick", None):
        st.session_state.eventClick = selected_event["eventClick"]

if st.session_state.eventClick:
    dicto = st.session_state.eventClick['event']
    df_select = pd.DataFrame([dicto])
    st.dataframe(
        df_select,
        hide_index=True
    )