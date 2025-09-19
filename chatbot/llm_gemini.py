import google.generativeai as genai

class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def invoke(self, text: str):

        system_prompt = (
            "You are a helpful and creative writing assistant. "
            "Your task is to generate a concise and engaging response to the user's request."
        )

        user_prompt = f"User's request: {text}"
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = self.model.generate_content(full_prompt)
        # mimic ChatOpenAI .invoke(content)
        class Result:
            content = response.text
        return Result()
