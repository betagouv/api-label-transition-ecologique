from pydantic import BaseModel


class UserIdentity(BaseModel):
    """User data retrieved from OpenId token"""
    id: str
    email: str
    firstname: str
    lastname: str
