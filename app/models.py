"""Implements the models used in api requests and responses.

Synced with the database schemas.
"""

from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field

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
    # notes: str | None = Field(None, examples=["Signed up with the Biggs Institute"])

    model_config = ConfigDict(from_attributes=True)
