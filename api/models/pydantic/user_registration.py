from pydantic import BaseModel


class UserRegistration(BaseModel):
    email: str
    firstname: str
    lastname: str
