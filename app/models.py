"""This file contains the models used in the endpoints in requests and responses
from the client-server.

"""

from datetime import date
from pydantic import BaseModel, EmailStr, Field



class ClientCreate(BaseModel):
    full_name: str = Field(..., examples=["Jane Doe"])
    date_of_birth: date
    gender: str = Field(..., examples=["Female"])
    email: EmailStr # Pydantic will validate this is a valid email format
    country: str = Field(..., examples=["Canada"])

    # Additional fields
    education_level: str | None = Field(None, examples=["Bachelor's Degree"])
    occupation: str | None = Field(None, examples=["Software Developer"])
    handedness: str | None = Field(None, examples=["Right"])
    notes: str | None = Field(None, examples=["Signed up with the Biggs Insitute"])

    class Config:
        # This allows the Pydantic model to be created from ORM objects,
        # which is more useful for response models but good practice to know.
        orm_mode = True