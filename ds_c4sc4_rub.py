
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

if not data_filtrada.empty:
    # 1. Contar los datos y limpiar el DataFrame
    conteo_desempeno = data_filtrada["performance_score"].value_counts().reset_index()
    conteo_desempeno.columns = ["Puntaje", "Empleados"]
    
    # 2. Forzar que el puntaje sea texto y ordenarlo correctamente
    conteo_desempeno["Puntaje"] = conteo_desempeno["Puntaje"].astype(int).astype(str)
    conteo_desempeno = conteo_desempeno.sort_values("Puntaje")
    
    # 3. Crear el Bar Chart con Tooltip personalizado
    fig = px.bar(
        conteo_desempeno,
        x="Puntaje",
        y="Empleados",
        title="Frecuencia de los Puntajes de Desempeño",
        color_discrete_sequence=["#2E86C1"],
        # Ajustamos el tooltip para que solo muestre las variables limpias
        hover_data={"Puntaje": True, "Empleados": True}
    )
    
    # 4. Rotar etiquetas del eje X a 0 grados (para que queden derechas/paradas)
    fig.update_xaxes(tickangle=0, type='category')
    
    # 5. Ajustar títulos de los ejes
    fig.update_layout(
        xaxis_title="Puntaje de Desempeño",
        yaxis_title="Cantidad de Empleados"
    )
    
    # 6. Desplegar gráfico
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


st.subheader("💰 Relación entre Edad y Salario")

# Reutilizamos el filtro que ignora el género para ver la distribución completa
if not data_grafico_horas.empty:
    
    # Crear gráfico de dispersión básico
    fig_dispersion = px.scatter(
        data_grafico_horas,
        x="age",
        y="salary",
        color="gender",  # Diferencia los puntos por género usando colores
        title="Dispersión de Salarios por Edad",
        labels={"age": "Edad (Años)", "salary": "Salario Mensual"},
        color_discrete_sequence=["#2E86C1", "#E74C3C"]
    )
    
    # Desplegar en Streamlit
    st.plotly_chart(fig_dispersion, use_container_width=True)
else:
    st.warning("No hay datos disponibles para generar el gráfico de dispersión.")

# ==============================================================================
# SECCIÓN: GRÁFICO DE DISPERSIÓN - HORAS TRABAJADAS VS DESEMPEÑO (CORREGIDO)
# ==============================================================================
st.subheader("📈 Horas Trabajadas vs. Puntaje de Desempeño")

if not data_grafico_horas.empty:
    
    # 1. Hacemos una copia temporal para no alterar tus datos originales
    df_dispersion = data_grafico_horas.copy()
    
    # 2. Forzamos a que el desempeño sea texto/categoría para eliminar decimales en el eje Y
    df_dispersion["performance_score"] = df_dispersion["performance_score"].astype(int).astype(str)
    
    # 3. Ordenamos de forma ascendente para que el eje Y vaya del 1 al 5 correctamente
    df_dispersion = df_dispersion.sort_values("performance_score")
    
    # 4. Crear el gráfico usando px.strip (gráfica de dispersión óptima para categorías)
    # Esto distribuye los puntos de forma sutil para que no se encimen en una sola línea delgada
    fig_horas_desempeno = px.strip(
        df_dispersion,
        x="average_work_hours",
        y="performance_score",
        color="gender",
        title="Relación entre Horas Mensuales y Rendimiento",
        labels={"average_work_hours": "Horas Trabajadas Promedio", "performance_score": "Puntaje de Desempeño"},
        color_discrete_sequence=["#2E86C1", "#E74C3C"]
    )
    
    # 5. Forzar el eje Y a ser puramente categórico
    fig_horas_desempeno.update_yaxes(type='category')
    
    # 6. Hacer que los puntos sean un poco más grandes y estilizados
    fig_horas_desempeno.update_traces(marker=dict(size=7, opacity=0.8))
    
    # Desplegar la gráfica corregida
    st.plotly_chart(fig_horas_desempeno, use_container_width=True)
else:
    st.warning("No hay datos disponibles para generar el gráfico de rendimiento vs horas.")
