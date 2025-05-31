import pandas as pd
from typing_extensions import Annotated, Sequence, TypedDict, List
from langchain_core.tools import tool

# Cache dos dataframes manipulados
dataframes = {}

@tool
def sheet_overview(input_filename: str) -> str:
    """
    Extracts the column names from a Excel file and returns them.

    Arguments:
    - input_filename: The name of the file loaded into memory.

    Use this tool to inspect the structure of a file and understand what data it contains.
    """
    if input_filename not in dataframes:
        return f"File '{input_filename}' not loaded yet."

    df = dataframes[input_filename]

    return f"Columns: {df.columns.to_list()}. Sample data: {df.head(1).values.tolist()[0]}"

@tool
def remove_columns(target_filename: str, columns_to_remove: List[str]):

    """
        Removes the specified columns from the given spreadsheet.

        Parameters:
        - target_filename (str): The name of the spreadsheet (must already be loaded in memory).
        - columns_to_remove (List[str]): A list of column names to be removed from the file.
    """

    if target_filename not in dataframes:
        return f"There is no '{target_filename}' file."
    
    if columns_to_remove == []:
        return "No columns provided to remove"

    dataframes[target_filename] = dataframes[target_filename].drop(columns=columns_to_remove, errors='raise')

    return "Columns removed successfully"

@tool
def merge_files(left_df_name: str, right_df_name: str, left_on: List[str], right_on: List[str]) -> str:
    """
    Merges two DataFrames using multiple columns.

    Arguments:
    - left_df_name: The name of the left DataFrame (already loaded in memory).
    - right_df_name: The name of the right DataFrame (already loaded in memory).
    - left_on: A list of column names in the left DataFrame to merge on.
    - right_on: A list of column names in the right DataFrame to merge on.

    This tool supports merging on multiple columns. The 'left_on' and 'right_on' lists must have the same length, 
    and each pair of corresponding columns will be used as merge keys.

    The resulting merged DataFrame will replace the left one in memory.
    """

    if left_df_name not in dataframes:
        return f"Left file '{left_df_name}' is not loaded."
    if right_df_name not in dataframes:
        return f"Right file '{right_df_name}' is not loaded."

    df1 = dataframes[left_df_name]
    df2 = dataframes[right_df_name]

    if len(left_on) != len(right_on):
        return "The number of columns in 'left_on' and 'right_on' must match."

    merged_df = pd.merge(df1, df2, left_on=left_on, right_on=right_on, how='outer')

    dataframes[left_df_name] = merged_df

    return (
        f"Successful merge of '{left_df_name}' and '{right_df_name}' using columns "
        f"{left_on} and {right_on}."
    )

@tool
def rename_column(target_filename: str, current_column_name: str, new_name: str) -> str:
    """
    Rename 'current_column_name' to 'new_name' in the spreadsheet 'target_filename'.
    """
    dataframes[target_filename] = dataframes[target_filename].rename(columns={current_column_name: new_name})

    return "Renaming successful"

def add_columns(target_filename: str, columns_to_add: List[str]) -> str:
    """
    Sums the 'columns_to_sum' in the file 'target_filename'.
    """
    df = dataframes[target_filename]
    df["Total"] = df[columns_to_add].sum(axis=1)

    return f"Columns added sucessfully'."


identifier_tools = [sheet_overview]
eraser_tools = [sheet_overview, remove_columns]
renamer_tools = [rename_column]
merger_tools = [sheet_overview, merge_files]
adder_tools = [sheet_overview, add_columns]