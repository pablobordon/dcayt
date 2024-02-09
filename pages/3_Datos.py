import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile


#configurar página
st.set_page_config(page_title="Datos", page_icon="#️⃣", layout="wide")



################ --- DATOS ---

df_proyectos = pd.read_excel(
    io="/home/pablo/Proyectos/DCAyT/Streamlit/datos/Proyectos2.xlsx",
    engine="openpyxl",
    skiprows=0,
    usecols="A:Q",
    nrows=51,
    )

df_participa = pd.read_excel(
    io="/home/pablo/Proyectos/DCAyT/Streamlit/datos/Participa.xlsx",
    engine="openpyxl",
    skiprows=0,
    usecols="A:E",
    nrows=279,
    )

df_personas = pd.read_excel(
    io="/home/pablo/Proyectos/DCAyT/Streamlit/datos/Personas.xlsx",
    engine="openpyxl",
    skiprows=0,
    usecols="A:J",
    nrows=431,
    )


@st.cache_data
def cargar_datos_excel(ruta_archivo, usecols, nrows):
    return pd.read_excel(
        io=ruta_archivo,
        engine="openpyxl",
        skiprows=0,
        usecols=usecols,
        nrows=nrows,
    )

df_proyectos = cargar_datos_excel("/home/pablo/Proyectos/DCAyT/Streamlit/datos/Proyectos2.xlsx", "A:Q", 51)
df_participa = cargar_datos_excel("/home/pablo/Proyectos/DCAyT/Streamlit/datos/Participa.xlsx", "A:E", 279)
df_personas = cargar_datos_excel("/home/pablo/Proyectos/DCAyT/Streamlit/datos/Personas.xlsx", "A:J", 431)


################# --- SIDEBAR ---

# Fusionar los DataFrames para tener toda la información relevante
df_fusion = pd.merge(df_participa, df_proyectos, on="IDproyecto")
df_fusion = pd.merge(df_fusion, df_personas, on="DNI")




# Para un título de tamaño menor y centrado en el sidebar
st.sidebar.markdown("""
    <h2 style='text-align: center; font-size: 20px;'>Filtrar a conveniencia</h2>
    """, unsafe_allow_html=True)


st.sidebar.markdown("""
    <h2 style='text-align: left; font-size: 16px;'>Por proyecto</h2>
    """, unsafe_allow_html=True)



# por Radicación
radicacion_filtro = st.sidebar.multiselect('Radicación del proyecto', options=df_fusion['Radicación'].unique(),default=df_fusion['Radicación'].unique())

#Por Estado
estado_unicos =df_fusion['Estado'].unique()
estado_filtro=st.sidebar.multiselect('Estado del proyecto',estado_unicos,default=df_fusion['Estado'].unique())

#Filtrado por 'Tipo'
tipos_unicos =df_fusion['Tipo'].unique() # Extrae los valores únicos de la columna 'Tipo' para usarlos en el multiselector
tipos_seleccionados = st.sidebar.multiselect('Tipo de proyecto', tipos_unicos,default=df_fusion['Tipo'].unique()) # Sidebar con multiselector

#Filtrado por Característica
caracteristica_unicos =df_fusion['Característica'].unique()
caracteristica_seleccionado=st.sidebar.multiselect('Característica del proyecto',caracteristica_unicos,default=df_fusion['Característica'].unique())

#Filtrado por Fecha Inicio-Finalización

# Asegurarse de que las columnas de fecha son de tipo datetime
df_fusion['Inicio'] = pd.to_datetime(df_fusion['Inicio'])
df_fusion['Finalización'] = pd.to_datetime(df_fusion['Finalización'])
# Convertir las fechas mínima y máxima a datetime.date (si es necesario)
fecha_min = df_fusion['Inicio'].min().date()
fecha_max = df_fusion['Finalización'].max().date()
# Sidebar para rango de fechas
fecha_inicio, fecha_fin = st.sidebar.slider(
    "Fechas Inicio - Finalización del proyecto",
    value=(fecha_min, fecha_max),
    format="MM/DD/YYYY"
)

#### Investigador


st.sidebar.markdown("""
    <h2 style='text-align: left; font-size: 16px;'>Por Investigador</h2>
    """, unsafe_allow_html=True)


# Agregar un campo de entrada en el sidebar para filtrar por apellido
apellido_filtro = st.sidebar.text_input("Apellido del investigador:", value="")
# Normalizar el texto de entrada a minúsculas para hacer la comparación insensible a mayúsculas/minúsculas
apellido_filtro = apellido_filtro.lower()


#Por tipo docente
tipo_docente_filtro = st.sidebar.multiselect('Condición del Investigador', options=df_fusion['Condición'].unique(),default=df_fusion['Condición'].unique())

#Por area
area_filtro=st.sidebar.multiselect('Carrera en la cual el investigador participa',options=df_fusion['Area'].unique(),default=df_fusion['Area'].unique())

#Por Sexo
sexo_filtro = st.sidebar.multiselect('Sexo del investigador', options=df_fusion['Sexo'].unique(),default=df_fusion['Sexo'].unique())

# Por Título de Grado
titulo_grado_filtro = st.sidebar.multiselect('Título de Grado del investigador', options=df_fusion['Título de Grado'].unique(), default=df_fusion['Título de Grado'].unique())



# Aplicar los filtros seleccionados
df_filtrado = df_fusion[df_fusion['Radicación'].isin(radicacion_filtro) & 
                        df_fusion['Sexo'].isin(sexo_filtro) & 
                        df_fusion['Condición'].isin(tipo_docente_filtro) &
                        df_fusion['Estado'].isin(estado_filtro) &
                        df_fusion['Area'].isin(area_filtro) &
                        (df_fusion['Inicio'].dt.date >= fecha_inicio) &
                        (df_fusion['Finalización'].dt.date <= fecha_fin) &
                        df_fusion['Característica'].isin(caracteristica_seleccionado) & 
                        df_fusion['Tipo'].isin(tipos_seleccionados) &
                        df_fusion['apellido'].str.lower().str.contains(apellido_filtro) &
                        df_fusion['Título de Grado'].isin(titulo_grado_filtro)
                        ]



## cerciorarse de que se está seleccionando algo
if df_filtrado.empty:
    st.warning("No hay datos disponibles basados en los filtros realizados. Recuerde no dejar opción sin seleccionar al filtrar.")
    st.stop() # This will halt the app from further execution.


st.markdown("<h3 style='text-align: center; color: grey;'>Datos de Investigadores y Proyectos</h3>", unsafe_allow_html=True)

st.markdown("""---""")

st.markdown("""
<h5 style='text-align: left; color: grey;'>
Diagramas y listas para analizar el estado el estado actual de proyectos e investigadores.<br>
<ul>
    <li>Modifique el selector para obtener más información.</li>
    <li>Utilice el panel lateral para aplicar filtros específicos.</li>
</ul>
</h5>
""", unsafe_allow_html=True)


st.markdown("""---""")


# KPIs - Mostrar en dos columnas
col1, col2 = st.columns(2)

with col1:
    # Contar el número de proyectos únicos filtrados
    total_proyectos = df_filtrado['IDproyecto'].nunique()
    st.markdown(
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 50px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    st.metric(label="Proyectos", value=total_proyectos)

with col2:
    # Calcular y mostrar el número total de personas únicas involucradas en los proyectos filtrados
    total_personas = df_filtrado['DNI'].nunique()
    st.markdown(
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 50px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    st.metric(label="Investigadores", value=total_personas)


# Checkbox para mostrar/ocultar el listado de personas y proyectos
if st.checkbox('Listado de investigadores en proyectos'):
    # Renombrar las columnas para la visualización
    df_mostrar = df_filtrado[['apellido', 'Nombre', 'Nombre_y']].rename(
        columns={
            'apellido': 'Apellido',
            'Nombre': 'Nombre',
            'Nombre_y': 'Proyecto'
        }
    )
    # Mostrar la tabla con las columnas renombradas
    st.dataframe(df_mostrar, height=600)  # Puedes ajustar la altura según necesites

st.markdown("""---""")






###################################  PIE CHARTS 

# Contabilizar Personas por la categoría seleccionada
def contar_personas_por_categoria(df, categoria):
    df_personas = df.groupby(categoria)['DNI'].nunique().reset_index(name='Num_Personas')
    return df_personas

# Contabilizar Proyectos por la categoría seleccionada
def contar_proyectos_por_categoria(df, categoria):
    df_proyectos = df.groupby(categoria)['IDproyecto'].nunique().reset_index(name='Num_Proyectos')
    return df_proyectos



st.markdown("<h4 style='text-align: center; color: grey;'>Proyectos en números</h4>", unsafe_allow_html=True)

# Usar st.columns para ajustar el ancho del selector de proyectos
col_selector_der, _ = st.columns([3, 7])  # Ajusta según necesidad para el ancho del selector
categoria_derecha = col_selector_der.selectbox(
    "Selecciona la categoría para visualizar en Proyectos:",
    ['Radicación', 'Tipo', 'Línea', 'Sublínea', 'Estado'],
    key='selector_derecha'  # Clave única para este selector
)
df_proyectos_categoria = contar_proyectos_por_categoria(df_filtrado, categoria_derecha)
fig_derecha = px.pie(df_proyectos_categoria, names=categoria_derecha, values='Num_Proyectos', title=f'Número de Proyectos por {categoria_derecha}',
                     color_discrete_sequence=px.colors.sequential.Sunsetdark)
fig_derecha.update_traces(textinfo='value+percent')
st.plotly_chart(fig_derecha)





st.markdown("""---""")





st.markdown("<h4 style='text-align: center; color: grey;'>Investigadores en números</h4>", unsafe_allow_html=True)

# Usar st.columns para ajustar el ancho del selector
col_selector_izq, _ = st.columns([3, 7])  # Ajusta según necesidad para el ancho del selector
categoria_izquierda = col_selector_izq.selectbox(
    "Selecciona la categoría para visualizar en Investigadores:",
    ['Radicación', 'Area', 'Condición', 'Sexo', 'Título de Grado', 'Título Posgrado'],
    key='selector_izquierda'  # Clave única para este selector
)
df_personas_categoria = contar_personas_por_categoria(df_filtrado, categoria_izquierda)
fig_izquierda = px.pie(df_personas_categoria, names=categoria_izquierda, values='Num_Personas', title=f'Número de Investigadores por {categoria_izquierda}',
                       color_discrete_sequence=px.colors.sequential.Aggrnyl)
fig_izquierda.update_traces(textinfo='value+percent')
st.plotly_chart(fig_izquierda)

st.markdown("""---""")






st.markdown("<h4 style='text-align: center; color: grey;'>Seguimiento de proyectos en el tiempo</h4>", unsafe_allow_html=True)


import plotly.figure_factory as ff


# Función para recortar el nombre del proyecto
def recortar_nombre(nombre, limite_palabras=3):
    palabras = nombre.split()
    nombre_recortado = ' '.join(palabras[:limite_palabras])
    return nombre_recortado + "..." if len(palabras) > limite_palabras else nombre_recortado

# Aplica la función para recortar los nombres de los proyectos
df_filtrado['Nombre_recortado'] = df_filtrado['Nombre_y'].apply(recortar_nombre)

# Preparar el DataFrame para Plotly create_gantt
df_gantt = df_filtrado[['Nombre_recortado', 'Inicio', 'Finalización', 'Radicación']].rename(columns={
    'Nombre_recortado': 'Task',
    'Inicio': 'Start',
    'Finalización': 'Finish',
    'Radicación': 'Resource'
})

# Usar una paleta secuencial para asignar colores
paleta_secuencial = px.colors.sequential.Sunsetdark

# Crea un mapeo único de 'Radicación' a un color de la paleta secuencial
radicaciones_unicas = df_gantt['Resource'].unique()
num_radicaciones = len(radicaciones_unicas)
colores_asignados = {radicacion: paleta_secuencial[i * len(paleta_secuencial) // num_radicaciones] for i, radicacion in enumerate(radicaciones_unicas)}

# Convierte el DataFrame ajustado a una lista de diccionarios
tasks = df_gantt.to_dict('records')

# Crear el gráfico de Gantt
fig = ff.create_gantt(tasks, index_col='Resource', title='Proyecto', group_tasks=True, show_colorbar=True, colors=colores_asignados)

# Mostrar el gráfico en Streamlit, ajustando al ancho del contenedor
st.plotly_chart(fig, use_container_width=True)

st.markdown("""---""")

