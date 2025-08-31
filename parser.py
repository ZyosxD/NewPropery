import re
import sys

def parse_results(filename):
    """
    Reads a saved HTML results page, parses the data table,
    and prints the extracted information in CSV format.
    """
    try:
        with open(filename, 'r', encoding='iso-8859-1') as f:
            html_content = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: El archivo '{filename}' no fue encontrado.\n")
        sys.exit(1)

    # Regex to find table rows and capture data fields.
    pattern = re.compile(
        r'<tr>\s*'
        r'<td[^>]*>WD</td>\s*'
        r'<td><a href="([^"]+)">([^<]+)</a></td>\s*'
        r'<td>\d+</td>\s*'
        r'<td>([^<]+)</td>\s*'
        r'<td>([^<]+)</td>\s*'
        r'.*?'
        r'</tr>',
        re.DOTALL
    )

    matches = pattern.findall(html_content)

    for match in matches:
        url_part = match[0].strip()
        entry_num = match[1].strip()
        rec_date = match[2].strip()
        party1_name = match[3].strip().replace(',', ';')

        full_url = f"https://www.utahcounty.gov/LandRecords/{url_part}"

        print(f"{full_url},{entry_num},{rec_date},{party1_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 parser.py <html_filename>\n")
        sys.exit(1)
    parse_results(sys.argv[1])
