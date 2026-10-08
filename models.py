from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

# Bảng 1: Lưu lịch sử trò chuyện Chatbot
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)        # Câu hỏi của người dùng
    bot_response = Column(Text, nullable=False)        # Câu trả lời của AI
    intent = Column(String(100), nullable=True)        # Ý định AI phân tích (VD: LOC_THUA)
    created_at = Column(DateTime, default=datetime.utcnow)

# Bảng 2: Lưu nhật ký ghi chú nông nghiệp
class CropLog(Base):
    __tablename__ = "crop_logs"

    id = Column(Integer, primary_key=True, index=True)
    so_thua = Column(String(50), index=True)           # Mã/số thửa đất
    ten_cay_trong = Column(String(100))                # Tên cây trồng (lúa, ngô...)
    ghi_chu = Column(Text, nullable=True)               # Ghi chú tình trạng
    ngay_tao = Column(DateTime, default=datetime.utcnow)