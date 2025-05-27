import os
import pandas as pd
from langchain_core.tools import tool
from settings import INPUT_DIR, OUTPUT_DIR
from builder import AgentState

@tool
def load_excel(state: AgentState, filename: str) -> AgentState:
    """reads an excel file"""

    path = os.path.join(INPUT_DIR, filename)
    df = pd.read_excel(path)

    new_state = state.copy()
    new_state["loaded_files"][filename] = path
    new_state["current_df_key"] = filename
    new_state["available_columns"][filename] = df.columns.to_list()
    new_state["temp_results"] = {filename: df}
    new_state["last_operation"] = f"Loaded {filename}"

    return state


@tool
def add_two_columns(
    state: AgentState, col_a: str, col_b: str, new_col_name: str
) -> AgentState:
    current_key = state.get("current_df_key")
    if not current_key:
        raise ValueError("No active spreadsheet.")

    df = state["temp_results"].get(current_key)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")

    # Faz a modificação no próprio DataFrame
    df[new_col_name] = df[col_a] + df[col_b]

    # Atualiza colunas disponíveis
    new_state = state.copy()
    new_state["available_columns"][current_key] = df.columns.tolist()
    new_state["last_operation"] = f"Added column '{new_col_name}' to '{current_key}'"

    return new_state


@tool
def save_excel(state: AgentState) -> AgentState:
    """saves the dataframe into an excel with the specified filename"""

    current_key = state.get("current_df_key")
    if not current_key:
        raise ValueError("No active spreadsheet.")

    df = state["temp_results"].get(current_key)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")
    
    



    df = dataframes.get(filename)
    if df is None:
        raise ValueError("Spreadsheet not loaded.")
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_excel(path, index=False)

    return new_state

