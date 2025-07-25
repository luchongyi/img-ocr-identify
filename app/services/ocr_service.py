
from paddle.base.core import GpuPassStrategy
from paddleocr import PaddleOCR
from fastapi import UploadFile
import io
from PIL import Image
import numpy as np
import time
from fastapi import HTTPException
from fastapi import UploadFile
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # 保证结果稳定


ocr = PaddleOCR(
    use_doc_orientation_classify=False, #功能作用‌：自动识别文档图像的旋转角度，提升后续文字识别的准确性。
    use_doc_unwarping=False, #功能作用‌：自动矫正文档图像的几何扭曲（如倾斜、扭曲等），提升后续文字识别的准确性。
    #(关闭后能快10倍)，如果准确度不行的话建议关闭提升准确性
    use_textline_orientation=False, #功能作用‌：自动识别文本行的方向，提升后续文字识别的准确性。
    lang='ch',
    #text_detection_model_name='ch_PP-OCRv3_det',不支持V3版本
    #text_recognition_model_name='ch_PP-OCRv3_rec',不支持V3版本
    det_model_dir='app/ocr_models/PP-OCRv4_mobile_det_infer',
    rec_model_dir='app/ocr_models/PP-OCRv4_mobile_rec_infer',
    ocr_version='PP-OCRv4',
)


def preprocess_image(image_bytes, max_width=640):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))
    return np.array(img)

def extract_rec_texts(result):
    rec_texts_list = []
    for res in result:
        if hasattr(res, 'rec_texts'):
            rec_texts_list.extend(res.rec_texts)
        elif isinstance(res, dict) and 'rec_texts' in res:
            rec_texts_list.extend(res['rec_texts'])
    return rec_texts_list

async def ocr_predict(file: UploadFile):
    import paddle
    # 文件类型校验
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='仅支持图片文件上传')
    # 文件大小校验（限制5MB以提高速度）
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 恢复到文件开头
    max_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_size:
        raise HTTPException(status_code=400, detail='图片文件过大，最大支持5MB')
    
    start = time.time()
    try:
        print("当前设备：", paddle.device.get_device())
        print("是否支持CUDA：", paddle.device.is_compiled_with_cuda())
        image_bytes = await file.read()
        img_np = preprocess_image(image_bytes)
        result = ocr.predict(img_np)
        rec_texts_list = extract_rec_texts(result)
        # 语言检测
        if rec_texts_list:
            full_text = " ".join(rec_texts_list)
            try:
                lang = detect(full_text)
            except Exception:
                lang = None
        else:
            lang = None
        processing_time = time.time() - start
        print(f"OCR识别耗时：{processing_time:.2f}秒")
        return {
            "rec_texts": rec_texts_list,
            "language": lang,
            "processing_time": f"{processing_time:.2f}秒",
            "text_count": len(rec_texts_list)
        }
    except Exception as e:
        print("OCR识别异常：", e)
        return {"error": str(e)}


async def detect_image_language(file: UploadFile):
    """
    检测图片中文字的语言类型。
    先通过OCR识别图片中的文本，再用langdetect库判断文本的主要语言。

    参数：
        file (UploadFile): 上传的图片文件
    返回：
        dict: 包含语言类型（language）、合并后的文本（text），如识别失败则返回错误信息
    """
    ocr_result = await ocr_predict(file)
    texts = ocr_result.get("rec_texts", [])
    if not texts:
        return {"language": None, "confidence": 0, "text": ""}
    full_text = " ".join(texts)
    try:
        lang = detect(full_text)
        return {"language": lang, "text": full_text}
    except Exception as e:

        
        
        
        return {"language": None, "error": str(e)}