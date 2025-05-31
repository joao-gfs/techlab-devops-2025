import os
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from builder import AgentState, make_agent_call
from tools import identifier_tools, eraser_tools, renamer_tools, merger_tools, dataframes, adder_tools
from settings import INPUT_DIR, OUTPUT_DIR
from dotenv import load_dotenv
from functions import list_files_in, load_dataframes_cache, print_stream, save_all_dataframes

# Agents: 
#  [X] identifier: passa as colunas que cada planilha vai ter
#  [X] eraser: apaga as colunas que não foram identificadas.
#  [X] renamer: renomeia as colunas de acordo com o tipo de cada beneficio.
#  [X] copy: copia a planilha principal pra resultados
#  [ ] merger: faz o merge das outras planilhas
#  [ ] somador: escolhe quais as colunas a somar e soma

load_dotenv()

def should_continue(state: AgentState) -> str: 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls: 
        return "end"
    else:
        return "continue"

def build_agent_graph(name: str, tools: list, qtd_tokens: int, parallel: bool = True):
    graph = StateGraph(AgentState)

    call_fn = make_agent_call(tools, qtd_tokens, parallel)

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


def run_agent(name: str ,prompt: dict, tools: list, qtd_tokens: int, parallel=True) -> str:
    app = build_agent_graph(name, tools, qtd_tokens, parallel)

    result = app.invoke(prompt)

    return result["messages"][-1].content

def stream_agent_execution(name: str, prompt: dict, tools: list, qtd_tokens: int, parallel: bool = True) -> str:
    app = build_agent_graph(name, tools, qtd_tokens, parallel)

    final_state = None
    stream = app.stream(prompt, stream_mode="values")

    for step in stream:
        final_state = step
        message = step["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

    return final_state["messages"][-1].content if final_state else ""


if __name__ == "__main__":

    res_merger = "Dados Colaboradores.xlsx"

    spreadsheets = list_files_in(OUTPUT_DIR)
    load_dataframes_cache(spreadsheets, OUTPUT_DIR)

    inputs_adder = {
    "messages": [
        SystemMessage(
            content=(
                "You're an assistant for spreadsheet column adding. Use the tools provided to inspect and sum data in a file"
            )
        ),
        HumanMessage(
            content=(
    f"""
    ### Instructions:

        1. Analyse the sample data in the file and identify the monetary columns
        2. Sum them using the 'add_columns' tools
        You **MUST** pass the name of the file WITH the extension (.xlsx)

        File: {res_merger}
    """
            )
        )
    ]
}

    res_adder = stream_agent_execution("adder", inputs_adder, adder_tools, qtd_tokens=750)
    print("\n[ADDER]")
    print(res_adder)

    save_all_dataframes('test_data')