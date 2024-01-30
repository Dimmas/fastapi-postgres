import smtplib
import jwt_guard
from typing import List
from user_service import *
from fastapi import FastAPI
from pydantic import BaseModel
from jwt_service import sign_token
from email.mime.text import MIMEText
from fastapi import HTTPException, status
from fastapi.middleware.cors import CORSMiddleware


from logger import get_logger
logger = get_logger(__name__)


app = FastAPI()


class User(BaseModel):
    id: int
    username: str
    email: str
    config: str
    fio: str

    class Config:
        from_attributes = True


@app.post("/register", response_model=User)
async def register_user(username: str, email: str, password: str, fio: str, birthday: str, tags: list):
    # Добавление пользователя в базу данных
    us = UserService
    try:
        new_user = await us.add_user(username=username, email=email, password=password, fio=fio, birthday=birthday, tags=tags)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    try:
        # Отправка письма на почту
        await send_email_confirmation(email)
    except Exception as e:
        logger.warning(f'send email confirmation error: {str(e)}')
    return new_user


@app.post("/login")
async def authenticate_user(username: str, password: str):
    # Аутентификация пользователя
    user = await create_user(username=username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username")

    user_pwd, salt = user.password.split(':')
    if user_pwd != hashlib.sha256(salt.encode() + password.encode()).hexdigest():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    # Генерация и возврат JWT-токена
    return sign_token({"uid": user.id})


@app.get("/users", response_model=List[User])
async def get_users(jwt_token: str = Depends(jwt_guard.has_access)) -> List[User]:
    # Получение списка всех пользователей
    us = UserService()
    return await us.get_users()


@app.get("/users/search", response_model=List[User])
async def search_users(
        jwt_token: str = Depends(jwt_guard.has_access),
        username: str = None,
        email: str = None,
        fio: str = None,
        birthday: str = None,
        tag: str = None) -> List[User]:
    # Поиск пользователей по указанным полям
    us = UserService()
    return await us.search_users(username=username, email=email, fio=fio, birthday=birthday, tag=tag)


@app.post("/user_delete/{user_id}")
async def delete_user(user_id: int, jwt_token: str = Depends(jwt_guard.has_access)):
    # Удаление пользователя из базы данных
    user = await create_user(uid=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    us = UserService()
    try:
        await us.delete_user(user)
        return {"message": "Пользователь успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Логирование каждого запроса
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


# Добавление CORS-заголовков
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def send_email_confirmation(email: str):
    # Отправка письма на почту
    msg = MIMEText("Подтверждение регистрации")
    msg["Subject"] = "Подтверждение регистрации"
    msg["From"] = "noreply@example.com"
    msg["To"] = email

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.login("username", "password")
        server.sendmail("noreply@example.com", [email], msg.as_string())
