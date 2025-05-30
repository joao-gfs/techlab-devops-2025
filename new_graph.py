import os
import pandas as pd
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from builder import AgentState, build_agent, merger_tools, formatter_tools, dataframes
from settings import INPUT_DIR
from dotenv import load_dotenv

# Agents: 
# 1 identifier: passa as colunas que cada planilha vai ter
# 1 formatter: recebe essa lista e chama a tool de apagar as colunas desnecessárias.
# 1 merger: faz o merge das planilhas.
# 1 somador: escolhe quais as colunas a somar e e faz

load_dotenv()

formatter_agent = build_agent(formatter_tools)
def formatter_call(state: AgentState) -> AgentState:
    response = formatter_agent.invoke(state['messages'])

    return {"messages": [response]}


merger_agent = build_agent(merger_tools)
def merger_call(state: AgentState) -> AgentState:

    system_msg = SystemMessage(content="""""")
    response = merger_agent.invoke([system_msg] + state['messages'])

    return {"messages": [response]}


def should_continue(state: AgentState) -> str: 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls: 
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node(  formatter_call)
graph.add_node("merger_agent", merger_call)

graph.set_entry_point("formatter_agent")

format_tool_node = ToolNode(formatter_tools)
graph.add_node("formatter_tools", format_tool_node)

graph.add_edge("formatter_tools", "formatter_agent")
graph.add_edge("formatter_agent", "merger_agent")

merge_tool_node = ToolNode(merger_tools)
graph.add_node("merger_tools", merge_tool_node)

graph.add_conditional_edges(
    "merger_agent",
    should_continue,
    {
        "continue": "merger_tools",
        "end": END
    }
)

graph.add_edge("merger_tools", "merger_agent")
graph.add_edge("merger_agent", END)

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

def list_files_in(folder: str) -> list[str]:
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def load_dataframes_cache(filenames):
    for filename in filenames:
        path = os.path.join(INPUT_DIR, filename)
        df = pd.read_excel(path)
        dataframes[filename] = df

spreadsheets = list_files_in(INPUT_DIR)
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
                     
                You should call the transfer tool with a message of a list of spreadsheets with the identified columns. Use the following format:

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

def save_all_dataframes(output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)
    for name, df in dataframes.items():
        base_name = os.path.splitext(name)[0]
        output_path = os.path.join(output_dir, f"{base_name}.xlsx")
        df.to_excel(output_path, index=False)

#print_stream(app.stream(inputs, stream_mode="values"))

response = app.invoke(inputs)

print(response)

save_all_dataframes("resultado")