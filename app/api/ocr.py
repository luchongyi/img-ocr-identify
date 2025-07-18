from fastapi import APIRouter, UploadFile,Request
from app.services.ocr_service import ocr_predict, detect_image_language
from fastapi import APIRouter, UploadFile, Request, Depends
#from app.core.security import verify_api_key
from app.core.limiter import limiter
from fastapi import Depends
from app.core.security import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db


router = APIRouter()

@router.post("/ocr/")
@limiter.limit("30/minute")  # 每分钟最多25次
async def ocr_api(
    request: Request, 
    file: UploadFile,
    current_user: dict = Depends(get_current_user)  # 新增
):
    return await ocr_predict(file)

@router.get("/health")
def health():
    return {"status": "ok"}
    