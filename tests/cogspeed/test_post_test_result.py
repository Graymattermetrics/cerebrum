import datetime
from typing import TYPE_CHECKING, Any
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CogspeedTestResult, CogspeedTestRound

if TYPE_CHECKING:
    from ..conftest import CreatedClientType

pytestmark = pytest.mark.asyncio


async def test_post_cogspeed_test_result(
    client: AsyncClient, session: AsyncSession, created_client: "CreatedClientType"
) -> None:
    client_id = created_client["client_id"]
    api_key = created_client["api_key"]

    headers = {"X-Client-ID": client_id, "X-Api-Key": api_key}

    payload = example_test_response.copy()
    payload["client_id"] = client_id

    response = await client.post(
        "clients/cogspeed/tests", json=payload, headers=headers
    )
    assert response.status_code == 201

    query = select(CogspeedTestResult).where(CogspeedTestResult.id == payload["id"])
    result = await session.execute(query)
    db_test_result = result.scalar_one_or_none()

    assert db_test_result is not None
    assert db_test_result.client_id == client_id
    assert db_test_result.message == "Test completed successfully"
    assert db_test_result.number_of_rounds == 26

    # Optionally, check that the rounds were also created
    query_rounds = select(CogspeedTestRound).where(
        CogspeedTestRound.test_id == payload["id"]
    )
    result_rounds = await session.execute(query_rounds)
    db_rounds = result_rounds.scalars().all()

    assert len(db_rounds) == len(example_test_rounds)


## Test data
example_test_rounds: list[Any] = [  # Don't add all 26 here for readability
    {
        "Num": 1,
        "Type": "user_paced",
        "Duration": 2826.0,
        "Response": -1.0,
        "Status": "no_response",
        "Ratio": -1.0,
        "Rm": 1.0,
        "Query": "left",
        "Location": "left",
        "Clicked": False,
        "Previous": "right",
    },
    {
        "Num": 2,
        "Type": "user_paced",
        "Duration": 1582.0,
        "Response": -1.0,
        "Status": "no_response",
        "Ratio": -1.0,
        "Rm": 1.0,
        "Query": "right",
        "Location": "right",
        "Clicked": False,
        "Previous": "left",
    },
]
example_test_response: dict[str, Any] = {
    "statusCode": 0,
    "status": "success",
    "success": True,
    "message": "Test completed successfully",
    "testDuration": 22720,
    "numberOfRounds": 26,
    "blockingRoundDuration": 1065,
    "cognitiveProcessingIndex": 74,
    "machinePacedBaseline": 1461.5399999976157,
    "version": "4a2b6dacbd7b39afdf328034b3b58380cd2136a2",
    "fatigueLevel": -1,
    "numberOfRollMeanLimitExceedences": 0,
    "finalRatio": 0.7524882629163948,
    "blockCount": 2,
    "lowestBlockTime": 964.5088542376734,
    "highestBlockTime": 1164.5088542376734,
    "blockRange": 200,
    "finalBlockDiff": 200,
    "totalMachinePacedAnswers": 16,
    "totalMachinePacedCorrectAnswers": 12,
    "totalMachinePacedIncorrectAnswers": 0,
    "totalMachinePacedNoResponseAnswers": 4,
    "quickestResponse": 677.5999999940395,
    "quickestCorrectResponse": 677.5999999940395,
    "slowestResponse": 1166.5999999940395,
    "slowestCorrectResponse": 1027.4000000059605,
    "meanMachinePacedAnswerTime": 872.1500000003725,
    "meanCorrectMachinePacedAnswerTime": 807.3083333348235,
    "_date": "29/06/2025, 21:14:21",
    "_date_minute_offset": -60,
    "id": "0ef66f68-9c2d-45c5-aabc-1689f4cb41de",
    "normalizedLocation": "Could not get location",
    "rounds": example_test_rounds,
    "localDate": datetime.datetime.now(datetime.UTC).isoformat(),
    "localTime": datetime.datetime.now(datetime.UTC).isoformat(),
}
