# Scraper de Registros de Propiedad del Condado de Utah

Este proyecto contiene un script para extraer información sobre nuevos propietarios con apellidos latinos del sitio web de Registros de la Propiedad del Condado de Utah.

## Archivos del Proyecto

-   `run_scraper.py`: El script principal y único que necesitas ejecutar. Automatiza todo el proceso de scraping.
-   `surnames.txt`: La lista de apellidos latinos utilizada para filtrar los resultados. Puedes editar este archivo para añadir o quitar apellidos.
-   `propietarios_latinos.csv`: El archivo CSV con los datos finales extraídos. Este archivo es generado (o actualizado) por `run_scraper.py`.

## Cómo Usar el Scraper

El uso del script es muy sencillo. Abre una terminal y ejecuta el siguiente comando:

```bash
python3 run_scraper.py --pages N
```
...donde `N` es el número de páginas de resultados que quieres procesar.

El script mostrará el progreso en la terminal y guardará (o añadirá) los resultados encontrados en el archivo `propietarios_latinos.csv`.

### Argumentos del Script

-   `--pages N`: (Opcional) Especifica el número `N` de páginas de resultados a procesar. **Por defecto, si no se especifica, procesará 1 página.**
-   `--output <nombre_archivo.csv>`: (Opcional) Especifica un nombre diferente para el archivo de salida. Por defecto, es `propietarios_latinos.csv`.

### Ejemplos de Uso

**Procesar las 5 primeras páginas:**
```bash
python3 run_scraper.py --pages 5
```

**Procesar 20 páginas y guardar los resultados en `reporte_completo.csv`:**
```bash
python3 run_scraper.py --pages 20 --output reporte_completo.csv
```

## Configuración

### Modificar la lista de apellidos

Para cambiar los apellidos que el script busca, simplemente edita el archivo `surnames.txt` con un editor de texto. Añade o elimina apellidos, asegurándote de que haya uno por línea. El script no distingue entre mayúsculas y minúsculas.
