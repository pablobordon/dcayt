import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os
import plotly.figure_factory as ff
#configurar página
st.set_page_config(page_title="Datos", page_icon="#️⃣", layout="wide")



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

#Filtrado por 'Tipo'
tipos_unicos =df_fusion['Tipo'].unique() # Extrae los valores únicos de la columna 'Tipo' para usarlos en el multiselector
tipos_seleccionados = st.sidebar.multiselect('Tipo de proyecto', tipos_unicos,default=df_fusion['Tipo'].unique()) # Sidebar con multiselector

#Filtrado por Característica
caracteristica_unicos =df_fusion['Característica'].unique()
caracteristica_seleccionado=st.sidebar.multiselect('Característica del proyecto',caracteristica_unicos,default=df_fusion['Característica'].unique())



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
                        df_fusion['Característica'].isin(caracteristica_seleccionado) & 
                        df_fusion['Tipo'].isin(tipos_seleccionados) &
                        df_fusion['apellido'].str.lower().str.contains(apellido_filtro) 
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
    st.metric(label="Proyectos según filtro", value=total_proyectos)

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
    st.metric(label="Investigadores según filtro", value=total_personas)


# Antes de mostrar el dataframe
st.markdown(
    """
    <style>
    .dataframe-container {
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Checkbox para mostrar/ocultar el listado de personas y proyectos
if st.checkbox('Listado de investigadores en proyectos'):
    # Renombrar las columnas y agregar "Tipo" y "Categoría" para la visualización
    df_mostrar = df_filtrado[['apellido', 'Nombre', 'Nombre_y', 'Tipo', 'Característica']].rename(
        columns={
            'apellido': 'Apellido',
            'Nombre': 'Nombre',
            'Nombre_y': 'Proyecto',
            'Tipo': 'Tipo',
            'Característica': 'Categoría'
        }
    )
    # Mostrar la tabla con las columnas renombradas
    st.dataframe(df_mostrar,width=1200)  # Removido height=600 para adaptarse al ancho del contenedor

st.markdown("""---""")


#############3 Gradico de ganth


st.markdown("<h4 style='text-align: center; color: grey;'>Seguimiento de proyectos en el tiempo</h4>", unsafe_allow_html=True)





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





###################################  KPI's

# Contabilizar Personas por la categoría seleccionada
def contar_personas_por_categoria(df, categoria):
    df_personas = df.groupby(categoria)['DNI'].nunique().reset_index(name='Num_Personas')
    return df_personas

# Contabilizar Proyectos por la categoría seleccionada
def contar_proyectos_por_categoria(df, categoria):
    df_proyectos = df.groupby(categoria)['IDproyecto'].nunique().reset_index(name='Num_Proyectos')
    return df_proyectos



###################################  PIE CHARTS 



st.markdown("<h4 style='text-align: center; color: grey;'>Proyectos por categoría</h4>", unsafe_allow_html=True)

# Actualizar la lista de categorías para incluir "Característica" y excluir "Radicación" y "Estado"
categorias = ['Tipo', 'Línea', 'Sublínea', 'Característica']
indice_default_linea = categorias.index('Línea')  # Encuentra el índice de "Línea" en la lista actualizada

# Usar st.columns para ajustar el ancho del selector de proyectos
col_selector_der, _ = st.columns([3, 7])  # Ajusta según necesidad para el ancho del selector
categoria_derecha = col_selector_der.selectbox(
    "Selecciona la categoría para visualizar en Proyectos:",
    categorias,
    index=indice_default_linea,  # Usa el índice de "Línea" como valor predeterminado
    key='selector_derecha'  # Clave única para este selector
)

df_proyectos_categoria = contar_proyectos_por_categoria(df_filtrado, categoria_derecha)
fig_derecha = px.pie(df_proyectos_categoria, names=categoria_derecha, values='Num_Proyectos', title=f'Número de Proyectos por {categoria_derecha}',
                     color_discrete_sequence=px.colors.sequential.Sunsetdark)
fig_derecha.update_traces(textinfo='value+percent')
st.plotly_chart(fig_derecha)

st.markdown("""---""")


st.markdown("<h4 style='text-align: center; color: grey;'>Investigadores por categoría</h4>", unsafe_allow_html=True)

# Actualizar la lista de categorías y usar un diccionario para mapear los nombres mostrados en el selector
categorias = ['Area', 'Condición', 'Sexo', 'Título de Grado', 'Título Posgrado']
categorias_mostradas = {
    'Area': 'Area',
    'Condición': 'Condición',
    'Sexo': 'Género',  # Cambiar la etiqueta de 'Sexo' a 'Género'
    'Título de Grado': 'Título de Grado',
    'Título Posgrado': 'Título Posgrado'
}

# Usar st.columns para ajustar el ancho del selector
col_selector_izq, _ = st.columns([3, 7])  # Ajusta según necesidad para el ancho del selector
categoria_izquierda = col_selector_izq.selectbox(
    "Selecciona la categoría para visualizar en Investigadores:",
    options=list(categorias_mostradas.values()),  # Mostrar los nombres modificados en el selector
    index=1,  # Establece 'Condición' (o el segundo elemento en la lista actualizada) como la opción predeterminada
    key='selector_izquierda'  # Clave única para este selector
)

# Convertir la selección de vuelta a la clave original si es necesario
categoria_seleccionada = [clave for clave, valor in categorias_mostradas.items() if valor == categoria_izquierda][0]

df_personas_categoria = contar_personas_por_categoria(df_filtrado, categoria_seleccionada)
fig_izquierda = px.pie(df_personas_categoria, names=categoria_seleccionada, values='Num_Personas', title=f'Número de Investigadores por {categoria_izquierda}',
                       color_discrete_sequence=px.colors.sequential.Sunsetdark)
fig_izquierda.update_traces(textinfo='value+percent')
st.plotly_chart(fig_izquierda)

st.markdown("""---""")








