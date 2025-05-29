import pandas as pd
from langchain.tools import tool
from settings import INPUT_DIR, OUTPUT_DIR
from typing_extensions import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_groq import ChatGroq

dataframes = {"result": pd.DataFrame()}

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def build_agent(tools) -> ChatGroq:
    agent = ChatGroq(
        model='llama3-70b-8192',
        temperature=0
    ).bind_tools(tools)

    return agent

# em vez de ler o excel, apenas pegar os listados nos dataframes

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
def remove_columns(target_filename: str, columns_to_remove: List['str']):

    """function that removes columns from target files"""

    if target_filename not in dataframes:
        return f"There is no '{target_filename}' file."

    dataframes[target_filename] = dataframes[target_filename].drop(columns=columns_to_remove, errors="ignore")

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
def copy_to_result(source_filename: str) -> str:
    """
    Copies a DataFrame from memory to the final result file.

    Arguments:
    - source_filename: The name of the DataFrame (already loaded in memory) to be copied.

    This tool is used to mark a DataFrame as the final result by copying it 
    to a special key called 'result_file'. This is useful when a specific 
    intermediate file needs to be designated as the output after a series 
    of transformations or merges.

    Returns a confirmation message upon success.
    """

    dataframes["result"] = dataframes[source_filename]

    return f"{source_filename} copied to result successfully."


formatter_tools = [sheet_overview, remove_columns]
merger_tools = [sheet_overview, merge_files, copy_to_result]