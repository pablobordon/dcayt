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
# Asegúrate de que "Programa de Estudios del Ambiente" esté entre las opciones disponibles, si no, ajusta el texto a un valor válido.
valor_default_radicacion = ["Centro de Investigación e Innovación Tecnológica"] if "Centro de Investigación e Innovación Tecnológica" in df_fusion['Radicación'].unique() else []

radicacion_filtro = st.sidebar.multiselect('Radicación del proyecto', options=df_fusion['Radicación'].unique(), default=valor_default_radicacion)

#Por Estado
estado_unicos =df_fusion['Estado'].unique()
estado_filtro=st.sidebar.multiselect('Estado del proyecto',estado_unicos,default=df_fusion['Estado'].unique())

#Filtrado por 'Tipo'
tipos_unicos =df_fusion['Tipo'].unique() # Extrae los valores únicos de la columna 'Tipo' para usarlos en el multiselector
tipos_seleccionados = st.sidebar.multiselect('Tipo de proyecto', tipos_unicos,default=df_fusion['Tipo'].unique()) # Sidebar con multiselector


#### Investigador


st.sidebar.markdown("""
    <h2 style='text-align: left; font-size: 16px;'>Por Investigador</h2>
    """, unsafe_allow_html=True)


# Agregar un campo de entrada en el sidebar para filtrar por apellido
apellido_filtro = st.sidebar.text_input("Apellido del investigador:", value="")
# Normalizar el texto de entrada a minúsculas para hacer la comparación insensible a mayúsculas/minúsculas
apellido_filtro = apellido_filtro.lower()


# Aplicar los filtros seleccionados
df_filtrado = df_fusion[df_fusion['Radicación'].isin(radicacion_filtro) & 
                        df_fusion['Estado'].isin(estado_filtro) &
                        df_fusion['Tipo'].isin(tipos_seleccionados) &
                        df_fusion['apellido'].str.lower().str.contains(apellido_filtro) 
                        ]



## cerciorarse de que se está seleccionando algo
if df_filtrado.empty:
    st.warning("No hay datos disponibles basados en los filtros realizados. Recuerde no dejar opción sin seleccionar al filtrar.")
    st.stop() # This will halt the app from further execution.



##########---------------MAPA##########################

########## Mapa #########

import folium
from streamlit_folium import st_folium


st.markdown("<h3 style='text-align: center; color: grey;'>Zona de influencia de proyectos</h3>", unsafe_allow_html=True)

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
<strong>Proyecto de Investigación</strong>: 🔵 (Color azul claro) 
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

#Añadir marcadores para los proyectos
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
#df_residencias = df_filtrado.dropna(subset=['LATITUDE', 'LONGITUDE'])
#for _, row in df_residencias.iterrows():
#    # Modificar aquí para cambiar el contenido del popup
#    popup_content = f"""
#    <b>Investigador:</b><br>
#    <b>Proyecto:</b> {row['Nombre_y']}
#    """
#    folium.CircleMarker(
#        location=[row['LATITUDE'], row['LONGITUDE']],
#        radius=5,  # Tamaño del marcador
#        color='purple',  # Color diferenciado para residencias
#        fill=True,
#        fill_color='purple',
#        popup=folium.Popup(popup_content, max_width=300),
#    ).add_to(m)


st_folium(m, height=600, width=1025)




st.markdown("""---""")