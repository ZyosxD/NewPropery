import re
import sys

def extract_surnames(filename):
    """
    Parses an HTML file from familyeducation.com and extracts the surnames.
    """
    try:
        with open(filename, 'r', encoding='iso-8859-1') as f:
            content = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: {filename} not found.\n")
        sys.exit(1)

    # The relevant surnames are in links within a div with class 'view-content'
    # This regex is specific to the structure of that page
    # e.g., <a href="/baby-names/name-meaning/amores">Amores</a>
    pattern = re.compile(r'<a href="/baby-names/name-meaning/[^"]+">([^<]+)</a>')

    matches = pattern.findall(content)

    # A set to avoid printing duplicate names from a single page
    found_names = set()
    for name in matches:
        # The names we want are single words, usually capitalized.
        # This check avoids extracting other navigation links.
        if ' ' not in name and len(name) > 1:
            found_names.add(name.strip())

    for name in sorted(list(found_names)):
        print(name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python3 extract_surnames.py <html_file>\n")
        sys.exit(1)
    extract_surnames(sys.argv[1])
