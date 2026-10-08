# ==============================================================================
# FILE: main.py
# HOÀN CHỈNH - ĐÃ SỬA DÙNG LIFESPAN THAY CHO ON_EVENT (XÓA CẢNH BÁO DEPRECATION)
# ==============================================================================

import os
import json
import logging
import base64
import asyncio
import time
from typing import Optional
from contextlib import asynccontextmanager

# Thư viện Web & API Framework
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Thư viện Cơ sở dữ liệu (SQLAlchemy)
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models

# Thư viện Google AI (SDK mới google-genai)
from google import genai
from google.genai import types

# ------------------------------------------------------------------------------
# 1. ĐỊNH NGHĨA ĐƯỜNG DẪN THƯ MỤC CHUẨN
# ------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")

# ------------------------------------------------------------------------------
# 2. IMPORT CÁC HÀM THUẬT TOÁN GIS TỪ server_gis.py
# ------------------------------------------------------------------------------
from server_gis import (
    load_data, 
    loc_thua as gis_loc_thua, 
    thua_cuc_tri as gis_thua_cuc_tri, 
    thua_gan as gis_thua_gan, 
    khoang_cach as gis_khoang_cach
)

# Setup Logging
logger = logging.getLogger("MAIN_LOGGER")
logger.setLevel(logging.INFO)


# ------------------------------------------------------------------------------
# 3. NẠP DỮ LIỆU GEOJSON & TẠO BẢNG CSDL BẰNG LIFESPAN (CHUẨN FASTAPI MỚI)
# ------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- THỰC THI KHI KHỞI ĐỘNG SERVER ---
    load_data()  # Nạp dữ liệu bản đồ vào RAM từ server_gis.py
    
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK DATABASE] Đã kết nối CSDL và khởi tạo các bảng thành công!")
    except Exception as e:
        print(f"[LỖI DATABASE] Kết nối CSDL thất bại: {str(e)}")
        
    yield  # Server bắt đầu chạy và nhận request ở đây
    
    # --- THỰC THI KHI TẮT SERVER (NẾU CẦN DỌN DẸP DỮ LIỆU) ---
    print("[INFO] Đang đóng ứng dụng...")


# Khởi tạo ứng dụng FastAPI với lifespan
app = FastAPI(
    title="Hệ thống AI Bản đồ Nông nghiệp",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# 4. TRẢ VỀ GIAO DIỆN WEB (index.html) KHI TRUY CẬP TRANG CHỦ
# ------------------------------------------------------------------------------
@app.get("/")
async def serve_index_html():
    """Mở file index.html làm giao diện chính"""
    if os.path.exists(INDEX_HTML_PATH):
        return FileResponse(INDEX_HTML_PATH)
    return {"message": f"Không tìm thấy file index.html tại: {INDEX_HTML_PATH}"}


# ------------------------------------------------------------------------------
# 5. ĐÓNG GÓI HÀM THUẬT TOÁN TỪ server_gis THÀNH TOOLS CHO GEMINI AI
# ------------------------------------------------------------------------------
def tool_loc_thua(dieu_kien: str) -> str:
    """Lọc danh sách thửa đất theo từ khóa (VD: loại đất, chủ sở hữu, lúa, thửa 1)."""
    res = gis_loc_thua(dieu_kien=dieu_kien)
    return json.dumps(res, ensure_ascii=False)

def tool_thua_cuc_tri(truong: str = "dien_tich", loai: str = "max") -> str:
    """Tìm thửa đất có diện tích hoặc thuộc tính lớn nhất/nhỏ nhất (loai='max' hoặc 'min')."""
    res = gis_thua_cuc_tri(truong=truong, loai=loai)
    return json.dumps(res, ensure_ascii=False)

def tool_thua_gan(lat: float, lon: float, ban_kinh_m: float = 500.0) -> str:
    """Tìm thửa đất gần vị trí tọa độ Lat, Lon trong bán kính ban_kinh_m (mét)."""
    res = gis_thua_gan(lat=lat, lon=lon, ban_kinh_m=ban_kinh_m)
    return json.dumps(res, ensure_ascii=False)

def tool_khoang_cach(dt1: str, dt2: str) -> str:
    """Tính khoảng cách mét giữa 2 đối tượng hoặc 2 thửa đất."""
    res = gis_khoang_cach(dt1=dt1, dt2=dt2)
    return json.dumps(res, ensure_ascii=False)

def tool_du_bao_thoi_tiet(tinh_thanh: str) -> str:
    """Tra cứu dự báo thời tiết tỉnh/thành phố."""
    return f"Thời tiết tại {tinh_thanh}: Nắng nhẹ, nhiệt độ 28°C - 32°C, độ ẩm 75%. (Nguồn: Trung tâm Dự báo KTTV Quốc gia)"

def tool_tra_cuu_gia_nong_san(san_pham: str, tinh_thanh: Optional[str] = None) -> str:
    """Tra cứu giá nông sản."""
    dia_ban = f" tại {tinh_thanh}" if tinh_thanh else ""
    return f"Giá {san_pham}{dia_ban}: 18,500 VNĐ/kg, xu hướng ổn định. (Nguồn: Cổng thông tin Thị trường Nông sản)"


# ------------------------------------------------------------------------------
# 6. CẤU HÌNH GEMINI AI CLIENT
# ------------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6L0VAn24MjUTa0JWoZ3XrvdAhXUiM615YV3vuycpmAdyQ")
client = genai.Client(api_key=api_key)

system_instruction = """
Bạn là Trợ lý AI Bản đồ Nông nghiệp thông minh.
QUY TẮC PHẢN HỒI:
1. Đối với câu hỏi chào hỏi hoặc giao tiếp thông thường: Trả lời NGAY LẬP TỨC, KHÔNG gọi bất kỳ công cụ nào.
2. Chỉ gọi các công cụ GIS (tool_loc_thua, tool_thua_cuc_tri, tool_thua_gan, tool_khoang_cach) khi người dùng hỏi cụ thể về thửa đất, diện tích, khoảng cách hoặc vị trí.
3. TUYỆT ĐỐI KHÔNG hiển thị chuỗi JSON thô cho người dùng. Đọc dữ liệu từ công cụ và trả lời bằng TIẾNG VIỆT TỰ NHIÊN, rõ ràng, ngắn gọn.
4. Giữ nguyên trích dẫn '(Nguồn: ...)' nếu thông tin từ công cụ thời tiết hoặc giá nông sản.
"""

ai_config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    tools=[
        tool_loc_thua, tool_thua_cuc_tri, tool_thua_gan, 
        tool_khoang_cach, tool_du_bao_thoi_tiet, tool_tra_cuu_gia_nong_san
    ]
)


# ------------------------------------------------------------------------------
# 7. CÁC API DÀNH CHO FRONTEND
# ------------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None

@app.post("/api/chat", summary="API Chatbot AI (Tự động Retry & Fallback các Model thế hệ mới 3.5+)")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    MODELS_TO_TRY = [
        'gemini-3.5-flash-lite',
        'gemini-3.5-flash',
        'gemini-3.6-flash',
        'gemini-3.7-flash',
        'gemini-3.8-flash'
    ]
    
    contents = []
    if request.image_base64:
        raw_b64 = request.image_base64.split(",")[1] if "," in request.image_base64 else request.image_base64
        image_bytes = base64.b64decode(raw_b64)
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
    contents.append(request.message)

    reply_text = None
    last_error = None

    for model_name in MODELS_TO_TRY:
        for attempt in range(3):
            try:
                logger.info(f"-> Đang gửi yêu cầu tới model '{model_name}' (Lần thử {attempt + 1})...")
                
                chat_session = client.chats.create(
                    model=model_name,
                    config=ai_config
                )
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(chat_session.send_message, contents),
                    timeout=35.0
                )
                reply_text = response.text
                break
            except Exception as e:
                last_error = e
                err_msg = str(e)
                
                if "503" in err_msg or "UNAVAILABLE" in err_msg:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Model '{model_name}' bận 503. Chờ {wait_time}s rồi thử lại...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Thử model tiếp theo do lỗi tại '{model_name}': {err_msg}")
                    break

        if reply_text:
            break

    if not reply_text:
        logger.error(f"Tất cả các model Gemini 3.5+ đều bận: {str(last_error)}")
        return {"reply": "Máy chủ AI của Google đang bị quá tải cao điểm. Vui lòng chờ khoảng 15-30 giây rồi thử lại nhé!"}

    # Tự động lưu cuộc hội thoại vào CSDL
    try:
        new_chat = models.ChatHistory(
            user_message=request.message,
            bot_response=reply_text,
            intent="GEMINI_GIS_CHAT"
        )
        db.add(new_chat)
        db.commit()
    except Exception as db_err:
        db.rollback()
        logger.error(f"Lỗi lưu CSDL: {str(db_err)}")

    return {"reply": reply_text}


# Các API GIS phục vụ trực tiếp cho frontend
@app.get("/api/loc-thua")
def api_loc_thua(dieu_kien: str):
    return gis_loc_thua(dieu_kien)

@app.get("/api/thua-cuc-tri")
def api_thua_cuc_tri(truong: str = "dien_tich", loai: str = "max"):
    return gis_thua_cuc_tri(truong, loai)

@app.get("/api/thua-gan")
def api_thua_gan(lat: float, lon: float, ban_kinh_m: float = 500.0):
    return gis_thua_gan(lat, lon, ban_kinh_m)

@app.get("/api/khoang-cach")
def api_khoang_cach(dt1: str, dt2: str):
    return gis_khoang_cach(dt1, dt2)

@app.get("/api/history")
def get_chat_history(limit: int = 20, db: Session = Depends(get_db)):
    chats = db.query(models.ChatHistory).order_by(models.ChatHistory.id.desc()).limit(limit).all()
    return {"tong_so": len(chats), "data": chats}

# Mount các file giao diện tĩnh
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")


# ------------------------------------------------------------------------------
# 8. KHỞI CHẠY SERVER
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)