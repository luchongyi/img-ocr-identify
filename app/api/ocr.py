from fastapi import APIRouter, UploadFile,Request
from app.services.ocr_service import ocr_predict
from fastapi import APIRouter, UploadFile, Request, Depends
from app.core.security import verify_api_key
from app.core.limiter import limiter



router = APIRouter()

@router.post("/ocr/")
@limiter.limit("30/minute")  # 每分钟最多25次
async def ocr_api(
    request: Request, 
    file: UploadFile,
    api_key: str = Depends(verify_api_key)  # 添加API密钥验证
):
    return await ocr_predict(file)


@router.get("/health")
def health():
    return {"status": "ok"}