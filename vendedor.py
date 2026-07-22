import sqlite3
import pandas as pd
import streamlit as st

# Configuración de la página exclusiva para vendedores
st.set_page_config(
    page_title="Consulta de Despachos", page_icon="📦", layout="wide"
)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
conn = sqlite3.connect("database.db", check_same_thread=False)

# --- INTERFAZ DE CONSULTA ---
st.image("logo.png", width=120)
st.title("Despachos Juguetes - Vista de Vendedor")

st.subheader("📊 Historial y Consulta de Despachos")

# Cargar datos ordenados automáticamente por fecha del más reciente al más antiguo
df = pd.read_sql_query(
    "SELECT * FROM despachos ORDER BY fecha DESC, id DESC", conn
)

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
