from fastapi import HTTPException
from bson import ObjectId
from bson.errors import InvalidId


def get_object_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 ID 형식입니다.",
        )


def get_str_id(id: ObjectId) -> str:
    return str(id)
