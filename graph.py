import os
import pandas as pd
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from builder import AgentState, build_agent
from tools import merger_tools, identifier_tools
from settings import INPUT_DIR
from dotenv import load_dotenv
from functions import list_files_in, load_dataframes_cache, print_stream, save_all_dataframes

# Agents: 
#  identifier: passa as colunas que cada planilha vai ter
#  eraser: apaga as colunas que não foram identificadas.
#  renamer: renomeia as colunas de acordo com o tipo de cada beneficio.
#  copy: copia a planilha principal pra resultados
#  merger: faz o merge das outras planilhas
#  somador: escolhe quais as colunas a somar e soma

load_dotenv()

def should_continue(state: AgentState) -> str: 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls: 
        return "end"
    else:
        return "continue"


def make_agent_call(tools: list):
    agent = build_agent(tools)
    
    def agent_call(state: AgentState) -> AgentState:
        response = agent.invoke(state['messages'])
        return {"messages": [response]}
    
    return agent_call

def build_agent_graph(name: str, tools: list):
    graph = StateGraph(AgentState)

    call_fn = make_agent_call(tools)

    agent_node = f"{name}_agent"
    tool_node = f"{name}_tools"

    graph.add_node(agent_node, call_fn)
    graph.set_entry_point(agent_node)

    graph.add_node(tool_node, ToolNode(tools))
    graph.add_edge(tool_node, agent_node)

    graph.add_conditional_edges(
        agent_node,
        should_continue,
        {
            "continue": tool_node,
            "end": END
        }
    )

    graph.add_edge(agent_node, END)

    return graph.compile()


def identifier(spreadsheets: str) -> str:
    app = build_agent_graph("identifier", identifier_tools)

    load_dataframes_cache(spreadsheets)

    inputs = {
        "messages": [
            SystemMessage(
                content=("""
                    You are a assistant designed to help with spreadsheet manipulation.
                    Use the tools to best responde the requests.
                    You will receive the name of the sheets, the columns and a sample of the data. You have to identify on each one:
                    - Identification columns like name, department in the company or documents (CPF, RG, etc)
                    - Total spendings or salary. There will be ***only one*** of it in each spreadsheet.
                    Remove all the remaining columns in each dataframe, including dates and classification (type, category, etc). 
                    If you cant specify correctly what the column is, remove it.
                        
                    Your response should be a list of spreadsheets with the identified columns. Use the following format:

                    ```
                    [SPREADSHEET_NAME]
                    Identification columns: [list of column names]
                    Total column: [column name or "None"]
                    ```

                    Example:
                    ```
                    folha_pagamento.xlsx
                    Identification columns: ['nome', 'departamento']
                    Total column: ['salario_bruto']
                    ```

                    If you believe a file is the main file (the registry), clearly indicate it:
                    ```
                    cadastro_funcionarios.xlsx (MAIN FILE)
                    Identification columns: ['nome', 'cpf', 'departamento']
                    Total column: ['salary']
                    ```

                    Be precise and remove ambiguity in your column selection.
                    """
                )
            ),
            HumanMessage(
                content=(f"""
                    {spreadsheets}
                    """
                )
            )
        ]
    }

    result = app.invoke(inputs)

    return result["messages"][-1].content


if __name__ == "__main__":

    spreadsheets = list_files_in(INPUT_DIR)
    res = identifier(spreadsheets)
    print(res)