import re
import sys
import subprocess

def get_address(url):
    """
    Fetches the content from a URL using curl and extracts the tax address.
    """
    try:
        result = subprocess.run(
            ['curl', '-A', 'Mozilla/5.0', '-sL', url],
            capture_output=True,
            text=True,
            encoding='iso-8859-1',
            check=True,
            timeout=15
        )
        html_content = result.stdout

        # This regex finds the <td> containing "Tax Address:", then captures
        # the content of the *next* <td>. This is the correct structure.
        pattern = re.compile(r'Tax Address:.*?</td>\s*<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)
        match = pattern.search(html_content)

        if match:
            # The captured group contains the address, potentially with <br> tags and whitespace.
            address_blob = match.group(1)
            # Replace any HTML tags (like <br>) with a space.
            cleaned_address = re.sub(r'<[^>]+>', ' ', address_blob)
            # Consolidate all whitespace (newlines, tabs, etc.) into single spaces and trim.
            final_address = ' '.join(cleaned_address.strip().split())
            # Return as a properly quoted CSV field.
            return f'"{final_address}"'
        else:
            return '"Address Not Found"'

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        # Return a meaningful error if curl fails or times out.
        error_message = str(e).replace('"', "'") # Sanitize error message for CSV
        return f'"Error fetching address: {error_message}"'

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 get_address.py <url>\n")
        sys.exit(1)

    print(get_address(sys.argv[1]))
