import re
import sys
import subprocess
import argparse
import time
import os
import csv

BASE_URL = "https://www.utahcounty.gov/LandRecords/"
SURNAMES_FILE = "surnames.txt"
STREET_SUFFIXES = {'WAY', 'ST', 'STR', 'AVE', 'BLVD', 'RD', 'DR', 'LN', 'PL', 'CIR', 'CT', 'LOOP', 'HWY', 'PIKE', 'RUN', 'PARK'}
# Patterns to remove from names for de-duplication
NAME_NOISE = [
    re.compile(r'\s+\(ET AL\)$', re.IGNORECASE),
    re.compile(r'\s+TEE$', re.IGNORECASE),
    re.compile(r'\s+SUCTEE$', re.IGNORECASE)
]

def normalize_name(name):
    """Removes common suffixes from a name string for better de-duplication."""
    normalized = name
    for pattern in NAME_NOISE:
        normalized = pattern.sub('', normalized)
    return normalized.strip()

def load_surnames():
    """Loads surnames from the specified file into a set."""
    if not os.path.exists(SURNAMES_FILE):
        sys.stderr.write(f"Error: El archivo de apellidos '{SURNAMES_FILE}' no fue encontrado.\n")
        sys.exit(1)
    with open(SURNAMES_FILE, 'r', encoding='iso-8859-1') as f:
        return {line.strip().upper() for line in f if line.strip()}

def load_existing_records(filename):
    """Reads an existing CSV file and returns a set of unique keys (normalized_name, street) to prevent duplicates."""
    existing_records = set()
    if not os.path.exists(filename):
        return existing_records

    print(f"Leyendo registros existentes de '{filename}' para evitar duplicados...")
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            name_idx = header.index('name')
            street_idx = header.index('street')
        except (StopIteration, ValueError):
            return existing_records

        for row in reader:
            if len(row) > max(name_idx, street_idx):
                name = row[name_idx]
                street = row[street_idx]
                normalized_name = normalize_name(name)
                existing_records.add((normalized_name, street))
    print(f"Se cargaron {len(existing_records)} registros existentes.")
    return existing_records

def fetch_page(url):
    """Fetches the HTML content of a given URL using curl."""
    try:
        result = subprocess.run(
            ['curl', '-A', 'Mozilla/5.0', '-sL', url],
            capture_output=True, text=True, encoding='iso-8859-1', check=True, timeout=20
        )
        return result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        sys.stderr.write(f"Advertencia: No se pudo descargar la página {url}. Error: {e}\n")
        return None

def parse_results_page(html):
    """Parses the HTML of a search results page to extract individual records."""
    pattern = re.compile(
        r'<tr>\s*<td[^>]*>WD</td>\s*<td><a href="([^"]+)">([^<]+)</a></td>\s*<td>\d+</td>\s*<td>([^<]+)</td>\s*<td>.*?</td>\s*<td>(.*?)</td>\s*</tr>',
        re.DOTALL
    )
    matches = pattern.findall(html)
    records = []
    for match in matches:
        grantee_name = match[3].strip().replace(',', ';')
        if not grantee_name or grantee_name == '&nbsp;':
            continue
        records.append({
            "url": f"{BASE_URL}{match[0].strip()}", "entry_num": match[1].strip(),
            "date": match[2].strip(), "name": grantee_name
        })
    return records

def get_and_parse_address(html):
    """Parses the HTML of a detail page to extract and programmatically split the tax address."""
    address_parts = {"street": "Not Found", "city": "Not Found", "state": "Not Found", "zip": "Not Found"}
    pattern_full = re.compile(r'Tax Address:.*?</td>\s*<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
    match_full = pattern_full.search(html)
    if not match_full: return address_parts
    address_blob = match_full.group(1)
    cleaned_address = ' '.join(re.sub(r'<[^>]+>', ' ', address_blob).strip().split())
    parts = cleaned_address.rsplit(',', 1)
    if len(parts) != 2:
        address_parts['street'] = cleaned_address
        return address_parts
    street_and_city_str = parts[0].strip()
    state_and_zip_str = parts[1].strip()
    state_zip_match = re.search(r'^([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$', state_and_zip_str)
    if state_zip_match:
        address_parts['state'] = state_zip_match.group(1)
        address_parts['zip'] = state_zip_match.group(2)
    words = street_and_city_str.split(' ')
    city_words = []
    for i in range(len(words) - 1, -1, -1):
        word = words[i]
        if word.isupper() and word not in STREET_SUFFIXES and len(word) > 1:
            city_words.insert(0, word)
        else:
            address_parts['street'] = ' '.join(words[0:i+1])
            break
    address_parts['city'] = ' '.join(city_words) if city_words else 'Not Found'
    if not address_parts['street'] and not city_words:
        address_parts['street'] = street_and_city_str
    return address_parts

def main(pages_limit, output_file):
    try:
        surnames = load_surnames()
        existing_records = load_existing_records(output_file)
        with open(output_file, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if not existing_records: # Write header only if the file is new/empty
                writer.writerow(["url", "entry_number", "date", "name", "street", "city", "state", "zip"])
            page_num = 0
            while True:
                if pages_limit is not None and page_num >= pages_limit:
                    print(f"Límite de {pages_limit} páginas alcanzado. Terminando.")
                    break
                offset = page_num * 100
                search_url = f"{BASE_URL}DocKoi.asp?avKoi=WD&offset={offset}"
                print(f"Procesando página {page_num + 1} (offset={offset})... (Presiona Ctrl+C para detener)")
                results_html = fetch_page(search_url)
                if not results_html:
                    page_num += 1; time.sleep(2); continue
                records = parse_results_page(results_html)
                if not records:
                    print("No se encontraron más registros. Terminando."); break
                for record in records:
                    surname = record["name"].split(';')[0].split(' ')[0].strip().upper()
                    if surname in surnames:
                        print(f"  Coincidencia encontrada: {record['name']}.")
                        address_html = fetch_page(record['url'])
                        if address_html:
                            address = get_and_parse_address(address_html)
                            normalized_name = normalize_name(record['name'])
                            record_key = (normalized_name, address['street'])
                            if record_key in existing_records:
                                print(f"    -> Duplicado encontrado (nombre normalizado). Omitiendo.")
                                continue
                            writer.writerow([
                                record['url'], record['entry_num'], record['date'], record['name'],
                                address['street'], address['city'], address['state'], address['zip']
                            ])
                            f.flush()
                            existing_records.add(record_key)
                page_num += 1
                time.sleep(1)
        print(f"\nProceso completado. Los datos han sido guardados en '{output_file}'.")
    except KeyboardInterrupt:
        print("\n\nProceso detenido por el usuario. Saliendo de forma segura.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper de Registros de Propiedad del Condado de Utah.")
    parser.add_argument('-p', '--pages', type=int, default=None, help="Límite opcional de páginas a procesar. Por defecto, procesa todas.")
    parser.add_argument('-o', '--output', type=str, default="propietarios_latinos.csv", help="Nombre del archivo CSV de salida.")
    args = parser.parse_args()
    main(args.pages, args.output)
