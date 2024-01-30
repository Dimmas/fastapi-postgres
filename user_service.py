import hashlib
import uuid
from models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from connect_db import get_session


async def create_user(
        session: AsyncSession = Depends(get_session),
        uid: int = None,
        username: str = None
) -> User:
    query = select(User)
    if uid:
        query = query.filter(User.id == uid)
    if username:
        query = query.filter(User.username == username)
    result = await session.execute(query)
    return result.scalars().first()


class UserService:

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def add_user(self, username: str, email: str, password: str, fio: str, birthday: str, tags: list):
        # Добавление пользователя в базу данных
        salt = uuid.uuid4().hex
        pwd = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
        new_user = User(username=username, email=email, password=pwd,
                        congig={'fio': fio, 'birthday': birthday, 'tags': tags})
        self.session.add(new_user)
        try:
            await self.session.commit()
            return new_user
        except Exception:
            await self.session.rollback()

    async def get_users(self):
        # Получение списка всех пользователей
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def search_users(
            self, username: str = None,
            email: str = None,
            fio: str = None,
            birthday: str = None,
            tag: str = None
    ):
        # Поиск пользователей по указанным полям
        query = select(User)
        if username:
            query = query.filter(User.username == username)
        if email:
            query = query.filter(User.email == email)

        if fio:
            query = query.filter(User.config["fio"].astext == fio)

        if birthday:
            query = query.filter(User.config["birthday"].astext == birthday)

        if tag:
            query = query.filter(User.config["tags"].contains(tag))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_user(self, user: User):
        await self.session.delete(user)
        await self.session.commit()
