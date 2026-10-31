# database/schemas/auth.py

from pydantic import BaseModel, Field
from typing import Annotated
from pydantic.networks import EmailStr

class LoginForm(BaseModel):
    email : Annotated[EmailStr, Field(min_length=5,max_length=255)]
    password : Annotated[str, Field(min_length=1,max_length=255)]
    rememberme : bool = False


class LoginSuccess(BaseModel):
    access_token : str

