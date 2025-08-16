from sqlalchemy import inspect
from app.models import CogspeedTestResultModel, CogspeedTestRoundModel
from app.schemas import CogspeedTestResult, CogspeedTestRound


def test_testresult_pydantic_and_sqlalchemy_schemas_are_in_sync():
    sqlalchemy_columns = {c.name for c in inspect(CogspeedTestResult).columns}
    pydantic_fields = set(CogspeedTestResultModel.model_fields.keys())

    sqlalchemy_only = {"created_at"}
    pydantic_only = {"rounds"}

    expected_pydantic_fields = (sqlalchemy_columns - sqlalchemy_only).union(
        pydantic_only
    )

    assert pydantic_fields == expected_pydantic_fields, (
        f"Pydantic model TestResult_Model_ is out of sync with SQLAlchemy model TestResult.\n"
        f"Missing from Pydantic: {sorted(list(expected_pydantic_fields - pydantic_fields))}\n"
        f"Unexpected in Pydantic: {sorted(list(pydantic_fields - expected_pydantic_fields))}"
    )


def test_testround_pydantic_and_sqlalchemy_schemas_are_in_sync():
    sqlalchemy_columns = {c.name for c in inspect(CogspeedTestRound).columns}
    pydantic_fields = set(CogspeedTestRoundModel.model_fields.keys())

    sqlalchemy_only = {"created_at", "client_id", "test_id"}
    pydantic_only: set[str] = set()

    expected_pydantic_fields = (sqlalchemy_columns - sqlalchemy_only).union(
        pydantic_only
    )

    assert pydantic_fields == expected_pydantic_fields, (
        "Pydantic model TestRound_Model_ is out of sync with SQLAlchemy model TestRound."
    )
