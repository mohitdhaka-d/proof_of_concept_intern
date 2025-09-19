from fastapi import FastAPI
from pydantic import BaseModel,EmailStr,Field
from chatbot.graph_builder import GraphBuilder
from chatbot.llm_gemini import GeminiLLM

app = FastAPI(title="LangGraph Chatbot + Email API")
GEMINI_API_KEY = "AIzaSyBxMzHG-BSRHbC_WtbPjN8QaO1emhr1_kc"

class ChatRequest(BaseModel):
    query: str
    recipient: str| None = Field(None)
    subject: str | None = None


class ChatResponse(BaseModel):
    output: str

def create_initial_state(request: ChatRequest) -> dict:
    return {
        "query": request.query,
        "recipient": request.recipient,
        "subject": request.subject,
        "draft": None,
        "output": "",
        "decision": ""
    }

# Init Gemini
llm = GeminiLLM(api_key=GEMINI_API_KEY, model="gemini-2.0-flash")
builder = GraphBuilder(llm)
graph = builder.setup_graph()


@app.get("/")
def root():
    return {"message": "API is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    state = create_initial_state(request)
    result = graph.invoke(state)
    return {"output": result["output"]}