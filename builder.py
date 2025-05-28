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
    return [load_excel, get_columns, save_excel]


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

    After loading, the contents of the file will be available in memory for further processing.
    Use this tool before trying to inspect, modify, or export an Excel file.
    """
    path = os.path.join(INPUT_DIR, input_filename)
    df = pd.read_excel(path)
    
    dataframes[input_filename] = df
    #state['temp_data'] = [input_filename]

    return state


@tool
def save_excel(state: AgentState, filename: str, output_filename: str) -> AgentState:
    """
    Saves an in-memory Excel file to disk.

    Arguments:
    - filename: The name of the file previously loaded into memory.
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
    - input_filename: The name of the file previously loaded into memory.

    Use this tool to inspect the structure of a file and understand what data it contains.
    """
    df = dataframes[input_filename]
    state['temp_data'] = df.columns.to_list()

    return state