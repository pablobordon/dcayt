import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os


#configurar página
st.set_page_config(page_title="Mapas", page_icon="🌐", layout="wide")


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



##########---------------MAPA##########################

########## Mapa #########

import folium
from streamlit_folium import st_folium


st.markdown("<h3 style='text-align: center; color: grey;'>Zona de influencia de proyectos y localización de investigadores</h3>", unsafe_allow_html=True)

st.markdown("""---""")


# Agregar un espacio en blanco
st.write(" ")


st.markdown("""
<h5 style='text-align: left; color: grey;'>
Este mapa permite visualizar información relacionada tanto con proyectos como con investigadores.<br>
<ul>
    <li>Seleccione los íconos para obtener más información.</li>
    <li>Utilice el panel lateral para aplicar filtros específicos.</li>
</ul>
</h5>

""", unsafe_allow_html=True)

#################
st.markdown("""
<span style='font-size: 13px;'> 
<strong>Proyecto de Extensión</strong>: 🟥 (Color rojo) / 
<strong>Proyecto de Vinculación</strong>: 🟢 (Color verde claro) / 
<strong>Proyecto de Investigación</strong>: 🔵 (Color azul claro) /
<strong>Investigador</strong>: 🟣 (Color rosa claro)
</span>
""", unsafe_allow_html=True)


# Asegurarse de que df_filtrado ya está preparado y contiene las columnas necesarias

# Filtrar el DataFrame para eliminar filas donde la latitud o la longitud de los proyectos sean NaN
df_mapa = df_filtrado.dropna(subset=['LATITUDE2', 'LONGITUDE2'])

# Definir un mapeo de colores para cada tipo de proyecto
tipo_a_color = {
    'Investigación': 'blue',
    'Vinculación': 'green',
    'Extensión': 'red',
}

# Crear un mapa de Folium
m = folium.Map(location=[-34.6037, -58.3816], zoom_start=10)  # Usar una ubicación y zoom iniciales adecuados

# Añadir marcadores para los proyectos
for _, row in df_mapa.iterrows():
    color_marcador = tipo_a_color.get(row['Tipo'], 'gray')
    popup_content = f"""
    <b>Nombre del proyecto:</b> {row['Nombre_y']}<br>
    <b>Contraparte:</b> {row['Contraparte']}<br>
    <b>Sitio:</b> <a href="{row['Sitio']}" target="_blank">Visitar sitio</a><br>
    <b>Tipo:</b> {row['Tipo']}
    """
    folium.Marker(
        location=[row['LATITUDE2'], row['LONGITUDE2']],
        popup=folium.Popup(popup_content, max_width=450),
        icon=folium.Icon(color=color_marcador),
    ).add_to(m)







# Añadir marcadores para las direcciones residenciales de los investigadores
# Asegurarse de filtrar filas donde las latitudes y longitudes residenciales sean NaN
df_residencias = df_filtrado.dropna(subset=['LATITUDE', 'LONGITUDE'])
for _, row in df_residencias.iterrows():
    # Modificar aquí para cambiar el contenido del popup
    popup_content = f"""
    <b>Investigador:</b><br>
    <b>Proyecto:</b> {row['Nombre_y']}
    """
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=5,  # Tamaño del marcador
        color='purple',  # Color diferenciado para residencias
        fill=True,
        fill_color='purple',
        popup=folium.Popup(popup_content, max_width=300),
    ).add_to(m)


st_folium(m, height=600, width=1025)





st.markdown("""
<h6 style='text-align: left; color: grey; margin-bottom: 0px;'>
La paleta de colores se asigna de la siguiente manera:
</h6>
<ul style='font-size: 13px; color: grey; margin-top: 0px;'>
    <li><strong>Proyecto de Extensión</strong>: 🟥 (Color rojo)</li>
    <li><strong>Proyecto de Vinculación</strong>: 🟢 (Color verde claro)</li>
    <li><strong>Proyecto de Investigación</strong>: 🔵 (Color azul claro)</li>
    <li><strong>Investigador</strong>: 🟣 (Color rosa claro)</li>
</ul>
""", unsafe_allow_html=True)



st.markdown("""---""")
