from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from typing import AsyncGenerator
from sqlalchemy import text, select
from config import settings
from src.models.albums_models import AlbumStatuses, AlbumTypes
from src.models.tracks_models import TracksStatuses, Genres

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
            await session.commit()
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
    from src.models.models import Base  # Импортируйте вашу базу моделей
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Осторожно! Удаляет все таблицы
        await conn.run_sync(Base.metadata.create_all)

        album_s = await conn.execute(select(AlbumStatuses))
        album_statuses = album_s.scalars().all()

        album_t = await conn.execute(select(AlbumTypes))
        album_types = album_t.scalars().all()

        track_s = await conn.execute(select(TracksStatuses))
        track_statuses = track_s.scalars().all()
        
        genre_s = await conn.execute(select(Genres))
        genres = genre_s.scalars().all()

        # Если статусов нет, заполняем
        if not album_statuses:
            await conn.execute(
                text("""
                     INSERT INTO album_statuses (id, title)
                     VALUES (1, 'draft'),
                            (2, 'public')
                     """)
            )

        if not album_types:
            await conn.execute(
                text("""
                     INSERT INTO album_types (id, title)
                     VALUES (1, 'single'),
                            (2, 'ep'),
                            (3, 'album'),
                            (4, 'mix')
                     """)
            )

        if not track_statuses:
            await conn.execute(
                text("""
                     INSERT INTO tracks_statuses (id, title)
                     VALUES (1, 'draft'),
                            (2, 'public')
                     """)
            )

        if not genres:
            await conn.execute(
                text("""
                     INSERT INTO genres (id, title)
                     VALUES (1, 'pop'),
                            (2, 'rock'),
                            (3, 'hip hop'),
                            (4, 'electronic'),
                            (5, 'jazz'),
                            (6, 'classical'),
                            (7, 'r&b'),
                            (8, 'country'),
                            (9, 'latin'),
                            (10, 'metal'),
                            (11, 'folk'),
                            (12, 'blues'),
                            (13, 'reggae'),
                            (14, 'punk'),
                            (15, 'soul'),
                            (16, 'funk'),
                            (17, 'indie'),
                            (18, 'alternative'),
                            (19, 'ambient'),
                            (20, 'world'),
                            (21, 'disco'),
                            (22, 'techno'),
                            (23, 'house'),
                            (24, 'dubstep'),
                            (25, 'drum & bass'),
                            (26, 'trap'),
                            (27, 'grunge'),
                            (28, 'emo'),
                            (29, 'synthwave'),
                            (30, 'k-pop'),
                            (31, 'afrobeats'),
                            (32, 'reggaeton'),
                            (33, 'bluegrass'),
                            (34, 'country pop'),
                            (35, 'pop punk'),
                            (36, 'indie rock'),
                            (37, 'alternative rock'),
                            (38, 'death metal'),
                            (39, 'black metal'),
                            (40, 'folk rock'),
                            (41, 'jazz fusion'),
                            (42, 'smooth jazz'),
                            (43, 'neo soul'),
                            (44, 'contemporary r&b'),
                            (45, 'lo-fi hip hop'),
                            (46, 'experimental'),
                            (47, 'garage rock'),
                            (48, 'psychedelic rock'),
                            (49, 'hard rock'),
                            (50, 'progressive rock')
                     """)
            )

            await conn.execute(
                text("""
                     INSERT INTO genre_parents (child_id, parent_id)
                     VALUES (30, 1),  -- k-pop -> pop
                            (34, 1),  -- country pop -> pop
                            (35, 1),  -- pop punk -> pop
                            (27, 2),  -- grunge -> rock
                            (28, 2),  -- emo -> rock
                            (36, 2),  -- indie rock -> rock
                            (37, 2),  -- alternative rock -> rock
                            (40, 2),  -- folk rock -> rock
                            (47, 2),  -- garage rock -> rock
                            (48, 2),  -- psychedelic rock -> rock
                            (49, 2),  -- hard rock -> rock
                            (50, 2),  -- progressive rock -> rock
                            (26, 3),  -- trap -> hip hop
                            (45, 3),  -- lo-fi hip hop -> hip hop
                            (22, 4),  -- techno -> electronic
                            (23, 4),  -- house -> electronic
                            (24, 4),  -- dubstep -> electronic
                            (25, 4),  -- drum & bass -> electronic
                            (29, 4),  -- synthwave -> electronic
                            (46, 4),  -- experimental -> electronic
                            (41, 5),  -- jazz fusion -> jazz
                            (42, 5),  -- smooth jazz -> jazz
                            (43, 7),  -- neo soul -> r&b
                            (44, 7),  -- contemporary r&b -> r&b
                            (33, 8),  -- bluegrass -> country
                            (32, 9),  -- reggaeton -> latin
                            (38, 10), -- death metal -> metal
                            (39, 10), -- black metal -> metal
                            (35, 14), -- pop punk -> punk
                            (28, 14), -- emo -> punk
                            (40, 11), -- folk rock -> folk
                            (36, 17), -- indie rock -> indie
                            (37, 18), -- alternative rock -> alternative
                            (23, 21), -- house -> disco
                            (31, 20) -- afrobeats -> world
                     """)
            )
            print("✅ User statuses have been populated")
        else:
            print(f"✅ User statuses already exist)")
