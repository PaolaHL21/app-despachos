import os
import sqlite3
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Control de Despachos", page_icon="📦", layout="wide"
)

# Directorio para archivos subidos
UPLOAD_DIR = "uploads"
os.makedirs(os.path.join(UPLOAD_DIR, "facturas"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "guias"), exist_ok=True)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS despachos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        cliente TEXT,
        vendedor TEXT,
        cajas INTEGER,
        embalaje TEXT,
        factura_path TEXT,
        guia_path TEXT
    )
"""
)
conn.commit()

# --- INTERFAZ DE USUARIO CON TÍTULO Y LOGO PERSONALIZADO ---
st.image(
    "logo.png", width=120
)  # Asegúrate de mantener tu archivo de logo en la carpeta
st.title("📦 Sistema de Gestión y Control de Despachos")

menu = ["Registrar Despacho", "Consultar Despachos"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

if choice == "Registrar Despacho":
  st.subheader("Registrar Nuevo Despacho")

  with st.form("form_despacho", clear_on_submit=True):
    fecha = st.date_input("Fecha")
    cliente = st.text_input("Nombre del Cliente")
    vendedor = st.selectbox("Vendedor", ["Jeison", "Otro Vendedor"])
    cajas = st.number_input("Cajas", min_value=1, step=1)

    # Tipo de embalaje actualizado con solo Normal y PP
    embalaje = st.selectbox("Tipo de Embalaje", ["Normal", "PP"])

    st.markdown("---")
    st.subheader("📎 Archivos Adjuntos")
    col3, col4 = st.columns(2)

    with col3:
      factura_file = st.file_uploader(
          "Cargar Factura (PDF)", type=["pdf"], key="factura"
      )
    with col4:
      guia_file = st.file_uploader(
          "Cargar Foto de Guía", type=["png", "jpg", "jpeg"], key="guia"
      )

    submit_button = st.form_submit_button("Guardar Despacho")

    if submit_button:
      if not cliente:
        st.warning("Por favor, ingresa el nombre del cliente.")
      else:
        # Guardar archivos físicos en la carpeta local
        factura_path = ""
        if factura_file is not None:
          factura_path = os.path.join(
              UPLOAD_DIR, "facturas", factura_file.name
          )
          with open(factura_path, "wb") as f:
            f.write(factura_file.getbuffer())

        guia_path = ""
        if guia_file is not None:
          guia_path = os.path.join(UPLOAD_DIR, "guias", guia_file.name)
          with open(guia_path, "wb") as f:
            f.write(guia_file.getbuffer())

        # Guardar registro en SQLite
        cursor.execute(
            """
                INSERT INTO despachos (fecha, cliente, vendedor, cajas, embalaje, factura_path, guia_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(fecha),
                cliente,
                vendedor,
                cajas,
                embalaje,
                factura_path,
                guia_path,
            ),
        )
        conn.commit()
        st.success("¡Despacho registrado con éxito!")

elif choice == "Consultar Despachos":
  st.subheader("📊 Historial y Consulta de Despachos")

  df = pd.read_sql_query("SELECT * FROM despachos", conn)

  if not df.empty:
    busqueda = st.text_input("🔍 Buscar por cliente o vendedor:")
    if busqueda:
      df = df[
          df["cliente"].str.contains(busqueda, case=False, na=False)
          | df["vendedor"].str.contains(busqueda, case=False, na=False)
      ]

    st.dataframe(df, use_container_width=True)

    # Exportar a CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar datos en CSV",
        data=csv,
        file_name="reporte_despachos.csv",
        mime="text/csv",
    )
  else:
    st.info("No hay despachos registrados todavía.")
