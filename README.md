# Scraper de Registros de Propiedad del Condado de Utah

Este proyecto contiene un script para extraer información sobre nuevos propietarios con apellidos latinos del sitio web de Registros de la Propiedad del Condado de Utah.

El script está diseñado para ser robusto, incluyendo las siguientes características:
- **Anti-duplicación:** Lee el archivo de resultados existente antes de empezar, para evitar añadir registros que ya han sido guardados en ejecuciones anteriores.
- **Paginación automática:** Procesa todas las páginas de resultados hasta que no encuentra más.
- **Salida elegante:** Permite detener el script de forma segura con `Ctrl+C`.

## Archivos del Proyecto

-   `run_scraper.py`: El script principal y único que necesitas ejecutar. Automatiza todo el proceso de scraping.
-   `surnames.txt`: La lista de apellidos latinos utilizada para filtrar los resultados. Puedes editar este archivo para añadir o quitar apellidos.
-   `propietarios_latinos.csv`: El archivo CSV con los datos finales extraídos. Este archivo es generado (o actualizado) por `run_scraper.py`.

## Cómo Usar el Scraper

El uso del script es muy sencillo. Abre una terminal y ejecuta el siguiente comando para procesar **todas** las páginas de resultados hasta que no se encuentren más:

```bash
python3 run_scraper.py
```

El script mostrará el progreso en la terminal y guardará (o añadirá) los resultados encontrados en el archivo de salida, omitiendo cualquier duplicado.

### Argumentos Opcionales

-   `--pages N`: Limita el número de páginas a procesar a `N`. Es útil para hacer pruebas rápidas sin recorrer todo el sitio.
-   `--output <nombre_archivo.csv>`: Especifica un nombre diferente para el archivo de salida. Por defecto, es `propietarios_latinos.csv`.

### Ejemplos de Uso

**Procesar únicamente las 5 primeras páginas:**
```bash
python3 run_scraper.py --pages 5
```

**Procesar todas las páginas y guardar los resultados en `reporte_completo.csv`:**
```bash
python3 run_scraper.py --output reporte_completo.csv
```

## Formato del Archivo de Salida

El archivo CSV de salida tendrá las siguientes columnas:

-   `url`: El enlace directo a la página de detalles del registro.
-   `entry_number`: El número de entrada del registro.
-   `date`: La fecha de registro.
-   `name`: El nombre de la Parte 1.
-   `street`: La dirección de la calle.
-   `city`: La ciudad.
-   `state`: El estado (ej. UT).
-   `zip`: El código postal.

## Configuración

### Modificar la lista de apellidos

Para cambiar los apellidos que el script busca, simplemente edita el archivo `surnames.txt` con un editor de texto. Añade o elimina apellidos, asegurándote de que haya uno por línea. El script no distingue entre mayúsculas y minúsculas.
