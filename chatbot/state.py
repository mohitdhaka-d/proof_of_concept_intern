from typing import TypedDict

class State(TypedDict):
    query: str
    recipient: str | None
    subject: str | None
    draft: str | None
    output: str
    decision: str