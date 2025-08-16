from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CogspeedTestResultModel
from app.schemas import CogspeedTestResult, CogspeedTestRound
from app.security import get_client_id_from_api_key


router = APIRouter()


@router.post("/clients/cogspeed/tests", status_code=status.HTTP_201_CREATED)
async def post_cogspeed_test(
    test: CogspeedTestResultModel,
    db: AsyncSession = Depends(get_db),
    client_id: str = Depends(get_client_id_from_api_key),
) -> int:
    if client_id != test.client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The client ID in the header ('{client_id}') does not match the client ID in the body ('{test.client_id}').",
        )

    metadata = {"client_id": test.client_id, "test_id": test.id}
    rounds = [metadata | r.model_dump() for r in test.rounds]

    db_cogspeed_test_result = CogspeedTestResult(
        rounds=[CogspeedTestRound(**r) for r in rounds],
        **test.model_dump(exclude={"rounds"}),
    )
    db.add(db_cogspeed_test_result)
    await db.commit()
    await db.refresh(db_cogspeed_test_result)

    return status.HTTP_201_CREATED
