import streamlit as st

st.set_page_config(
    page_title="PPI Project (⚠️ Under Contruction)",
    # page_icon='🎛️',
    page_icon=r'assets\logo.svg',
    layout="wide", # "centered",
    initial_sidebar_state= "auto" # "collapsed"
)

## PAGES
pg_home = st.Page(r'pages\home.py', title='HOME', icon=':material/home:')
pg_pedidos = st.Page(r'pages\pedidos.py', title='PEDIDOS', icon=':material/box:')
pg_business_unit = st.Page(r'pages\busines_unit.py', title='BUSINESS UNIT', icon=':material/business_center:')
pg_bi_dashboards = st.Page(r'pages\bi_dashboards.py', title='BI / DASHBOARDS', icon=':material/monitoring:')
pg_chat_ia = st.Page(r'pages\chat_ia.py', title='ARTIFICIAL INTELLIGENCE', icon=':material/smart_toy:')

PG = st.navigation(
    {
        'APP': [
            pg_home
        ],
        'COSITAS:': [
            pg_bi_dashboards,
            pg_business_unit,
            pg_pedidos,
            pg_chat_ia
        ]
    }
)

PG.run()

# st.switch_page(pg_home)

# st.title('PPI Project')
# st.divider()
# st.caption('''
# Este es el proyecto de optimización de datos del PPI

# pgonzalezp
# ''')