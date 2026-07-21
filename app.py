import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="IGNOVA - Despacho Juguetes", page_icon="🧸", layout="wide")

def conectar_db():
    return sqlite3.connect("despachos.db")

# Inicialización de BD
conn = conectar_db()
conn.execute("""CREATE TABLE IF NOT EXISTS despachos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, cliente TEXT, 
    vendedor TEXT, cajas INTEGER, tipo_cajas TEXT, factura_ruta TEXT, guia_ruta TEXT)""")
conn.commit()
conn.close()

st.image("logo.png", width=150)
st.title("IGNOVA-Despacho Juguetes")

params = st.query_params
es_vendedor = params.get("modo") == "vendedor"

if es_vendedor:
    st.info("👋 Vista de Consulta para Vendedores")
    # Solo mostramos el buscador directamente
    tab_seleccionada = st.container()
else:
    # Vista Admin: Mostramos las pestañas
    tabs = st.tabs(["📝 Registrar Despacho", "🔍 Consultar Despachos"])
    
    with tabs[0]:
        with st.expander("Registrar Nuevo Despacho", expanded=True):
            with st.form("form_reg", clear_on_submit=True):
                fecha = st.date_input("Fecha")
                cliente = st.text_input("Nombre del Cliente")
                vendedor = st.selectbox("Vendedor", ["Jeison"])
                cajas = st.number_input("Cajas", min_value=1)
                tipo = st.selectbox("Tipo de Embalaje", ["Caja Normal", "Caja PP"])
                
                if st.form_submit_button("Guardar Despacho"):
                    conn = conectar_db()
                    conn.execute("INSERT INTO despachos (fecha, cliente, vendedor, cajas, tipo_cajas, factura_ruta, guia_ruta) VALUES (?,?,?,?,?,?,?)", 
                                 (str(fecha), cliente, vendedor, cajas, tipo, "N/A", "N/A"))
                    conn.commit()
                    conn.close()
                    st.success(f"Despacho para {cliente} guardado.")
    tab_seleccionada = tabs[1]

with tab_seleccionada:
    conn = conectar_db()
    df = pd.read_sql("SELECT * FROM despachos", conn)
    conn.close()
    
    st.subheader("Búsqueda de Despachos")
    c1, c2 = st.columns(2)
    busqueda = c1.text_input("Buscar por nombre de cliente")
    
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        filtro_fecha = c2.date_input("Filtrar por fecha específica", value=None)
        
        if busqueda: df = df[df['cliente'].str.contains(busqueda, case=False)]
        if filtro_fecha: df = df[df['fecha'].dt.date == filtro_fecha]
        
    st.dataframe(df, use_container_width=True)
