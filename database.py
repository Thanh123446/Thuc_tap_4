from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Điền chính xác Server Name từ hình ảnh của bạn (có chữ r ở đầu)
SERVER_NAME = r"DESKTOP-KNP80BR\MSSQLSERVER01"

# 2. Tên Database bạn tạo trong SSMS
DATABASE_NAME = "AgricultureDB"

# Chuỗi kết nối SQL Server dùng Windows Authentication
DATABASE_URL = f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()