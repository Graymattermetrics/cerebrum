"""This file contains the models used in the endpoints in requests and responses
from the client-server.

"""

from datetime import date
from pydantic import BaseModel, EmailStr, Field

__all__ = ["LoginBody", "LoginResponse", "ClientCreate"]


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool = Field(..., description="Whether or not the login was successful")
    


class ClientCreate(BaseModel):
    email: EmailStr
    password: str

    full_name: str = Field(..., examples=["Jane Doe"])
    date_of_birth: date
    gender: str = Field(..., examples=["Female"])
    country: str = Field(..., examples=["Canada"])

    # Additional fields
    education_level: str | None = Field(None, examples=["Bachelor's Degree"])
    occupation: str | None = Field(None, examples=["Software Developer"])
    handedness: str | None = Field(None, examples=["Right"])
    # notes: str | None = Field(None, examples=["Signed up with the Biggs Insitute"])

    class Config:
        orm_mode = True

