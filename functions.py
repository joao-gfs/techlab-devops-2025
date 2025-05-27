import pandas as pd
import os
from settings import INPUT_DIR
from pprint import pprint

filename = 'Dados Colaboradores.xlsx'
path = os.path.join(INPUT_DIR, filename)
df = pd.read_excel(path)

df.set_index('Nome', inplace=True)

pprint(df.to_dict())


def convert_df(df: pd.DataFrame, index: str) -> dict:
    df.set_index(index, imn)