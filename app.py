import streamlit as st
import sqlite3
import pandas as pd
import os

# --- STREAMING_CHUNK:Configuración Inicial ---
st.set_page_config(page_title="IGNOVA - Despacho Juguetes", page_icon="🧸", layout="wide")

CARPETA_ARCHIVOS = "archivos_despachos"
if not os.path.exists(CARPETA_ARCHIVOS): os.makedirs(CARPETA_ARCHIVOS)

def conectar_db(): return sqlite3.connect("despachos.db")

# Inicialización de BD
conn = conectar_db()
conn.execute("""CREATE TABLE IF NOT EXISTS despachos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, cliente TEXT, 
    vendedor TEXT, cajas INTEGER, tipo_cajas TEXT, factura_ruta TEXT, guia_ruta TEXT)""")
conn.commit()
conn.close()

# --- STREAMING_CHUNK:Control de Vista ---
# Si la URL termina en ?modo=vendedor, ocultamos el registro
query_params = st.query_params
es_vendedor = query_params.get("modo") == "vendedor"

# --- STREAMING_CHUNK:Encabezado ---
col1, col2 = st.columns([1, 10])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=100)
    else: st.write("🧸")
with col2:
    st.title("IGNOVA - Despacho Juguetes")

# --- STREAMING_CHUNK:Lógica de Vistas ---
if es_vendedor:
    st.info("👋 Vista de Consulta para Vendedores")
    tabs = ["🔍 Consultar Despachos"]
else:
    tabs = ["📝 Registrar Despacho", "🔍 Consultar Despachos"]

tab_seleccionada = st.tabs(tabs)

# --- STREAMING_CHUNK:Pestaña de Registro (Solo Admin) ---
if not es_vendedor:
    with tab_seleccionada[0]:
        with st.expander("Registrar Nuevo Despacho", expanded=True):
            with st.form("form_reg", clear_on_submit=True):
                fecha = st.date_input("Fecha")
                cliente = st.text_input("Nombre del Cliente")
                vendedor = st.selectbox("Vendedor", ["Jeison"])
                cajas = st.number_input("Cajas", min_value=1)
                tipo = st.selectbox("Tipo de Embalaje", ["Caja Normal", "Caja PP"])
                factura_file = st.file_uploader("Factura (PDF)", type=["pdf"])
                guia_file = st.file_uploader("Foto Guía (JPG/PNG)", type=["jpg", "png"])
                
                if st.form_submit_button("Guardar Despacho"):
                    f_ruta, g_ruta = "", ""
                    if factura_file:
                        f_ruta = os.path.join(CARPETA_ARCHIVOS, f"{cliente}_{fecha}_{factura_file.name}")
                        with open(f_ruta, "wb") as f: f.write(factura_file.getbuffer())
                    if guia_file:
                        g_ruta = os.path.join(CARPETA_ARCHIVOS, f"{cliente}_{fecha}_{guia_file.name}")
                        with open(g_ruta, "wb") as f: f.write(guia_file.getbuffer())

                    conn = conectar_db()
                    conn.execute("INSERT INTO despachos (fecha, cliente, vendedor, cajas, tipo_cajas, factura_ruta, guia_ruta) VALUES (?,?,?,?,?,?,?)", 
                                 (str(fecha), cliente, vendedor, cajas, tipo, f_ruta, g_ruta))
                    conn.commit()
                    conn.close()
                    st.success(f"Despacho para {cliente} guardado.")

# --- STREAMING_CHUNK:Pestaña de Consulta (Para todos) ---
idx_consulta = 1 if not es_vendedor else 0
with tab_seleccionada[idx_consulta]:
    conn = conectar_db()
    df = pd.read_sql("SELECT * FROM despachos", conn)
    conn.close()
    
    st.subheader("Filtros de Búsqueda")
    c1, c2 = st.columns(2)
    busqueda = c1.text_input("Buscar por nombre de cliente")
    
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        filtro_fecha = c2.date_input("Filtrar por fecha específica", value=None)
        
        if busqueda: df = df[df['cliente'].str.contains(busqueda, case=False)]
        if filtro_fecha: df = df[df['fecha'].dt.date == filtro_fecha]
        
    st.dataframe(df, use_container_width=True)
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte (CSV)", csv, "despachos.csv", "text/csv")