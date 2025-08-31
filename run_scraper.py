import re
import sys
import subprocess
import argparse
import time
import os

BASE_URL = "https://www.utahcounty.gov/LandRecords/"
SURNAMES_FILE = "surnames.txt"

def load_surnames():
    """Loads surnames from the specified file into a set for efficient lookup."""
    if not os.path.exists(SURNAMES_FILE):
        sys.stderr.write(f"Error: El archivo de apellidos '{SURNAMES_FILE}' no fue encontrado.\n")
        sys.exit(1)
    with open(SURNAMES_FILE, 'r', encoding='iso-8859-1') as f:
        return {line.strip().upper() for line in f if line.strip()}

def fetch_page(url):
    """Fetches the HTML content of a given URL using curl."""
    try:
        result = subprocess.run(
            ['curl', '-A', 'Mozilla/5.0', '-sL', url],
            capture_output=True, text=True, encoding='iso-8859-1',
            check=True, timeout=20
        )
        return result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        sys.stderr.write(f"Advertencia: No se pudo descargar la página {url}. Error: {e}\n")
        return None

def parse_results_page(html):
    """Parses the HTML of a search results page to extract individual records."""
    pattern = re.compile(
        r'<tr>\s*<td[^>]*>WD</td>\s*<td><a href="([^"]+)">([^<]+)</a></td>\s*<td>\d+</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>.*?</tr>',
        re.DOTALL
    )
    matches = pattern.findall(html)
    records = []
    for match in matches:
        records.append({
            "url": f"{BASE_URL}{match[0].strip()}",
            "entry_num": match[1].strip(),
            "date": match[2].strip(),
            "name": match[3].strip().replace(',', ';')
        })
    return records

def get_tax_address(html):
    """Parses the HTML of a detail page to extract the tax address."""
    pattern = re.compile(r'Tax Address:.*?</td>\s*<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
    match = pattern.search(html)
    if match:
        address_blob = match.group(1)
        cleaned_address = re.sub(r'<[^>]+>', ' ', address_blob)
        final_address = ' '.join(cleaned_address.strip().split())
        return final_address
    return "Address Not Found"

def main(pages_to_scrape, output_file):
    """Main function to orchestrate the scraping process."""
    surnames = load_surnames()

    # Check if file exists to decide whether to write header
    file_exists = os.path.exists(output_file)

    with open(output_file, 'a', encoding='utf-8') as f:
        if not file_exists:
            f.write("url,entry_number,date,name,tax_address\n")

        for page_num in range(pages_to_scrape):
            offset = page_num * 100
            search_url = f"{BASE_URL}DocKoi.asp?avKoi=WD&offset={offset}"

            print(f"Procesando página {page_num + 1} (offset={offset})...")

            results_html = fetch_page(search_url)
            if not results_html:
                continue

            records = parse_results_page(results_html)
            if not records:
                print("No se encontraron más registros. Terminando.")
                break

            for record in records:
                surname = record["name"].split(';')[0].split(' ')[0].strip().upper()
                if surname in surnames:
                    print(f"  Coincidencia encontrada: {record['name']}. Obteniendo dirección...")
                    address_html = fetch_page(record['url'])
                    if address_html:
                        address = get_tax_address(address_html)
                        f.write(f"\"{record['url']}\",\"{record['entry_num']}\",\"{record['date']}\",\"{record['name']}\",\"{address}\"\n")
                        f.flush() # Write to disk immediately

            # Be a good web citizen
            time.sleep(1)

    print(f"\nProceso completado. Los datos han sido guardados en '{output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper de Registros de Propiedad del Condado de Utah.")
    parser.add_argument('-p', '--pages', type=int, default=1, help="Número de páginas de resultados a procesar.")
    parser.add_argument('-o', '--output', type=str, default="propietarios_latinos.csv", help="Nombre del archivo CSV de salida.")
    args = parser.parse_args()

    main(args.pages, args.output)
