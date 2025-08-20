"""Implements the schemas used in the database."""

import uuid
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

__all__ = ["Base", "Client", "CogspeedTestResult", "CogspeedTestRound"]


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"

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
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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

    test_results: Mapped[list["CogspeedTestResult"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class CogspeedTestResult(Base):
    __tablename__ = "cogspeed_test_results"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.client_id"), primary_key=True
    )
    client: Mapped["Client"] = relationship(back_populates="test_results")
    rounds: Mapped[list["CogspeedTestRound"]] = relationship(
        back_populates="test_result", cascade="all, delete-orphan"
    )

    status_code: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    success: Mapped[bool] = mapped_column(Boolean)
    message: Mapped[str] = mapped_column(String)
    test_duration: Mapped[int] = mapped_column(Integer)
    number_of_rounds: Mapped[int] = mapped_column(Integer)
    blocking_round_duration: Mapped[int] = mapped_column(Integer)
    cognitive_processing_index: Mapped[int] = mapped_column(Integer)
    machine_paced_baseline: Mapped[float] = mapped_column(Float)
    version: Mapped[str] = mapped_column(String)
    fatigue_level: Mapped[int] = mapped_column(Integer)
    number_of_roll_mean_limit_exceedences: Mapped[int] = mapped_column(Integer)
    final_ratio: Mapped[float] = mapped_column(Float)
    block_count: Mapped[int] = mapped_column(Integer)
    lowest_block_time: Mapped[float] = mapped_column(Float)
    highest_block_time: Mapped[float] = mapped_column(Float)
    block_range: Mapped[int] = mapped_column(Integer)
    final_block_diff: Mapped[int] = mapped_column(Integer)
    total_machine_paced_answers: Mapped[int] = mapped_column(Integer)
    total_machine_paced_correct_answers: Mapped[int] = mapped_column(Integer)
    total_machine_paced_incorrect_answers: Mapped[int] = mapped_column(Integer)
    total_machine_paced_no_response_answers: Mapped[int] = mapped_column(Integer)
    quickest_response: Mapped[float] = mapped_column(Float)
    quickest_correct_response: Mapped[float] = mapped_column(Float)
    slowest_response: Mapped[float] = mapped_column(Float)
    slowest_correct_response: Mapped[float] = mapped_column(Float)
    mean_machine_paced_answer_time: Mapped[float] = mapped_column(Float)
    mean_correct_machine_paced_answer_time: Mapped[float] = mapped_column(Float)
    date: Mapped[str] = mapped_column(String)
    date_minute_offset: Mapped[int] = mapped_column(Integer)
    normalized_location: Mapped[str] = mapped_column(String)
    local_date: Mapped[str] = mapped_column(String)
    local_time: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CogspeedTestRound(Base):
    __tablename__ = "cogspeed_test_rounds"

    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    test_id: Mapped[str] = mapped_column(String, primary_key=True)
    round_number: Mapped[int] = mapped_column(Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["client_id", "test_id"],
            ["cogspeed_test_results.client_id", "cogspeed_test_results.id"],
        ),
    )

    test_result: Mapped["CogspeedTestResult"] = relationship(back_populates="rounds")

    status: Mapped[str] = mapped_column(String)
    round_type_normalized: Mapped[str] = mapped_column(String)
    answer_location: Mapped[int] = mapped_column(Integer)
    location_clicked: Mapped[int | None] = mapped_column(Integer, nullable=True)
    query_number: Mapped[str] = mapped_column(String)
    duration: Mapped[float] = mapped_column(Float)
    correct_rolling_mean_ratio: Mapped[str | float] = mapped_column(
        String
    )  # store as string to handle "n/a"
    round_type: Mapped[int] = mapped_column(Integer)
    time_taken: Mapped[float] = mapped_column(Float)
    is_correct_or_incorrect_from_previous: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    ratio: Mapped[float] = mapped_column(Float)
    id: Mapped[str] = mapped_column(String, unique=True)
    time_epoch: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
