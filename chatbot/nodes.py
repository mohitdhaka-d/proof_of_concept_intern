class BasicChatbotNode:
    def __init__(self, llm):
        self.llm = llm

    def process(self, state):
        user_input = state["query"]
        # Construct a new, more specific prompt that instructs the LLM
        # to format its response as a list of points.
        prompt = (
            f"User query: {user_input}\n\n"
            "Please provide a response that is a concise, bulleted list of points."
        )
        # Invoke the LLM with the new, structured prompt.
        response = self.llm.invoke(prompt)
        return {"output": response.content}