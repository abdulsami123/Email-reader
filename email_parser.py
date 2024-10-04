import re
import urllib.parse
from bs4 import BeautifulSoup

import re
import urllib.parse
from bs4 import BeautifulSoup

def extract_newsletter_links(email_content):
    # Parse the HTML content
    soup = BeautifulSoup(email_content, 'html.parser')

    # Pattern for TLDR newsletter tracking links
    pattern = r'https://tracking\.tldrnewsletter\.com/CL0/([^/]+)/\d+/[^/]+'
    
    # Excluded prefixes
    excluded_prefixes = ('https://tldr', 'https://advertise.tldr', 'https://links.tldr', 'https://a.tldr' , 'https://refer.tldr')
    
    # Find all links in the email
    all_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        match = re.match(pattern, href)
        if match:
            # Extract and decode the actual URL
            encoded_url = match.group(1)
            decoded_url = urllib.parse.unquote(encoded_url)
            
            # Check if the decoded URL starts with any of the excluded prefixes
            if not any(decoded_url.lower().startswith(prefix) for prefix in excluded_prefixes):
                all_links.append(decoded_url)
            # else:
            #     print(f"Excluded link: {decoded_url}")  # Debug print

    # Remove duplicates
    unique_links = list(set(all_links))
    
    #print(f"Total links found: {len(all_links)}")  # Debug print
    #print(f"Unique links after filtering: {len(unique_links)}")  # Debug print
    
    return unique_links






