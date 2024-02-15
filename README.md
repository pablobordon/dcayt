# DCAyT - Investigadores y Proyectos - Período 2022-2024

## Descripción
Este proyecto está diseñado para ser una herramienta útil, principalmente para directores de centros y programas de investigación del Departamento de Ciencias Aplicadas de la Universidad Nacional de Moreno. Asimismo, permite que investigadores y estudiantes involucrados en los proyectos accedan y hagan seguimiento de información relevante de manera eficiente. El objetivo es crear visualizaciones interactivas que faciliten la navegación por la información sin necesidad de consultar directamente a la base de datos accesible a través del [buscador de proyectos](http://www.unm.edu.ar/index.php/investigacion/buscador-de-proyectos).


## Estructura del Proyecto
Archivos organizados de la siguiente manera:
- `Principal.py`: Módulo principal que ejecuta la aplicación.
- `1_Redes.py`: Gestiona la visualización de redes de investigadores y proyectos.
- `2_Zonas.py`: Facilita la visualización geográfica de zonas relacionadas con los proyectos.
- `3_Datos.py`: Administra la carga y manipulación de datos del proyecto.
- Carpeta datos: Personas.xslx; Proyectos.xlsx; Participa.xlsx. Respetar formato al replicar.
  
## Instalación
Este proyecto puede ser replicado por otros departamentos académicos de la Universidad. Para instalar y ejecutar este proyecto localmente, sigue los siguientes pasos:

1. **Instalar Python**: Asegúrate de tener Python instalado en tu sistema. Si aún no lo tienes, puedes descargarlo desde [python.org](https://python.org).

2. **Clonar el repositorio**: Copia el repositorio en tu máquina local usando el siguiente comando en tu terminal o línea de comandos:
git clone [URL_DEL_REPOSITORIO](https://github.com/pablobordon/dcayt.git)

Esto creará una copia local del proyecto en tu sistema.

3. **Crear un entorno virtual**: Navega al directorio del proyecto clonado y ejecuta el siguiente comando para crear un entorno virtual. Esto te permite instalar y manejar las dependencias del proyecto de manera aislada.

python -m venv venv

Esto creará un nuevo directorio `venv` dentro de tu proyecto, donde se almacenarán las dependencias.

4. **Activar el entorno virtual**: Antes de instalar las dependencias, activa el entorno virtual con el siguiente comando:
- En Windows:
  ```
  venv\Scripts\activate
  ```
- En macOS y Linux:
  ```
  source venv/bin/activate
  ```
Notarás que el prompt de tu terminal cambia para reflejar que el entorno virtual está activo.

5. **Instalar dependencias**: Con el entorno virtual activo, instala las dependencias del proyecto ejecutando:
pip install -r requirements.txt

Asegúrate de que el archivo `requirements.txt` esté presente en el directorio del proyecto y contenga todas las bibliotecas necesarias.

## Uso
Para ejecutar la aplicación, asegúrate de que tu entorno virtual esté activo y luego navega al directorio del proyecto. Ejecuta el siguiente comando:

streamlit run Principal.py

