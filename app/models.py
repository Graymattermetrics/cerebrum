"""Implements the models used in api requests and responses.

Synced with the database schemas.
"""

from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field

__all__ = [
    "Base_Client_Model_",
    "Client_Create_Model_",
    "Client_Model_",
    "LoginBody_Model_",
    "LoginResponse_Model_",
]


class Base_Client_Model_(BaseModel):
    email: EmailStr
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


class Client_Create_Model_(Base_Client_Model_):
    password: str


class Client_Model_(Base_Client_Model_):
    client_id: str
    # Existing clients also contain api_key field
    api_key: str = Field(
        ..., description="The client API key used to make requests to our servers"
    )
    password_hash: str


class LoginBody_Model_(BaseModel):
    email: EmailStr
    password: str


class LoginResponse_Model_(BaseModel):
    success: bool = Field(..., description="Whether or not the login was successful")
    error: str | None = Field(..., description="Error in request")
    client: Client_Model_ | None = Field(..., description="The newly created client")
