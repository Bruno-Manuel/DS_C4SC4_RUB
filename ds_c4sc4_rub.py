
import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px

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
opciones_estado_civil = data["marital_status"].unique()
estados_civiles_seleccionados = st.multiselect("Selecciona uno o varios Estados Civiles:",
    options=opciones_estado_civil, default=opciones_estado_civil )

data_filtrada = data[
        (data["gender"] == selected_gender) & 
        (data["marital_status"].isin(estados_civiles_seleccionados)) & 
        (data["performance_score"] >= rango_desempeno[0]) & 
        (data["performance_score"] <= rango_desempeno[1])
    ]

st.subheader("📊 Distribución del Puntaje de Desempeño")

# Validar que existan datos para graficar tras aplicar los filtros
if not data_filtrada.empty:
    
    # 1. Volvemos a px.histogram porque los datos son continuos
    fig = px.histogram(
        data_filtrada, 
        x="performance_score",
        title="Frecuencia de los Puntajes de Desempeño",
        labels={"performance_score": "Puntaje de Desempeño", "count": "Número de Empleados"},
        color_discrete_sequence=["#2E86C1"] 
    )
    
    # 3. Ajustes estéticos del diseño y del eje X
    fig.update_layout(
        xaxis_title="Puntaje de Desempeño (Rango Continuo)",
        yaxis_title="Cantidad de Empleados",
    )
    
    # 4. Desplegar el gráfico interactivo corregido
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No hay datos disponibles para generar la gráfica con los filtros actuales.")


st.subheader("🕒 Horas promedio por Género")

# 1. Filtrar los datos ignorando el género para que el gráfico conserve la comparación
data_grafico_horas = data[
    (data["marital_status"].isin(estados_civiles_seleccionados)) & 
    (data["performance_score"] >= rango_desempeno[0]) & 
    (data["performance_score"] <= rango_desempeno[1])
]

if not data_grafico_horas.empty:
    # 2. Agrupar y calcular el promedio de horas usando el dataset parcialmente filtrado
    df_horas = data_grafico_horas.groupby("gender", as_index=False)["average_work_hours"].mean()
    
    # Redondear para una visualización más limpia
    df_horas["average_work_hours"] = df_horas["average_work_hours"].round(1)
    
    # 3. Crear y mostrar la gráfica de barras básica
    fig_horas = px.bar(
        df_horas, 
        x="gender", 
        y="average_work_hours", 
        title="Promedio de Horas Trabajadas (Filtrado por Estado Civil y Desempeño)",
        text="average_work_hours",
        color="gender",
        color_discrete_sequence=["#2E86C1", "#E74C3C"]
    )
    
    # Ajuste para que el número del promedio quede arriba de la barra
    fig_horas.update_traces(textposition="outside")
    
    st.plotly_chart(fig_horas, use_container_width=True)
else:
    st.warning("No hay datos disponibles para calcular el promedio de horas con los filtros seleccionados.")
