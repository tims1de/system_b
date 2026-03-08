from fastapi import APIRouter, Response, HTTPException, Depends
from app.schemas.signed_api_data import SignedApiData
from app.services.message_service import MessageService
from app.storage.unit_of_work import UnitOfWork

router = APIRouter(prefix="/api")


@router.get("/health")
async def health_check() -> Response:
    """Health check endpoint"""
    return Response(content="OK", status_code=200)

@router.post("/messages/incoming", response_model=SignedApiData)
async def incoming_messages(
    signed_data: SignedApiData,
    uow: UnitOfWork = Depends(UnitOfWork)
):
    """Приём входящих транзакций и сохранение в реестр."""
    try:
        return await MessageService.process_incoming(signed_data, uow)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/messages/outgoing", response_model=SignedApiData)
async def outgoing_messages(
    signed_data: SignedApiData,
    uow: UnitOfWork = Depends(UnitOfWork)
):
    """Выдача исходящих транзакций по запросу (SearchRequest)."""
    try:
        return await MessageService.process_outgoing(signed_data, uow)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")