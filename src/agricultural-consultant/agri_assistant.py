'''from tools.seed_prices_tool import get_seed_price_tool
from tools.yield_estimation_tool import get_yield_data_tool
from tools.fertilizer_tool import get_fertilizer_tool
from tools.market_prices_tool import get_market_price_tool

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- QueryAnalysis ---
class QueryAnalysis(BaseModel):
    intent: Literal["seed_price", "yield_data", "market_price", "fertilizer", "general"]
    crop_name: Optional[str] = Field(description="Bitki veya ürün adı")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

# --- LangGraph State ---
class AgentState(TypedDict):
    user_input: str
    messages: List[Any]
    tool_results: Dict[str, str]
    final_response: str
    query_analysis: Optional[QueryAnalysis]

# --- LLM ---
llm = ChatOpenAI(
    model="Alpata/OctaAI-32B",
    base_url="http://10.10.1.150:8000/v1",
    api_key="EMPTY",
    temperature=0.4,
)

# --- Prompt ---
RESPONSE_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "Sen bir tarım danışmanısın. Kullanıcının sorusunu anlayarak doğru bilgileri özetle. Sayısal verileri vurgula."),
    ("human", "Soru: {user_input}\nTool sonuçları:\n{tool_results}")
])

# --- Analiz Yardımcıları ---
def extract_crop_name(query: str) -> Optional[str]:
    known_crops = ["buğday", "arpa", "mısır", "ayçiçeği", "nohut", "domates", "patates", "mercimek"]
    for crop in known_crops:
        if crop in query.lower():
            return crop
    return None

def create_fallback_analysis(query: str) -> QueryAnalysis:
    query_lower = query.lower()
    crop = extract_crop_name(query)

    if "tohum" in query_lower:
        return QueryAnalysis(intent="seed_price", crop_name=crop, confidence=0.8, reasoning="Tohum kelimesi geçti")
    if "verim" in query_lower:
        return QueryAnalysis(intent="yield_data", crop_name=crop, confidence=0.8, reasoning="Verim kelimesi geçti")
    if "gübre" in query_lower:
        return QueryAnalysis(intent="fertilizer", crop_name=crop, confidence=0.8, reasoning="Gübre kelimesi geçti")
    if "pazar" in query_lower or "fiyat" in query_lower:
        return QueryAnalysis(intent="market_price", crop_name=crop, confidence=0.8, reasoning="Fiyat/pazar kelimesi")

    return QueryAnalysis(intent="general", crop_name=None, confidence=0.5, reasoning="Genel sorgu")

# --- Node: Sorgu Analizi ---
def query_analyzer_node(state: AgentState) -> AgentState:
    query = state["user_input"]
    analysis = create_fallback_analysis(query)
    state["query_analysis"] = analysis
    return state

# --- Node: Tool Seçimi ve Çalıştırma ---
def tool_executor_node(state: AgentState) -> AgentState:
    analysis = state["query_analysis"]
    results = {}
    crop = analysis.crop_name

    if not crop:
        results["bilgi"] = "Ürün adı tespit edilemedi."
        state["tool_results"] = results
        return state

    if analysis.intent == "seed_price":
        results["tohum"] = get_seed_price_tool.invoke(crop)
    elif analysis.intent == "yield_data":
        results["verim"] = get_yield_data_tool.invoke(crop)
    elif analysis.intent == "fertilizer":
        results["gübre"] = get_fertilizer_tool.invoke(crop)
    elif analysis.intent == "market_price":
        results["fiyat"] = get_market_price_tool.invoke(crop)
    else:
        results["bilgi"] = "Anlamlandırılamayan sorgu."

    state["tool_results"] = results
    return state

# --- Node: Yanıt Üretimi ---
def response_generator_node(state: AgentState) -> AgentState:
    prompt = RESPONSE_TEMPLATE.format_messages(
        user_input=state["user_input"],
        tool_results="\n".join(f"{k}: {v}" for k, v in state["tool_results"].items())
    )
    response = llm.invoke(prompt)
    state["final_response"] = response.content
    return state

# --- Graph Oluşturma ---
def create_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("tool_execution", tool_executor_node)
    workflow.add_node("response_generator", response_generator_node)

    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", "tool_execution")
    workflow.add_edge("tool_execution", "response_generator")
    workflow.add_edge("response_generator", END)
    return workflow.compile()

# --- CLI Test ---
if __name__ == "__main__":
    app = create_graph()
    print("Komut girin (\u00f6rnek: bu\u011fday i\u00e7in tohum fiyat\u0131 veya verim bilgisi):")

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ["çık", "çıkış"]:
                break

            state = {
                "user_input": user_input,
                "messages": [],
                "tool_results": {},
                "final_response": "",
                "query_analysis": None
            }

            result = app.invoke(state)
            print(result["final_response"])

        except Exception as e:
            print(f"Hata: {e}")'''
from tools.seed_prices_tool import get_seed_price_tool
from tools.yield_estimation_tool import get_yield_data_tool
from tools.fertilizer_tool import get_fertilizer_tool
from tools.market_prices_tool import get_market_price_tool

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- QueryAnalysis ---
class QueryAnalysis(BaseModel):
    used_intents: List[str] = Field(description="Kullanıcı sorgusuna göre tespit edilen niyetler")
    crop_name: Optional[str] = Field(description="Bitki veya ürün adı")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

# --- LangGraph State ---
class AgentState(TypedDict):
    user_input: str
    messages: List[Any]
    tool_results: Dict[str, str]
    final_response: str
    query_analysis: Optional[QueryAnalysis]

# --- LLM ---
llm = ChatOpenAI(
    model="Alpata/OctaAI-32B",
    base_url="http://10.10.1.150:8000/v1",
    api_key="EMPTY",
    temperature=0.4,
)

# --- Prompt ---
RESPONSE_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "Sen bir tarım danışmanısın. Kullanıcının sorusunu anlayarak doğru bilgileri özetle. Sayısal verileri vurgula."),
    ("human", "Soru: {user_input}\nTool sonuçları:\n{tool_results}")
])

# --- Analiz Yardımcıları ---
def extract_crop_name(query: str) -> Optional[str]:
    known_crops = ["buğday", "arpa", "mısır", "ayçiçeği", "nohut", "domates", "patates", "mercimek"]
    for crop in known_crops:
        if crop in query.lower():
            return crop
    return None

def create_fallback_analysis(query: str) -> QueryAnalysis:
    query_lower = query.lower()
    crop = extract_crop_name(query)

    intents = []
    if "tohum" in query_lower:
        intents.append("seed_price")
    if "verim" in query_lower:
        intents.append("yield_data")
    if "gübre" in query_lower:
        intents.append("fertilizer")
    if "pazar" in query_lower or "fiyat" in query_lower:
        intents.append("market_price")

    if not intents:
        intents.append("general")

    return QueryAnalysis(used_intents=intents, crop_name=crop, confidence=0.8, reasoning="Anahtar kelimeler ile tespit edildi")

# --- Node: Sorgu Analizi ---
def query_analyzer_node(state: AgentState) -> AgentState:
    query = state["user_input"]
    analysis = create_fallback_analysis(query)
    state["query_analysis"] = analysis
    return state

# --- Node: Tool Seçimi ve Çalıştırma ---
def tool_executor_node(state: AgentState) -> AgentState:
    analysis = state["query_analysis"]
    results = {}
    crop = analysis.crop_name

    if not crop:
        results["bilgi"] = "Ürün adı tespit edilemedi."
        state["tool_results"] = results
        return state

    for intent in analysis.used_intents:
        if intent == "seed_price":
            results["tohum"] = get_seed_price_tool.invoke(crop)
        elif intent == "yield_data":
            results["verim"] = get_yield_data_tool.invoke(crop)
        elif intent == "fertilizer":
            results["gübre"] = get_fertilizer_tool.invoke(crop)
        elif intent == "market_price":
            results["fiyat"] = get_market_price_tool.invoke(crop)
        else:
            results["bilgi"] = "Anlamlandırılamayan sorgu."

    state["tool_results"] = results
    return state

# --- Node: Yanıt Üretimi ---
def response_generator_node(state: AgentState) -> AgentState:
    prompt = RESPONSE_TEMPLATE.format_messages(
        user_input=state["user_input"],
        tool_results="\n".join(f"{k}: {v}" for k, v in state["tool_results"].items())
    )
    response = llm.invoke(prompt)
    state["final_response"] = response.content
    return state

# --- Graph Oluşturma ---
def create_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("tool_execution", tool_executor_node)
    workflow.add_node("response_generator", response_generator_node)

    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", "tool_execution")
    workflow.add_edge("tool_execution", "response_generator")
    workflow.add_edge("response_generator", END)
    return workflow.compile()

# --- CLI Test ---
if __name__ == "__main__":
    app = create_graph()
    print("Komut girin (örnek: buğday için tohum ve verim bilgisi):")

    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ["çık", "çıkış"]:
                break

            state = {
                "user_input": user_input,
                "messages": [],
                "tool_results": {},
                "final_response": "",
                "query_analysis": None
            }

            result = app.invoke(state)
            print(result["final_response"])

        except Exception as e:
            print(f"Hata: {e}")

