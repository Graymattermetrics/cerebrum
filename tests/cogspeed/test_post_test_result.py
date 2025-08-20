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
    print(response.json())
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
        "status": "correct",
        "roundTypeNormalized": "training",
        "answerLocation": 4,
        "locationClicked": 4,
        "queryNumber": "7num",
        "duration": -1,
        "correctRollingMeanRatio": "n/a",
        "roundNumber": 1,
        "roundType": 0,
        "timeTaken": 1222.2000000476837,
        "isCorrectOrIncorrectFromPrevious": None,
        "ratio": 0,
        "_id": "bb8685a0-d571-42a6-93f0-0a9ecc417984",
        "_time_epoch": 8180.100000143051,
    },
    {
        "status": "correct",
        "roundTypeNormalized": "practice",
        "answerLocation": 6,
        "locationClicked": 6,
        "queryNumber": "9dot",
        "duration": -1,
        "correctRollingMeanRatio": "n/a",
        "roundNumber": 2,
        "roundType": 1,
        "timeTaken": 1001.5999999046326,
        "isCorrectOrIncorrectFromPrevious": None,
        "ratio": 0,
        "_id": "246826c7-1b43-460d-908f-3ee2765c6dc4",
        "_time_epoch": 9181.700000047684,
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
