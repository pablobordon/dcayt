
import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile


#configurar página
st.set_page_config(page_title="Presentación", page_icon="", layout="wide")

st.markdown("<h2 style='text-align: center; color: grey;'>DCAyT - Investigadores y Proyectos - Período 2020-2024 </h1>", unsafe_allow_html=True)


st.markdown("""---""")
st.markdown("<h5 style='text-align: center; color: grey;'>Navegar panel lateral</h5>", unsafe_allow_html=True)

st.markdown("<h5 style='text-align: center; color: grey;'>En Redes se ilustra la interconexión entre investigadores y proyectos del departamentor.</h5>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: grey;'>En Datos se da cuenta del estado de situación de proyectos e investigadores.</h5>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: grey;'>En Mapas visualizar información relacionada tanto con proyectos como con investigadores.</h5>", unsafe_allow_html=True)




