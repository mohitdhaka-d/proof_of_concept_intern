from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from chatbot.state import State
import uuid

# Assuming your imports are correct
from chatbot.graph_builder import GraphBuilder
from chatbot.llm_gemini import GeminiLLM

# Simple in-memory store for session data.
# WARNING: Do not use in production. Use a database or cache like Redis.
session_store: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title="LangGraph Chatbot + Email API")
GEMINI_API_KEY = "AIzaSyC6xTKW9RHSOA4HE9tOMxvl-59l8alqC38" # Make sure to set your API key

class ChatRequest(BaseModel):
    query: str
    recipient: Optional[str] = Field(None)
    subject: Optional[str] = None
    session_id: Optional[str] = Field(None)

class ConfirmRequest(BaseModel):
    session_id: str
    user_action: str # "send" or "cancel"

class ChatResponse(BaseModel):
    output: Optional[str] = None
    awaiting_confirmation: bool = False
    draft: Optional[str] = None
    session_id: str

# Init Gemini and Graph
llm = GeminiLLM(api_key=GEMINI_API_KEY, model="gemini-2.0-flash")
builder = GraphBuilder(llm)
graph = builder.setup_graph()


@app.get("/")
def home():
    return {"message": "Server running, replies are auto-detected in background"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # Retrieve existing state or create a new one
    session_id = request.session_id or str(uuid.uuid4())
    state = session_store.get(session_id, {
        "query": request.query,
        "recipient": request.recipient,
        "subject": request.subject,
        "draft": None,
        "output": "",
        "decision": "",
        "user_confirmation": None,
        "status":""
    })
    
    state["query"] = request.query
    
    # Run the graph until a decision is needed or it completes
    result = graph.invoke(state)

    # Check the result to see if we need to wait for a user response
    if result["status"] == "awaiting_input":
        # Save the current state and prompt the user for confirmation
        session_store[session_id] = result
        return ChatResponse(
            output="Email draft created. Please confirm.",
            awaiting_confirmation=True,
            draft=result["draft"],
            session_id=session_id
        )

    # If the graph completed, clear the session and return the final output
    if session_id in session_store:
        del session_store[session_id]
        
    return ChatResponse(output=result["output"], session_id=session_id)


@app.post("/confirm", response_model=ChatResponse)
def confirm_endpoint(request: ConfirmRequest):
    # Get the stored state
    state = session_store.get(request.session_id)
    if not state:
        return ChatResponse(output="Error: Session not found.", session_id=request.session_id)
    
    state["user_confirmation"] = request.user_action.lower()

    # Resume the graph from where it left off
    result = graph.invoke(state)

    # Clear the session after the process is complete
    if request.session_id in session_store:
        del session_store[request.session_id]

    return ChatResponse(output=result.get("output", ""), session_id=request.session_id)


from chatbot.check_replies_function import check_replies_function
scheduler = BackgroundScheduler()
scheduler.add_job(check_replies_function,
                   "interval",
                     seconds=10,
                     max_instances=3,
                     coalesce=True)  # check every 10 seconds
scheduler.start()
print("🔄 Reply checker started in background...")

# import time
# try:
#     while True:
#         time.sleep(1)
# except (KeyboardInterrupt, SystemExit):
#     scheduler.shutdown()
#     print("🛑 Scheduler stopped.")


# @app.get("/check-replies")
# def check_replies():
#     check_replies_function()
#     return {"status": "Checked inbox for replies"}