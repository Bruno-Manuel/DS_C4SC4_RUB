
import streamlit as st
import pandas as pd
import datetime
from PIL import Image

data = pd.read_csv("Employee_data.csv")

columnas_seleccionadas = [
    'name_employee',
    'birth_date',
    'age',
    'gender',
    'marital_status',
    'hiring_date',
    'position',
    'salary',
    'performance_score',
    'last_performance_date',
    'average_work_hours',
    'satisfaction_level',
    'absences'
]

data = data[columnas_seleccionadas].copy()

st.title("📊 Panel de Análisis de Empleados")

st.markdown("""
Bienvenido a la aplicación web de gestión de talento. Este sistema permite analizar de
manera detallada la base de datos de los colaboradores de la empresa, mostrando
indicadores clave como el rendimiento, niveles de satisfacción, salarios y ausentismo
para facilitar la toma de decisiones estratégicas en Recursos Humanos.
""")

image = Image.open('logotipo.png')
st.image(image, caption='Logotipo de la compañia') 

selected_gender = st.radio("Selecciona el género", data["gender"].unique()) 
rango_desempeno = st.slider(
    "Selecciona el rango de puntaje de desempeño:",
    min_value=1.0,
    max_value=5.0,
    value=(1.0, 5.0), # Valores iniciales por defecto (mínimo, máximo)
    step=0.1          # Permite avanzar de décima en décima
)
selected_marital_status = st.selectbox("Selecciona el estado civil", data["marital_status"].unique())


data_filtrada = data[
    (data["gender"] == selected_gender) & 
    (data["marital_status"] == selected_marital_status) & 
    (data["performance_score"] >= rango_desempeno[0]) & 
    (data["performance_score"] <= rango_desempeno[1])
]
