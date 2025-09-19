from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes import BasicChatbotNode
from .email_utils import send_email

class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)

         # Node 1: Detect intent
    def detect_intent_node(self, state: State):
        query = state["query"].lower()
        recipient = state.get("recipient")

        if "email" in query or "mail" in query:
            if recipient and "@" in recipient:
                    state["decision"] = "email"
            else:
                state["decision"] = "chat"
        else:
            state["decision"] = "chat"
        return state
    
    def draft_email_node(self, state: State):
        
        SYSTEM_PROMPT = """
        You are an AI assistant that ONLY writes professional, properly formatted emails.  
        Rules:
        - Generate ONLY one final email draft.  
        - Do not provide alternatives or options.  
        - Do not add explanations, comments, or instructions.  
        - The response must contain ONLY the email text.  
        - The email must include: a greeting, body, and closing.  

        """
        prompt = f"{SYSTEM_PROMPT}\n\nUser request: {state['query']}"
        result = self.llm.invoke(prompt)
        state["draft"] = result.content.strip()
        return state
    
    def send_email_node(self, state: State):

        if state.get("recipient") and state.get("draft"):
            send_email(
            to_email=state["recipient"],
            subject=state.get("subject", "No Subject"),
            body=state["draft"]
        )
            state["output"] = f"✅ Email sent to {state['recipient']}"
            # print("finally run ho gya")
    
        else:
            state["output"] = "❌ Missing recipient or draft"
            
        return state
    
    def normal_chat_node(self, state: State):
        chatbot_node = BasicChatbotNode(self.llm)
        return chatbot_node.process(state)


    def setup_graph(self):
        builder = self.graph_builder

        # Add nodes
        builder.add_node("detect_intent", self.detect_intent_node)
        builder.add_node("draft_email", self.draft_email_node)
        builder.add_node("send_email", self.send_email_node)
        builder.add_node("normal_chat", self.normal_chat_node)

        # Add edges with conditions
        builder.add_edge(START, "detect_intent")
    # Add conditional edges from "detect_intent" based on the state
        builder.add_conditional_edges(
            "detect_intent",
            lambda state: state["decision"],
            {"email": "draft_email", "chat": "normal_chat"}
            )
        builder.add_edge("draft_email", "send_email")
        builder.add_edge("send_email", END)
        builder.add_edge("normal_chat", END)

        # Compile graph
        return builder.compile()

