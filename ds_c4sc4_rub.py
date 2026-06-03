import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px

# ==============================================================================
# CONFIGURACIÓN INICIAL DE DATOS (PREPARACIÓN DEL DATASET)
# ==============================================================================
data = pd.read_csv("Employee_data.csv")

columnas_seleccionadas = [
    'name_employee', 'birth_date', 'age', 'gender', 'marital_status',
    'hiring_date', 'position', 'salary', 'performance_score',
    'last_performance_date', 'average_work_hours', 'satisfaction_level', 'absences'
]
data = data[columnas_seleccionadas].copy()

# ==============================================================================
# instrucción para el despliegue de un título y una breve descripción de la aplicación web
# ==============================================================================
st.title("📊 Panel de Análisis de Empleados")

st.markdown("""
Bienvenido a la aplicación web de gestión de talento. Este sistema permite analizar de
manera detallada la base de datos de los colaboradores de la empresa, mostrando
indicadores clave como el rendimiento, niveles de satisfacción, salarios y ausentismo
para facilitar la toma de decisiones estratégicas en Recursos Humanos.
""")

# ==============================================================================
# despliegue del logotipo de la empresa en la aplicación web
# ==============================================================================
image = Image.open('logotipo.png')
st.image(image, caption='Logotipo de la compañía') 

# ==============================================================================
# CONTROLES Y FILTROS BASE (REQUERIDOS PARA EL FUNCIONAMIENTO DE LOS COMPONENTES)
# ==============================================================================
# despliegue de un control para seleccionar el género del empleado
selected_gender = st.radio("Selecciona el género", data["gender"].unique()) 

# despliegue de un control para seleccionar un rango del puntaje de desempeño del empleado
rango_desempeno = st.slider(
    "Selecciona el rango de puntaje de desempeño:",
    min_value=1.0, max_value=5.0, value=(1.0, 5.0), step=0.1          
)

# despliegue de un control para seleccionar el estado civil del empleado
opciones_estado_civil = data["marital_status"].unique()
estados_civiles_seleccionados = st.multiselect(
    "Selecciona uno o varios Estados Civiles:",
    options=opciones_estado_civil, default=opciones_estado_civil 
)

# Segmentación de datasets para mantener las barras comparativas por género
data_filtrada = data[
    (data["gender"] == selected_gender) & 
    (data["marital_status"].isin(estados_civiles_seleccionados)) & 
    (data["performance_score"] >= rango_desempeno[0]) & 
    (data["performance_score"] <= rango_desempeno[1])
]

data_grafico_horas = data[
    (data["marital_status"].isin(estados_civiles_seleccionados)) & 
    (data["performance_score"] >= rango_desempeno[0]) & 
    (data["performance_score"] <= rango_desempeno[1])
]

# ==============================================================================
# visualización de la distribución de los puntajes de desempeño
# ==============================================================================
st.subheader("📊 Distribución de los puntajes de desempeño")

if not data_filtrada.empty:
    # 1. Contar frecuencias y transformar la variable entera a texto para evitar decimales en el eje X
    conteo_desempeno = data_filtrada["performance_score"].value_counts().reset_index()
    conteo_desempeno.columns = ["Puntaje", "Empleados"]
    conteo_desempeno["Puntaje"] = conteo_desempeno["Puntaje"].astype(int).astype(str)
    conteo_desempeno = conteo_desempeno.sort_values("Puntaje")
    
    # 2. Configurar gráfico de barras con tooltips limpios en español
    fig_barras = px.bar(
        conteo_desempeno, x="Puntaje", y="Empleados",
        title="Frecuencia de los Puntajes de Desempeño",
        color_discrete_sequence=["#2E86C1"],
        hover_data={"Puntaje": True, "Empleados": True}
    )
    
    # 3. Forzar alineación completamente horizontal en el eje X y desplegar gráfica
    fig_barras.update_xaxes(tickangle=0, type='category')
    fig_barras.update_layout(xaxis_title="Puntaje de Desempeño", yaxis_title="Cantidad de Empleados")
    st.plotly_chart(fig_barras, use_container_width=True)
else:
    st.warning("No hay datos disponibles para generar la gráfica con los filtros actuales.")

# ==============================================================================
# visualización del promedio de horas trabajadas por el género del empleado
# ==============================================================================
st.subheader("🕒 Promedio de horas trabajadas por el género del empleado")

if not data_grafico_horas.empty:
    # 1. Agrupar mediante dataset parcial y promediar las horas redondeando el valor resultante
    df_horas = data_grafico_horas.groupby("gender", as_index=False)["average_work_hours"].mean()
    df_horas["average_work_hours"] = df_horas["average_work_hours"].round(1)
    
    # 2. Configurar barras comparativas asignando un color por cada género
    fig_horas = px.bar(
        df_horas, x="gender", y="average_work_hours", 
        title="Promedio de Horas Trabajadas (Filtrado por Estado Civil y Desempeño)",
        text="average_work_hours", color="gender",
        color_discrete_sequence=["#2E86C1", "#E74C3C"]
    )
    
    # 3. Forzar la visualización numérica encima de las barras para una lectura rápida
    fig_horas.update_traces(textposition="outside")
    st.plotly_chart(fig_horas, use_container_width=True)
else:
    st.warning("No hay datos disponibles para calcular el promedio de horas.")

# ==============================================================================
# visualización de la edad de los empleados con respecto al salario de los mismo
# ==============================================================================
st.subheader("💰 Edad de los empleados con respecto al salario de los mismos")

if not data_grafico_horas.empty:
    # 1. Diseñar el scatter plot relacionando las variables continuas de edad y sueldo
    fig_dispersion = px.scatter(
        data_grafico_horas, x="age", y="salary", color="gender", 
        title="Dispersión de Salarios por Edad",
        labels={"age": "Edad (Años)", "salary": "Salario Mensual"},
        color_discrete_sequence=["#2E86C1", "#E74C3C"]
    )
    
    # 2. Renderizar la gráfica interactiva dentro de la interfaz del sistema
    st.plotly_chart(fig_dispersion, use_container_width=True)
else:
    st.warning("No hay datos disponibles para generar el gráfico de dispersión.")

# ==============================================================================
# visualización de la relación del promedio de horas trabajadas versus el puntaje de desempeño
# ==============================================================================
st.subheader("📈 Relación del promedio de horas trabajadas versus el puntaje de desempeño")

if not data_grafico_horas.empty:
    # 1. Clonar estructura parcial y convertir el desempeño a tipo string para limpiar marcas decimales vacías
    df_strip = data_grafico_horas.copy()
    df_strip["performance_score"] = df_strip["performance_score"].astype(int).astype(str)
    df_strip = df_strip.sort_values("performance_score")
    
    # 2. Crear gráfico de tipo px.strip para mitigar el solapamiento de registros en un mismo renglón discreto
    fig_horas_desempeno = px.strip(
        df_strip, x="average_work_hours", y="performance_score", color="gender",
        title="Relación entre Horas Mensuales y Rendimiento",
        labels={"average_work_hours": "Horas Trabajadas Promedio", "performance_score": "Puntaje de Desempeño"},
        color_discrete_sequence=["#2E86C1", "#E74C3C"]
    )
    
    # 3. Forzar comportamiento estrictamente categórico en el eje Y y desplegar
    fig_horas_desempeno.update_yaxes(type='category')
    st.plotly_chart(fig_horas_desempeno, use_container_width=True)
else:
    st.warning("No hay datos disponibles para generar el gráfico de rendimiento.")

# ==============================================================================
# despliegue de una conclusión sobre el análisis mostrado en la aplicación web
# ==============================================================================
st.subheader("💡 Conclusión sobre el análisis mostrado en la aplicación web")

st.markdown("""
Tras evaluar de manera integral los indicadores clave de la plantilla, se presentan las siguientes conclusiones estratégicas para la toma de decisiones en el área de Capital Humano:

1. **Rendimiento y Distribución del Desempeño:** La mayor concentración de los colaboradores se ubica en un nivel de desempeño de **3 (satisfactorio)**. Sin embargo, existe un grupo menor pero crítico en los niveles 1 y 2 que requiere de planes de capacitación específicos o mentorías para alinear sus resultados con los objetivos de la organización.

2. **Equidad en la Jornada Laboral:** Al analizar el promedio de horas trabajadas mensualmente por género, se observa una **distribución sumamente equitativa** entre hombres y mujeres. Ambos grupos mantienen promedios de actividad prácticamente idénticos, lo que demuestra consistencia en las cargas de trabajo asignadas en toda la organización.

3. **Estructura Salarial y Edad:** La gráfica de dispersión refleja que los salarios no están correlacionados de forma lineal o directa con la edad del empleado. Esto sugiere una estructura de compensaciones basada en **puestos, responsabilidades y habilidades**, más que en la antigüedad cronológica, promoviendo una cultura de meritocracia.

4. **Productividad vs. Horas de Trabajo:** La relación entre el tiempo invertido y el puntaje de desempeño muestra que **trabajar más horas no garantiza automáticamente una mejor calificación**. Los colaboradores con rendimientos sobresalientes (niveles 4 y 5) registran un volumen de horas similar al de los niveles promedio. Esto indica que factores cualitativos, como la eficiencia, el uso de herramientas de automatización o el nivel de competencia técnica, impactan con mayor fuerza el éxito que la simple extensión de la jornada laboral.
""")
