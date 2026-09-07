from pydantic import BaseModel


class ApiRequest(BaseModel):
    """Represents an API request with a prompt and optional parameters."""
    message: str
