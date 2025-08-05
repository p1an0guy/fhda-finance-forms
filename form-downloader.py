import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Target URL
BASE_URL = "https://business.fhda.edu/finance-forms/"
SAVE_DIR = "downloaded_forms"
os.makedirs(SAVE_DIR, exist_ok=True)

# Helper: clean link text to make a safe filename
def clean_filename(text):
    text = text.strip()
    text = re.sub(r'[\\/*?:"<>|]', "", text)  # Remove illegal filename chars
    text = re.sub(r'\s+', '_', text)          # Replace spaces with underscores
    return text[:100]                         # Limit filename length

# Fetch the page
response = requests.get(BASE_URL)
if response.status_code != 200:
    print("Failed to access the website.")
    exit()

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")
pdf_links = []
downloaded_files = []  # List to store names of successfully downloaded files

# Find all <a> tags with .pdf hrefs
for link in soup.find_all("a", href=True):
    href = link["href"]
    if href.lower().endswith(".pdf"):
        pdf_url = urljoin(BASE_URL, href)
        link_text = link.get_text(strip=True) or "document"

        # Clean and construct filename
        filename = clean_filename(link_text) + ".pdf"
        save_path = os.path.join(SAVE_DIR, filename)

        # Download the PDF
        print(f"Downloading: {filename}")
        try:
            pdf_response = requests.get(pdf_url)
            with open(save_path, "wb") as f:
                f.write(pdf_response.content)
            downloaded_files.append(filename)  # Add to list after successful download
        except Exception as e:
            print(f"Failed to download {pdf_url}: {e}")

print("✅ All PDFs downloaded with proper names.")
print(f"\nSuccessfully downloaded {len(downloaded_files)} files:")
for i, filename in enumerate(downloaded_files, 1):
    print(f"{i:2d}. {filename}")

print(f"\nList of downloaded files: {downloaded_files}")
