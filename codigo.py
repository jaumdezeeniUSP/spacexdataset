import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})
    dataframes = []

    for table in tables:
        data_rows = []
        for row in table.find_all('tr'):
            columns = row.find_all(['th', 'td'])
            if columns:
                data = [column.get_text(strip=True) for column in columns]
                data_rows.append(data)
        df = pd.DataFrame(data_rows[1:], columns=data_rows[0])
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)

urls = [
    'https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches_(2010%E2%80%932019)',
    'https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches_(2020%E2%80%932021)',
    'https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches#cite_note-698'
]

dfs = [extract_data(url) for url in urls]
df = pd.concat(dfs, ignore_index=True)


df['Flight No.'] = df['Flight No.'].astype(str)

def extract_text(row):
    if not row['Flight No.'].isdigit():
        return row['Flight No.']

df['Description'] = df.apply(extract_text, axis=1).shift(-1)
df.reset_index(drop=True, inplace=True)

dfF9 = df[pd.to_numeric(df['Flight No.'], errors='coerce').notna()]
tkout = ['FlightNo.', 'Date and time (UTC)']
dfF9 = dfF9.drop(columns=tkout)
def remover_numeros(texto):
    if isinstance(texto, str):
        return re.sub(r'\[\d+\]', '', texto)
    else:
        return texto
dfF9 = dfF9.applymap(remover_numeros)
dfF9.reset_index(drop=True, inplace=True)
dfF9.to_csv('falcon9launches.csv', index=False)