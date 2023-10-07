from fastapi import APIRouter, HTTPException

from . import crud
from .schemas import TypeSchema

router = APIRouter(prefix='/bot_types',
                   tags=['bot type'])


@router.get('/')
async def get_types():
    return await crud.get_types()


@router.post('/')
async def add_type(_type: TypeSchema):
    if detail := await crud.add_type(_type=_type):
        raise HTTPException(status_code=400, detail=detail)
    return _type
