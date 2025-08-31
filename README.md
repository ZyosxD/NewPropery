# Scraper de Registros de Propiedad del Condado de Utah

Este proyecto contiene un conjunto de scripts para extraer información sobre nuevos propietarios con apellidos latinos del sitio web de Registros de la Propiedad del Condado de Utah.

## Archivos del Proyecto

-   `propietarios_latinos.csv`: El archivo CSV con los datos finales extraídos. Por defecto, contiene los resultados encontrados en la primera página de búsqueda.
-   `surnames.txt`: La lista de apellidos latinos utilizada para filtrar los resultados. Puedes editar este archivo para añadir o quitar apellidos.
-   `parser.py`: Script de Python que analiza una página de resultados de búsqueda (guardada como archivo HTML) y extrae los datos de cada registro.
-   `filter.py`: Script de Python que filtra los datos generados por `parser.py` basándose en la lista de `surnames.txt`.
-   `get_address.py`: Script de Python que toma una URL de una página de detalles y extrae la dirección fiscal ("Tax Address").
-   `extract_surnames.py`: (Opcional) Un script de ayuda para extraer listas de apellidos de una página HTML de `familyeducation.com` que hayas guardado previamente.

## Cómo Usar los Scripts

Para ejecutar el proceso y obtener los datos de una nueva página de resultados, sigue estos pasos en una terminal de línea de comandos (como bash en Linux o macOS).

### Paso 1: Descargar una página de resultados

Primero, necesitas descargar el código HTML de la página de resultados que quieres analizar. Puedes hacerlo usando una herramienta como `curl`. El parámetro `offset` en la URL determina la página: `offset=0` es la primera página, `offset=100` es la segunda, y así sucesivamente.

**Ejemplo para descargar la tercera página de resultados (offset=200):**
```bash
curl -A "Mozilla/5.0" -sL "https://www.utahcounty.gov/LandRecords/DocKoi.asp?avKoi=WD&offset=200" -o results_page_3.txt
```

### Paso 2: Ejecutar el proceso de scraping

Una vez que tienes el archivo HTML (p. ej., `results_page_3.txt`), puedes ejecutar la secuencia de scripts para procesarlo. El siguiente comando buscará coincidencias en el archivo y las **añadirá** al final de `propietarios_latinos.csv`.

```bash
# Define el nombre del archivo HTML que descargaste
INPUT_FILE="results_page_3.txt"

# 1. Analiza el archivo HTML y crea un CSV temporal con los datos de esa página
python3 parser.py $INPUT_FILE > parsed_data.csv

# 2. Filtra esos datos por apellido y crea otro CSV temporal
python3 filter.py > filtered_data.csv

# 3. Recorre los nuevos resultados filtrados, obtiene la dirección y añade la línea completa al archivo final
while IFS=, read -r url rest_of_line; do
  address=$(python3 get_address.py "$url")
  echo "$url,$rest_of_line,$address" >> propietarios_latinos.csv
done < filtered_data.csv

echo "Proceso completado para $INPUT_FILE. Los nuevos datos se han añadido a propietarios_latinos.csv."
```

### Paso 3: Ver los resultados

Abre el archivo `propietarios_latinos.csv` con cualquier programa de hoja de cálculo (como Excel, Google Sheets o LibreOffice Calc) para ver los resultados.

## Configuración

### Modificar la lista de apellidos

Para cambiar los apellidos que se buscan, simplemente edita el archivo `surnames.txt` con un editor de texto. Añade o elimina apellidos, asegurándote de que haya uno por línea. El script de filtrado no distingue entre mayúsculas y minúsculas.
