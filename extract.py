import requests
from bs4 import BeautifulSoup
import pandas as pd

input_file = pd.read_excel('Input.xlsx')

for index, row in input_file.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paragraphs = soup.select('.td-pb-span8.td-main-content p')
        if paragraphs:
            article_text = ' '.join(paragraph.get_text() for paragraph in paragraphs)
        else:
            alt_paragraphs = soup.select('.tdb-block-inner p')
            if alt_paragraphs:
                article_text = ' '.join(paragraph.get_text() for paragraph in alt_paragraphs)
            else:
                print(f"No content found for URL_ID: {url_id}")
                continue
        
        with open(f'{url_id}.txt', 'w', encoding='utf-8') as file:
            file.write(article_text)
    else:
        print(f"Failed to fetch URL: {url}")

