from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from typing import AsyncGenerator
from sqlalchemy import text, select
from config import settings
from src.models.users_models import UserStatuses

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция, которую FastAPI будет использовать как зависимость.
    Она создает сессию, отдает её в эндпоинт, а после закрывает.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Добавьте эти функции для совместимости
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Алиас для get_async_session"""
    async for session in get_async_session():
        yield session


async def init_db():
    """Инициализация базы данных (создание таблиц)"""
    from src.models.users_models import Base  # Импортируйте вашу базу моделей
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Осторожно! Удаляет все таблицы
        await conn.run_sync(Base.metadata.create_all)

        result = await conn.execute(select(UserStatuses))
        statuses = result.scalars().all()

        # Если статусов нет, заполняем
        if not statuses:
            await conn.execute(
                text("""
                     INSERT INTO user_statuses (id, title, description)
                     VALUES (1, 'active', 'Активный пользователь'),
                            (2, 'inactive', 'Неактивный пользователь'),
                            (3, 'banned', 'Заблокированный пользователь'),
                            (4, 'deleted', 'Удаленный пользователь')
                     """)
            )
            print("✅ User statuses have been populated")
        else:
            print(f"✅ User statuses already exist ({len(statuses)} records)")
