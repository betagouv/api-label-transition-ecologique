from pydantic import BaseModel


class UserRegistration(BaseModel):
    """Data sent to the auth/register endpoint to create a new user"""
    email: str
    firstname: str
    lastname: str
