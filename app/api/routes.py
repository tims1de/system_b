from fastapi import APIRouter, Response

router = APIRouter(prefix="/api")


@router.get("/health")
async def health_check() -> Response:
    """Health check endpoint"""
    return Response(content="OK", status_code=200)