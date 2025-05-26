import pandas as pd
from langchain_core.tools import tool
from core.dataframe_cache import dataframes

@tool
def open_excel(path: str) -> str:
    """reads an excel file"""

    df = pd.read_excel(path)
    dataframes[path] = df
    return f"File '{path}' loaded successfully."

@tool
def get_columns(path: str) -> list:
    """gets the names of the columns of a dataframe"""

    df = dataframes.get(path)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")
    return df.columns.tolist()


@tool
def add_two_columns(path: str, col_a: str, col_b: str, new_col_name: str) -> str:
    '''adds the values of two columns and create a new'''

    df = dataframes.get(path)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")

    df[new_col_name] = df[col_a] + df[col_b]

    new_path = path.replace(".xlsx", f"_with_{new_col_name}.xlsx")
    df.to_excel(new_path, index=False)

    return f"New column '{new_col_name}' added and saved to '{new_path}'."


@tool
def save_excel(path: str) -> str:
    df = dataframes.get(path)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")
    df.to_excel(path, index=False)

    return f"File saved successfully to '{path}'."