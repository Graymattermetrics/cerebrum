"""Implements the models used in api requests and responses.

Synced with the database schemas.
"""

from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field

__all__ = [
    "ClientBaseModel",
    "ClientCreateModel",
    "ClientModel",
    "LoginBodyModel",
    "LoginResponseModel",
    "CogspeedTestRoundModel",
    "CogspeedTestResultModel",
]


class ClientBaseModel(BaseModel):
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


class ClientCreateModel(ClientBaseModel):
    password: str


class ClientModel(ClientBaseModel):
    client_id: str
    # Existing clients also contain api_key field
    api_key: str = Field(
        ..., description="The client API key used to make requests to our servers"
    )
    password_hash: str


class LoginBodyModel(BaseModel):
    email: EmailStr
    password: str


class LoginResponseModel(BaseModel):
    success: bool = Field(..., description="Whether or not the login was successful")
    error: str | None = Field(..., description="Error in request")
    client: ClientModel | None = Field(..., description="The newly created client")


class CogspeedTestRoundModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(alias="status")
    round_type_normalized: str = Field(alias="roundTypeNormalized")
    answer_location: int = Field(alias="answerLocation")
    location_clicked: int | None = Field(alias="locationClicked")
    query_number: str = Field(alias="queryNumber")
    duration: float = Field(alias="duration")
    correct_rolling_mean_ratio: str | float = Field(alias="correctRollingMeanRatio")
    round_number: int = Field(alias="roundNumber")
    round_type: int = Field(alias="roundType")
    time_taken: float = Field(alias="timeTaken")
    is_correct_or_incorrect_from_previous: str | None = Field(
        alias="isCorrectOrIncorrectFromPrevious"
    )
    ratio: float = Field(alias="ratio")
    id: str = Field(alias="_id")
    time_epoch: float = Field(alias="_time_epoch")


class CogspeedTestResultModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    client_id: str
    status: str
    success: bool
    message: str
    version: str = Field(..., description="The config version used in the test")

    status_code: int = Field(alias="statusCode")
    test_duration: int = Field(alias="testDuration")
    number_of_rounds: int = Field(alias="numberOfRounds")
    blocking_round_duration: int = Field(alias="blockingRoundDuration")
    cognitive_processing_index: int = Field(alias="cognitiveProcessingIndex")
    machine_paced_baseline: float = Field(alias="machinePacedBaseline")
    fatigue_level: int = Field(alias="fatigueLevel")
    number_of_roll_mean_limit_exceedences: int = Field(
        alias="numberOfRollMeanLimitExceedences"
    )
    final_ratio: float = Field(alias="finalRatio")
    block_count: int = Field(alias="blockCount")
    lowest_block_time: float = Field(alias="lowestBlockTime")
    highest_block_time: float = Field(alias="highestBlockTime")
    block_range: float = Field(alias="blockRange")
    final_block_diff: float = Field(alias="finalBlockDiff")
    total_machine_paced_answers: int = Field(alias="totalMachinePacedAnswers")
    total_machine_paced_correct_answers: int = Field(
        alias="totalMachinePacedCorrectAnswers"
    )
    total_machine_paced_incorrect_answers: int = Field(
        alias="totalMachinePacedIncorrectAnswers"
    )
    total_machine_paced_no_response_answers: int = Field(
        alias="totalMachinePacedNoResponseAnswers"
    )
    quickest_response: float = Field(alias="quickestResponse")
    quickest_correct_response: float = Field(alias="quickestCorrectResponse")
    slowest_response: float = Field(alias="slowestResponse")
    slowest_correct_response: float = Field(alias="slowestCorrectResponse")
    mean_machine_paced_answer_time: float = Field(alias="meanMachinePacedAnswerTime")
    mean_correct_machine_paced_answer_time: float = Field(
        alias="meanCorrectMachinePacedAnswerTime"
    )
    date: str = Field(alias="_date")
    date_minute_offset: int = Field(alias="_date_minute_offset")
    normalized_location: str = Field(alias="normalizedLocation")
    local_date: str = Field(alias="localDate")
    local_time: str = Field(alias="localTime")

    rounds: list[CogspeedTestRoundModel]
