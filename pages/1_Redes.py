import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile


#configurar página
st.set_page_config(page_title="Redes", page_icon="👤", layout="wide")



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







################## ---- MAINPAGE ----


################ --- REDES DE PERSONAS ---
    
from pyvis.network import Network
import tempfile
import json

st.markdown("<h3 style='text-align: center; color: grey;'>Redes de Investigadores en proyectos</h3>", unsafe_allow_html=True)

st.markdown("""---""")



# Agregar un espacio en blanco
st.write(" ")

st.markdown("""
<h5 style='text-align: left; color: grey;'>
Este diagrama ilustra la interconexión entre investigadores y proyectos del departamento.<br>
<ul>
    <li>Interactúe con los nodos: seleccionándolos para descubrir más detalles y arrastrándolos para visualizar profundidad de la conexión.</li>
    <li>Utilice el panel lateral para aplicar filtros específicos.</li>
</ul>
</h5>

""", unsafe_allow_html=True)

# Definición de funciones
def abreviar_nombre_proyecto(nombre, max_chars=25):
    if len(nombre) > max_chars:
        abreviado = nombre[:max_chars-3] + "..."
    else:
        abreviado = nombre
    return abreviado

def formatear_apellido(apellido):
    return apellido.capitalize()

# Preparar datos (simulación de la carga de datos)
# Asumir df_fusion ya está preparado según tu descripción previa
# Aquí deberías cargar y fusionar tus dataframes como indicaste anteriormente

# Mapeo de roles a colores específicos
rol_a_color = {
    'Director': 'gold',
    'Codirector': 'lightgreen',
    'Investigador': 'lightblue',
    'Estudiante': 'lightpink',
}


# Crear un gráfico de red con configuraciones de física para movimiento dinámico
net = Network(height="750px", width="100%", bgcolor="#f0f0f0", font_color="black")

# Configurar las opciones de física para el movimiento leve y constante
options = {
    "physics": {
        "enabled": True,
        "stabilization": {"enabled": False},  # Deshabilitar la estabilización inicial puede ayudar
        "solver": "barnesHut",  # Usar un solucionador menos intensivo
        "barnesHut": {
            "gravitationalConstant": -5000,
            "centralGravity": 0.5,
            "springLength": 75,
            "springConstant": 0.05,
            "damping": 0.08,
            "avoidOverlap": 0
        },
        "minVelocity": 0.2  # Ajustar para reducir el movimiento mínimo necesario
    }
}




# Iterar sobre df_filtrado para agregar nodos y aristas
for index, row in df_filtrado.iterrows():
    apellido = formatear_apellido(row['Apellido'])
    nombre_proyecto = abreviar_nombre_proyecto(row['Nombre_y'], 25)  # Ajusta 25 al número de caracteres deseado
    rol = row['Rol']
    
    # Obtener el color basado en el rol
    color_nodo = rol_a_color.get(rol, "gray")

    # Agregar nodo de la persona con el apellido formateado
    net.add_node(apellido, title=f"Rol: {rol}", label=apellido, color=color_nodo, size=15)
    
    # Agregar nodo del proyecto diferenciado con el nombre en negrita y abreviado
    net.add_node(nombre_proyecto, title=f"{row['Nombre_y']}", label=nombre_proyecto, color="#f44336", size=10)
    
    # Conectar persona con proyecto
    net.add_edge(apellido, nombre_proyecto)

# Generar el gráfico y guardarlo como HTML
tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
net.save_graph(tmpfile.name)

# Usar st.components.v1.html para mostrar el gráfico de red en Streamlit
HtmlFile = open(tmpfile.name, 'r', encoding='utf-8')
source_code = HtmlFile.read() 
st.components.v1.html(source_code, height=800, scrolling=True)




st.markdown("""

<h6 style='text-align: left; color: grey; margin-bottom: 0px;'>
La paleta de colores se asigna de la siguiente manera:
</h6>
<ul style='font-size: 13px; color: grey; margin-top: 0px;'>
    <li><strong>Proyecto</strong>: 🟥 (Color rojo)</li>
    <li><strong>Director</strong>: 🟡 (Color dorado)</li>
    <li><strong>Codirector</strong>: 🟢 (Color verde claro)</li>
    <li><strong>Investigador</strong>: 🔵 (Color azul claro)</li>
    <li><strong>Estudiante</strong>: 🟣 (Color rosa claro)</li>
</ul>
""", unsafe_allow_html=True)



st.markdown("""---""")