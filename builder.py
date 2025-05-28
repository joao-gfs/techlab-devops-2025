import os
import pandas as pd
from langchain.tools import tool
from settings import INPUT_DIR, OUTPUT_DIR
from typing_extensions import Annotated, Sequence, TypedDict, List, Dict
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage

from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_groq import ChatGroq

dataframes = {}

# Agent Setting
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    temp_data: List[str]

def get_tools() -> List[tool]:
    return [load_excel, get_columns, save_excel, merge_files]

#llama3-8b-8192
#llama3-70b-8192
def build_agent() -> ChatGroq:
    tools = get_tools()

    agent = ChatGroq(
        model='llama3-70b-8192',
        temperature=0
    ).bind_tools(tools)

    return agent


# TOOLS
@tool
def load_excel(state: AgentState, input_filename: str) -> AgentState:
    """
    Loads an Excel file from disk into memory.

    Arguments:
    - input_filename: Name of the Excel file to load (must exist in the input folder).

    Use this tool before trying to inspect, modify, or export an Excel file.
    """
    path = os.path.join(INPUT_DIR, input_filename)
    try:
        df = pd.read_excel(path)
        dataframes[input_filename] = df
    except Exception as e:
        state["temp_data"].append(f"Faile to load file '{input_filename}': {e}")
    return state


@tool
def save_excel(filename: str, output_filename: str) -> str:
    """
    Saves an in-memory Excel file to disk.

    Arguments:
    - filename: The name of the file loaded into memory.
    - output_filename: The name of the Excel file to be saved on disk.

    Use this tool after processing or modifying a file, to export the result.
    """
    if filename not in dataframes:
        return f"Error: file '{filename}' not found in memory. Load it first using 'load_excel'."

    path = os.path.join(OUTPUT_DIR, output_filename)
    df = dataframes[filename]

    df.to_excel(path, index=False)

    return f"File saved successfully as '{output_filename}'"


@tool
def get_columns(state: AgentState, input_filename: str) -> AgentState:
    """
    Extracts the column names from a loaded Excel file and stores them in 'temp_data'.

    Arguments:
    - input_filename: The name of the file loaded into memory.

    Use this tool to inspect the structure of a file and understand what data it contains.
    """
    if input_filename not in dataframes:
        state["temp_data"].append(f"File '{input_filename}' not loaded yet.")
        return state

    df = dataframes[input_filename]
    state['temp_data'] = df.columns.to_list()

    return state

@tool
def merge_files(left_df_name: str, right_df_name: str, left_on: str, right_on: str) -> AgentState:
    """
    Merges two dataframes using specified columns.

    Arguments:
    - left_df_name: Name of left DataFrame.
    - right_df_name: Name of right DataFrame.
    - left_on: Column name in left DataFrame to merge on.
    - right_on: Column name in right DataFrame to merge on.

    The result will replace the left DataFrame in memory.
    """

    df1 = dataframes[left_df_name]
    df2 = dataframes[right_df_name]

    merged_df = pd.merge(df1, df2, left_on=left_on, right_on=right_on, how='outer')

    dataframes[left_df_name] = merged_df

    return f"Succesfull merge"