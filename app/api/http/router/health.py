from datetime import UTC, datetime

from fastapi import APIRouter, Request

router = APIRouter(prefix='', tags=['Health'])


async def service_status(_request: Request):
    return {'server_time': datetime.now(UTC).isoformat(), 'status': 'OK'}


@router.get('/', include_in_schema=False)
async def index(_request: Request):
    return await service_status(_request)


@router.get('/health')
async def health(_request: Request):
    return await service_status(_request)
