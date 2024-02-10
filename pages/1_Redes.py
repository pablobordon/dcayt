import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os

#configurar página
st.set_page_config(page_title="Redes", page_icon="👤", layout="wide")

# Insertar CSS personalizado
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

################ --- DATOS ---


# Definición de la función para cargar datos
@st.cache_data
def cargar_datos_excel(ruta_archivo, usecols, nrows):
    return pd.read_excel(
        io=ruta_archivo,
        engine="openpyxl",
        skiprows=0,
        usecols=usecols,
        nrows=nrows,
    )

# Función ajustada para obtener la ruta relativa de los archivos
def obtener_ruta_relativa(nombre_archivo):
    directorio_base = os.getcwd()  # Obtiene el directorio de trabajo actual
    ruta_completa = os.path.join(directorio_base, "datos", nombre_archivo)
    if not os.path.isfile(ruta_completa):  # Verifica si la ruta no existe
        # Alternativa: busca la ruta relativa desde la raíz del proyecto
        ruta_completa = os.path.join(directorio_base, "pages", "datos", nombre_archivo)
        if not os.path.isfile(ruta_completa):  # Si aún no encuentra el archivo, intenta otra estructura de directorio
            directorio_base = os.path.dirname(os.path.abspath(__file__))
            ruta_completa = os.path.join(directorio_base, "datos", nombre_archivo)
    return ruta_completa

# Uso de la función para cargar los archivos con rutas relativas
df_proyectos = cargar_datos_excel(obtener_ruta_relativa("Proyectos2.xlsx"), "A:Q", 51)
df_participa = cargar_datos_excel(obtener_ruta_relativa("Participa.xlsx"), "A:E", 279)
df_personas = cargar_datos_excel(obtener_ruta_relativa("Personas.xlsx"), "A:J", 431)



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
# Asegúrate de que "Programa de Estudios del Ambiente" esté entre las opciones disponibles, si no, ajusta el texto a un valor válido.
valor_default_radicacion = ["Programa de Estudios del Ambiente"] if "Programa de Estudios del Ambiente" in df_fusion['Radicación'].unique() else []

radicacion_filtro = st.sidebar.multiselect('Radicación del proyecto', options=df_fusion['Radicación'].unique(), default=valor_default_radicacion)


#Por Estado
estado_unicos =df_fusion['Estado'].unique()


# Asegúrate de que "En ejecución" esté entre las opciones disponibles, si no, ajusta el texto a un valor válido.
valor_default_estado = ["En ejecución"] if "En ejecución" in df_fusion['Estado'].unique() else []

estado_filtro = st.sidebar.multiselect('Estado del proyecto', estado_unicos, default=valor_default_estado)


#Filtrado por 'Tipo'
tipos_unicos =df_fusion['Tipo'].unique() # Extrae los valores únicos de la columna 'Tipo' para usarlos en el multiselector
# Asegúrate de que "Investigación" esté entre las opciones disponibles, si no, ajusta el texto a un valor válido.
valor_default_tipo = ["Investigación"] if "Investigación" in df_fusion['Tipo'].unique() else []

tipos_seleccionados = st.sidebar.multiselect('Tipo de proyecto', tipos_unicos, default=valor_default_tipo)



#### Investigador


st.sidebar.markdown("""
    <h2 style='text-align: left; font-size: 16px;'>Por Investigador</h2>
    """, unsafe_allow_html=True)


# Agregar un campo de entrada en el sidebar para filtrar por apellido
apellido_filtro = st.sidebar.text_input("Apellido del investigador:", value="")
# Normalizar el texto de entrada a minúsculas para hacer la comparación insensible a mayúsculas/minúsculas
apellido_filtro = apellido_filtro.lower()


#Por tipo docente
# Asegúrate de que las condiciones deseadas estén entre las opciones disponibles, si no, ajusta los textos a valores válidos.
valores_default_condicion = ["Docente", "Auxiliar graduado", "Auxiliar estudiante"]
valores_default_condicion = [valor for valor in valores_default_condicion if valor in df_fusion['Condición'].unique()]

tipo_docente_filtro = st.sidebar.multiselect('Condición del Investigador', options=df_fusion['Condición'].unique(), default=valores_default_condicion)


# Aplicar los filtros seleccionados
df_filtrado = df_fusion[df_fusion['Radicación'].isin(radicacion_filtro) & 
                        df_fusion['Condición'].isin(tipo_docente_filtro) &
                        df_fusion['Estado'].isin(estado_filtro) &
                        df_fusion['Tipo'].isin(tipos_seleccionados) &
                        df_fusion['apellido'].str.lower().str.contains(apellido_filtro) 
                        ]



## cerciorarse de que se está seleccionando algo
if df_filtrado.empty:
    st.warning("No hay datos disponibles basados en los filtros realizados.")
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


st.markdown("""


<ul style='font-size: 13px; color: grey; margin-top: 0px;'>
    <strong>Proyecto</strong>: 🟥 (Color rojo)
    <strong>Director</strong>: 🟡 (Color dorado)
    <strong>Codirector</strong>: 🟢 (Color verde claro)
    <strong>Investigador</strong>: 🔵 (Color azul claro)
    <strong>Estudiante</strong>: 🟣 (Color rosa claro)
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
    'Codirector': 'mediumaquamarine',
    'Investigador': 'lightsteelblue',
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
    net.add_node(nombre_proyecto, title=f"{row['Nombre_y']}", label=nombre_proyecto, color="#CD5C5C", size=10)
    
    # Conectar persona con proyecto
    net.add_edge(apellido, nombre_proyecto)

# Generar el gráfico y guardarlo como HTML
tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
net.save_graph(tmpfile.name)

# Usar st.components.v1.html para mostrar el gráfico de red en Streamlit
HtmlFile = open(tmpfile.name, 'r', encoding='utf-8')
source_code = HtmlFile.read() 
st.components.v1.html(source_code, height=800, scrolling=True)




st.markdown("""---""")