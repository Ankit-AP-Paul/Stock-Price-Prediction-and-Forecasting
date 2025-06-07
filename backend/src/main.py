import uuid
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
from dotenv import load_dotenv
from passlib.hash import bcrypt
from sqlalchemy import create_engine, Column, String, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base
from src.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, UserProfileResponse
import yfinance as yf
import pandas as pd

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
JWT_SECRET = os.environ.get("JWT_SECRET")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Backend Microservice", version="1.0.0",
              description="Stokis Backend Microservice")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    createdAt = Column(DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(
        timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def set_password(self, plaintext_password):
        self.password = bcrypt.hash(plaintext_password)

    def check_password(self, plaintext_password):
        return bcrypt.verify(plaintext_password, self.password)


Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(user_id: str, name: str, email: str):
    payload = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={
                            "message": "Token has expired", "status": 401})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail={
                            "message": "Invalid token", "status": 401})


security = HTTPBearer()


@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Backend is running!", "status": 200}


@app.post("/register", response_model=TokenResponse, tags=["Auth"])
def register_user(user_create: UserCreate):
    db = next(get_db())
    existing_user = db.query(User).filter(
        User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail={
                            "message": "Email already registered", "status": 400})

    user = User(name=user_create.name, email=user_create.email)
    user.set_password(user_create.password)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.name, user.email)
    user_response = UserResponse(id=user.id, name=user.name, email=user.email,
                                 createdAt=user.createdAt, updatedAt=user.updatedAt)
    return {"token": token, "user": user_response, "message": "User registered successfully", "status": 200}


@app.post("/login", response_model=TokenResponse, tags=["Auth"])
def login_user(user_login: UserLogin):
    db = next(get_db())
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not user.check_password(user_login.password):
        raise HTTPException(status_code=401, detail={
                            "message": "Invalid email or password", "status": 401})

    token = create_access_token(user.id, user.name, user.email)
    user_response = UserResponse(id=user.id, name=user.name, email=user.email,
                                 createdAt=user.createdAt, updatedAt=user.updatedAt)
    return {"token": token, "user": user_response, "message": "Login successful", "status": 200}


@app.get("/profile", response_model=UserProfileResponse, tags=["User"])
def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = decode_access_token(token)
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={
                            "message": "User not found", "status": 404})
    user_response = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        createdAt=user.createdAt,
        updatedAt=user.updatedAt
    )
    return {"user": user_response, "message": "Profile retrieved successfully", "status": 200}


@app.get("/stock-info", response_model=dict, tags=["Stock"])
def get_stock_info(ticker_symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = decode_access_token(token)
    try:
        engine = create_engine(DATABASE_URL)
        query = text("SELECT * FROM stock_info WHERE ticker = :ticker")
        data = pd.read_sql_query(query, engine, params={
                                 "ticker": ticker_symbol})
        engine.dispose()
        for col in data.select_dtypes(include=['datetime64']).columns:
            data[col] = data[col].dt.strftime('%Y-%m-%d')
        data_dict = data.to_dict(orient="records")
        return {"data": data_dict, "message": "Stock info retrieved successfully", "status": 200}
    except Exception as e:
        return {"message": f"Error retrieving stock info: {str(e)}", "status": 500}


@app.get("/stock-history", response_model=dict, tags=["Stock"])
def get_stock_history(ticker_symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = decode_access_token(token)
    try:
        engine = create_engine(DATABASE_URL)
        query = f"SELECT * FROM \"{ticker_symbol}\""
        data = pd.read_sql_query(text(query), engine)
        engine.dispose()
        for col in data.select_dtypes(include=['datetime64']).columns:
            data[col] = data[col].dt.strftime('%Y-%m-%d')
        data_dict = data.to_dict(orient="records")
        return {"data": data_dict, "message": "Stock data retrieved successfully", "status": 200}
    except Exception as e:
        return {"message": f"Error retrieving stock data: {str(e)}", "status": 500}

@app.get("/top-gainers-and-losers", response_model=dict, tags=["Stock"])
def get_top_gainers_and_losers(n:int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = decode_access_token(token)
    try:
        engine = create_engine(DATABASE_URL)
        query1 = text("SELECT * FROM percentage_change ORDER BY percentage_change DESC LIMIT :n")
        top_gainers = pd.read_sql_query(query1, engine, params={
                                 "n": n})
        query2 = text("SELECT * FROM percentage_change ORDER BY percentage_change ASC LIMIT :n")
        top_losers = pd.read_sql_query(query2, engine, params={
                                 "n": n})
        engine.dispose()
        top_gainers_list = top_gainers.to_dict(orient="records")
        top_losers_list = top_losers.to_dict(orient="records")
        return {
            "top_gainers": top_gainers_list,
            "top_losers": top_losers_list,
            "message": "Top gainers and losers retrieved successfully",
            "status": 200
        }
    except Exception as e:
        return {"message": f"Error retrieving top gainers and losers: {str(e)}", "status": 500}

