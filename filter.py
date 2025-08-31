import sys

def filter_by_surname():
    """
    Filters the parsed data based on a list of Latino surnames.
    """
    try:
        with open('surnames.txt', 'r', encoding='iso-8859-1') as f:
            # Store surnames in a set for efficient O(1) average time complexity lookups
            latino_surnames = {line.strip().upper() for line in f}
    except FileNotFoundError:
        sys.stderr.write("Error: No se encontró el archivo surnames.txt.\n")
        sys.exit(1)

    try:
        with open('parsed_data.csv', 'r', encoding='iso-8859-1') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Data is in format: url,entry_num,date,name
                    parts = line.split(',')
                    name_field = parts[3]

                    # The name format is "LASTNAME; FIRSTNAME..." or just a company name
                    # We take the first part of the name before any special characters
                    # And then take the first word of that as the primary surname.
                    surname = name_field.split(';')[0].split(' ')[0].strip().upper()

                    if surname in latino_surnames:
                        print(line)

                except IndexError:
                    # Skip any line that doesn't have enough columns
                    # sys.stderr.write(f"Skipping malformed line: {line}\n")
                    continue
    except FileNotFoundError:
        sys.stderr.write("Error: No se encontró el archivo parsed_data.csv.\n")
        sys.exit(1)

if __name__ == "__main__":
    filter_by_surname()
