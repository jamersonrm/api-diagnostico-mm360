
import requests
from bs4 import BeautifulSoup

def extrair_bio_instagram(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if '"description"' in script.text:
                start = script.text.find('"description":') + len('"description":')
                end = script.text.find(',"url":')
                bio = script.text[start:end].strip().strip('"')
                return bio
        return None
    except Exception as e:
        return f"Erro: {e}"

# Exemplo de uso
# print(extrair_bio_instagram("https://www.instagram.com/seuperfil"))
