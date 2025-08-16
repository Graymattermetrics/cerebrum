"""Implements the schemas used in the database."""

import uuid
from datetime import datetime, date

from pydantic import ConfigDict
from sqlmodel import (
    SQLModel,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

__all__ = ["Client", "TestResult", "TestRound"]


class Client(SQLModel, table=True):
    __tablename__ = "clients"  # type: ignore
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore

    client_id: Mapped[str] = mapped_column(String, primary_key=True)

    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)

    # Additional optional data
    education_level: Mapped[str | None] = mapped_column(String)
    occupation: Mapped[str | None] = mapped_column(String)
    handedness: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(String)

    # Metrics
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    login_count: Mapped[int] = mapped_column(default=0, autoincrement=True)

    # Security
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String)

    api_key: Mapped[str] = mapped_column(
        String, unique=True, default=lambda: uuid.uuid4().hex, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    test_results: Mapped[list["TestResult"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class TestResult(SQLModel, table=True):
    __tablename__ = "cogspeed_test_result"  # type: ignore
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore

    id: Mapped[str] = mapped_column("id", String, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.client_id"), primary_key=True
    )
    client: Mapped["Client"] = relationship(back_populates="test_results")

    status_code: Mapped[int] = mapped_column("statusCode", Integer)
    status: Mapped[str] = mapped_column("status", String)
    success: Mapped[bool] = mapped_column("success", Boolean)
    message: Mapped[str] = mapped_column("message", String)
    test_duration: Mapped[int] = mapped_column("testDuration", Integer)
    number_of_rounds: Mapped[int] = mapped_column("numberOfRounds", Integer)
    blocking_round_duration: Mapped[int] = mapped_column(
        "blockingRoundDuration", Integer
    )
    cognitive_processing_index: Mapped[int] = mapped_column(
        "cognitiveProcessingIndex", Integer
    )
    machine_paced_baseline: Mapped[float] = mapped_column("machinePacedBaseline", Float)
    version: Mapped[str] = mapped_column("version", String)
    fatigue_level: Mapped[int] = mapped_column("fatigueLevel", Integer)
    number_of_roll_mean_limit_exceedences: Mapped[int] = mapped_column(
        "numberOfRollMeanLimitExceedences", Integer
    )
    final_ratio: Mapped[float] = mapped_column("finalRatio", Float)
    block_count: Mapped[int] = mapped_column("blockCount", Integer)
    lowest_block_time: Mapped[float] = mapped_column("lowestBlockTime", Float)
    highest_block_time: Mapped[float] = mapped_column("highestBlockTime", Float)
    block_range: Mapped[int] = mapped_column("blockRange", Integer)
    final_block_diff: Mapped[int] = mapped_column("finalBlockDiff", Integer)
    total_machine_paced_answers: Mapped[int] = mapped_column(
        "totalMachinePacedAnswers", Integer
    )
    total_machine_paced_correct_answers: Mapped[int] = mapped_column(
        "totalMachinePacedCorrectAnswers", Integer
    )
    total_machine_paced_incorrect_answers: Mapped[int] = mapped_column(
        "totalMachinePacedIncorrectAnswers", Integer
    )
    total_machine_paced_no_response_answers: Mapped[int] = mapped_column(
        "totalMachinePacedNoResponseAnswers", Integer
    )
    quickest_response: Mapped[float] = mapped_column("quickestResponse", Float)
    quickest_correct_response: Mapped[float] = mapped_column(
        "quickestCorrectResponse", Float
    )
    slowest_response: Mapped[float] = mapped_column("slowestResponse", Float)
    slowest_correct_response: Mapped[float] = mapped_column(
        "slowestCorrectResponse", Float
    )
    mean_machine_paced_answer_time: Mapped[float] = mapped_column(
        "meanMachinePacedAnswerTime", Float
    )
    mean_correct_machine_paced_answer_time: Mapped[float] = mapped_column(
        "meanCorrectMachinePacedAnswerTime", Float
    )
    date: Mapped[str] = mapped_column("_date", String)
    date_minute_offset: Mapped[int] = mapped_column("_date_minute_offset", Integer)
    normalized_location: Mapped[str] = mapped_column("normalizedLocation", String)
    local_date: Mapped[str] = mapped_column("localDate", String)
    local_time: Mapped[str] = mapped_column("localTime", String)

    config_version: Mapped[str] = mapped_column("configVersion", String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # rounds: Mapped[list["TestRound"]] = relationship(
    #     back_populates="test_result",
    #     cascade="all, delete-orphan",
    #     foreign_keys="[TestRound.client_id, TestRound.test_id]"
    # )


class TestRound(SQLModel, table=True):
    __tablename__ = "cogspeed_test_round"  # type: ignore
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore

    # Composite primary key: (client_id, test_id, num)
    client_id: Mapped[str] = mapped_column(
        String, ForeignKey("cogspeed_test_result.client_id"), primary_key=True
    )
    test_id: Mapped[str] = mapped_column(
        String, ForeignKey("cogspeed_test_result.id"), primary_key=True
    )
    num: Mapped[int] = mapped_column("Num", Integer, primary_key=True)

    type: Mapped[str] = mapped_column("Type", String)
    duration: Mapped[float] = mapped_column("Duration", Float)
    response: Mapped[float] = mapped_column("Response", Float)
    status: Mapped[str] = mapped_column("Status", String)
    ratio: Mapped[float] = mapped_column("Ratio", Float)
    rm: Mapped[float] = mapped_column("Rm", Float)
    query: Mapped[str] = mapped_column("Query", String)
    location: Mapped[str] = mapped_column("Location", String)
    clicked: Mapped[bool] = mapped_column("Clicked", Boolean)
    previous: Mapped[str] = mapped_column("Previous", String)

    # test_result_id: Mapped[int] = mapped_column(ForeignKey("test_result.id"))
    # test_result: Mapped["TestResult"] = relationship(
    #     back_populates="rounds",
    #     foreign_keys=[client_id, test_id]
    # )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
