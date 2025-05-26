import os
import pandas as pd
from langchain_core.tools import tool
from settings import INPUT_DIR, OUTPUT_DIR
from dataframe_cache import dataframes


@tool
def load_excel(filename: str) -> str:
    """reads an excel file"""

    path = os.path.join(INPUT_DIR, filename)
    df = pd.read_excel(path)
    dataframes[filename] = df
    return f"File '{filename}' loaded successfully."


@tool
def get_columns(filename: str) -> list:
    """gets the names of the columns of a dataframe"""

    df = dataframes.get(filename)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")
    return df.columns.tolist()


@tool
def add_two_columns(filename: str, col_a: str, col_b: str, new_col_name: str) -> str:
    '''adds the values of two columns and create a new with the values'''

    df = dataframes.get(filename)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")

    df[new_col_name] = df[col_a] + df[col_b]

    new_filename = filename.replace(".xlsx", f"_with_{new_col_name}.xlsx")
    df.to_excel(new_filename, index=False)

    return f"New column '{new_col_name}' added and saved to '{new_filename}'."


@tool
def save_excel(filename: str) -> str:
    """saves the dataframe into an excel with the specified filename"""

    df = dataframes.get(filename)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_excel(path, index=False)

    return f"File saved successfully to '{filename}'."

