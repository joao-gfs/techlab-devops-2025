from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from builder import AgentState, make_agent_call

# Agents: 
#  [X] identifier: passa as colunas que cada planilha vai ter
#  [X] eraser: apaga as colunas que não foram identificadas.
#  [X] renamer: renomeia as colunas de acordo com o tipo de cada beneficio.
#  [X] merger: faz o merge das outras planilhas
#  [X] final eraser: apaga colunas repetidas no documento mergeado
#  [x] somador: escolhe quais as colunas a somar e soma

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