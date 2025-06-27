from typing import Annotated
from pydantic import BaseModel, EmailStr, StringConstraints


class UserRegister(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: Annotated[str, StringConstraints(min_length=3)]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: Annotated[str, StringConstraints(min_length=3)]
