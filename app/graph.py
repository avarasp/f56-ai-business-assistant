import json
from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END

from app.llm import structured_call, text_call
from app.prompts import (
    ROUTER_SYSTEM,
    SALES_PLANNER_SYSTEM,
    PRODUCT_PLANNER_SYSTEM,
    CONTACT_PLANNER_SYSTEM,
    ANSWER_SYSTEM,
)
from app.schemas import RouteDecision, SalesQuery, ProductQuery, ContactQuery
from app.tools.sales import get_sales
from app.tools.products import get_products
from app.tools.contacts import get_contacts


class GraphState(TypedDict, total=False):
    question: str
    intent: str
    tool_name: str
    tool_input: dict
    tool_result: object
    answer: str
    error: str


def route_question(state: GraphState) -> GraphState:
    decision = structured_call(
        system=ROUTER_SYSTEM,
        user=state["question"],
        schema=RouteDecision,
    )
    return {
        **state,
        "intent": decision.intent,
    }


def choose_route(state: GraphState) -> Literal[
    "plan_sales", "plan_products", "plan_contacts", "unsupported"
]:
    return {
        "sales": "plan_sales",
        "products": "plan_products",
        "contacts": "plan_contacts",
        "unsupported": "unsupported",
    }[state["intent"]]


def plan_sales(state: GraphState) -> GraphState:
    plan = structured_call(
        system=SALES_PLANNER_SYSTEM,
        user=state["question"],
        schema=SalesQuery,
    )
    return {
        **state,
        "tool_name": "get_sales",
        "tool_input": plan.model_dump(mode="json"),
    }


def run_sales(state: GraphState) -> GraphState:
    try:
        plan = SalesQuery.model_validate(state["tool_input"])
        result = get_sales(plan)
        return {**state, "tool_result": result}
    except Exception as exc:
        return {**state, "error": f"sales tool failed: {exc}"}


def plan_products(state: GraphState) -> GraphState:
    plan = structured_call(
        system=PRODUCT_PLANNER_SYSTEM,
        user=state["question"],
        schema=ProductQuery,
    )
    return {
        **state,
        "tool_name": "get_products",
        "tool_input": plan.model_dump(mode="json"),
    }


def run_products(state: GraphState) -> GraphState:
    try:
        plan = ProductQuery.model_validate(state["tool_input"])
        result = get_products(plan)
        return {**state, "tool_result": result}
    except Exception as exc:
        return {**state, "error": f"products tool failed: {exc}"}


def plan_contacts(state: GraphState) -> GraphState:
    plan = structured_call(
        system=CONTACT_PLANNER_SYSTEM,
        user=state["question"],
        schema=ContactQuery,
    )
    return {
        **state,
        "tool_name": "get_contacts",
        "tool_input": plan.model_dump(mode="json"),
    }


def run_contacts(state: GraphState) -> GraphState:
    try:
        plan = ContactQuery.model_validate(state["tool_input"])
        result = get_contacts(plan)
        return {**state, "tool_result": result}
    except Exception as exc:
        return {**state, "error": f"contacts tool failed: {exc}"}


def unsupported(state: GraphState) -> GraphState:
    return {
        **state,
        "answer": (
            "No sé responder eso con las herramientas que tengo disponibles "
            "por ahora. Actualmente puedo consultar ventas, productos y contactos."
        ),
    }


def render_answer(state: GraphState) -> GraphState:
    if state.get("error"):
        return {
            **state,
            "answer": (
                "No pude obtener una respuesta confiable desde la base de datos. "
                f"Detalle técnico: {state['error']}"
            ),
        }

    payload = json.dumps(
        {
            "question": state["question"],
            "tool_name": state.get("tool_name"),
            "tool_result": state.get("tool_result"),
        },
        ensure_ascii=False,
        default=str,
    )

    answer = text_call(
        system=ANSWER_SYSTEM,
        user=payload,
    )
    return {**state, "answer": answer}


builder = StateGraph(GraphState)

builder.add_node("route_question", route_question)
builder.add_node("plan_sales", plan_sales)
builder.add_node("run_sales", run_sales)
builder.add_node("plan_products", plan_products)
builder.add_node("run_products", run_products)
builder.add_node("plan_contacts", plan_contacts)
builder.add_node("run_contacts", run_contacts)
builder.add_node("unsupported", unsupported)
builder.add_node("render_answer", render_answer)

builder.set_entry_point("route_question")

builder.add_conditional_edges(
    "route_question",
    choose_route,
    {
        "plan_sales": "plan_sales",
        "plan_products": "plan_products",
        "plan_contacts": "plan_contacts",
        "unsupported": "unsupported",
    },
)

builder.add_edge("plan_sales", "run_sales")
builder.add_edge("run_sales", "render_answer")

builder.add_edge("plan_products", "run_products")
builder.add_edge("run_products", "render_answer")

builder.add_edge("plan_contacts", "run_contacts")
builder.add_edge("run_contacts", "render_answer")

builder.add_edge("unsupported", END)
builder.add_edge("render_answer", END)

graph = builder.compile()


def ask(question: str) -> dict:
    return graph.invoke({"question": question})
