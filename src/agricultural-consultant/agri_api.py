from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from agri_assistant import create_graph, AgentState, QueryAnalysis  # mevcut modülün içinden

app = FastAPI(title="Tarım Danışmanı API", version="1.0.0")
graph_app = create_graph()

# API input modeli
class QueryRequest(BaseModel):
    prompt: str

# API output modeli
class QueryResponse(BaseModel):
    response: str
    tool_results: Dict[str, str]
    query_analysis: Optional[Dict[str, Any]]

@app.get("/")
def root():
    return {
        "message": "Tarım Danışmanı API çalışıyor.",
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Tarım Danışmanı API çalışıyor."}

@app.post("/query", response_model=QueryResponse)
def process_query(request: QueryRequest):
    try:
        initial_state = AgentState(
            user_input=request.prompt,
            messages=[],
            tool_results={},
            final_response="",
            query_analysis=None
        )
        result = graph_app.invoke(initial_state)

        return QueryResponse(
            response=result["final_response"],
            tool_results=result["tool_results"],
            query_analysis=result["query_analysis"].model_dump() if result["query_analysis"] else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
