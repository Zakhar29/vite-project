#!/usr/bin/env python3
"""
Заполняет проект демо-данными: пользователи, альбомы, треки, посты.

Запуск (из корня репозитория, при поднятом docker compose):
    pip install -r scripts/requirements.txt
    python scripts/seed.py

Повторный запуск пропускает сид, если в ленте уже есть контент.
Принудительно: python scripts/seed.py --force
"""

from __future__ import annotations

import argparse
import sys
import urllib.parse
from dataclasses import dataclass
from typing import Any

import httpx

GATEWAY_URL = "http://localhost:8080"
CATALOG_URL = "http://localhost:8004"
SOCIAL_URL = "http://localhost:8002"

DEMO_PASSWORD = "demo12345"

# Публичные URL для обложек и аудио (работают без MinIO)
SAMPLE_MP3 = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{}.mp3"
COVER_URL = "https://picsum.photos/seed/{seed}/400/400"


@dataclass
class DemoUser:
    username: str
    nickname: str
    email: str


DEMO_USERS = [
    DemoUser("luna_waves", "Luna Waves", "luna@demo.local"),
    DemoUser("neon_pulse", "Neon Pulse", "neon@demo.local"),
    DemoUser("dj_metro", "DJ Metro", "metro@demo.local"),
]

DEMO_ALBUMS = [
    {
        "user": "luna_waves",
        "title": "Midnight Drive",
        "type": 3,  # album
        "cover_seed": "midnightdrive",
        "tracks": [
            {"title": "Neon Highway", "bpm": 128, "genres": [4, 22], "text": "Electronic night ride."},
            {"title": "Starlight", "bpm": 110, "genres": [1, 4], "text": "Ambient pop glow."},
        ],
    },
    {
        "user": "neon_pulse",
        "title": "City Lights EP",
        "type": 2,  # ep
        "cover_seed": "citylights",
        "tracks": [
            {"title": "Downtown", "bpm": 95, "genres": [3, 45], "text": "Lo-fi hip hop beats."},
            {"title": "After Hours", "bpm": 88, "genres": [3, 43], "text": "Neo soul vibes."},
        ],
    },
    {
        "user": "dj_metro",
        "title": "Summer Hit",
        "type": 1,  # single
        "cover_seed": "summerhit",
        "tracks": [
            {"title": "Sunset Boulevard", "bpm": 124, "genres": [23, 1], "text": "House summer anthem."},
        ],
    },
]

DEMO_POSTS = [
    ("luna_waves", "Только что выкатила «Midnight Drive» — слушайте на главной!"),
    ("neon_pulse", "Новый EP «City Lights» уже в ленте. Какой трек зашёл больше?"),
    ("dj_metro", "Летний сингл «Summer Hit» — для вечеринок и дороги."),
    ("luna_waves", "Кто ещё пишет в жанре synthwave? Давайте обсудим в комментариях."),
]


class SeedError(RuntimeError):
    pass


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def ensure_services(client: httpx.Client) -> None:
    for name, url in [
        ("gateway", f"{GATEWAY_URL}/docs"),
        ("music_catalog", f"{CATALOG_URL}/docs"),
        ("social_feed", f"{SOCIAL_URL}/docs"),
    ]:
        try:
            response = client.get(url, timeout=5)
            if response.status_code >= 500:
                raise SeedError(f"{name} недоступен ({url})")
        except httpx.RequestError as exc:
            raise SeedError(
                f"Сервис {name} не отвечает ({url}). Запустите: docker compose up -d"
            ) from exc


def already_seeded(client: httpx.Client) -> bool:
    response = client.get(
        f"{GATEWAY_URL}/api/v1/music-feed/new-releases",
        params={"limit": 1},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return int(data.get("total", 0)) > 0


def register_or_login(client: httpx.Client, user: DemoUser) -> str:
    login_response = client.post(
        f"{GATEWAY_URL}/api/v1/auth/login",
        json={"email": user.email, "password": DEMO_PASSWORD},
        timeout=15,
    )
    if login_response.status_code == 200:
        return login_response.json()["access_token"]

    register_payload = {
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "password": DEMO_PASSWORD,
    }
    register_response = client.post(
        f"{GATEWAY_URL}/api/v1/auth/register",
        json=register_payload,
        timeout=15,
    )

    if register_response.status_code == 201:
        return register_response.json()["access_token"]

    raise SeedError(
        f"Не удалось создать/войти как {user.username}: "
        f"register={register_response.status_code} login={login_response.status_code}"
    )


def create_album(
    client: httpx.Client,
    token: str,
    album_cfg: dict[str, Any],
    mp3_offset: int,
) -> None:
    headers = auth_headers(token)

    album_response = client.post(
        f"{CATALOG_URL}/album_create/albums",
        headers=headers,
        json={
            "title": album_cfg["title"],
            "type": album_cfg["type"],
            "cover_url": "",
        },
        timeout=15,
    )
    album_response.raise_for_status()
    album_id = album_response.json()["id"]

    cover_url = COVER_URL.format(seed=album_cfg["cover_seed"])
    patch_response = client.patch(
        f"{CATALOG_URL}/album_create/albums/{album_id}",
        headers=headers,
        json={"cover_url": cover_url},
        timeout=15,
    )
    patch_response.raise_for_status()

    for index, track_cfg in enumerate(album_cfg["tracks"], start=1):
        track_response = client.post(
            f"{CATALOG_URL}/album_create/albums/{album_id}/tracks",
            headers=headers,
            json={
                "title": track_cfg["title"],
                "text": track_cfg["text"],
                "bpm": track_cfg["bpm"],
                "author_attention": False,
            },
            timeout=15,
        )
        track_response.raise_for_status()
        track_id = track_response.json()["track_id"]

        audio_url = urllib.parse.quote(SAMPLE_MP3.format(mp3_offset + index), safe="")
        audio_response = client.patch(
            f"{CATALOG_URL}/album_create/tracks/{track_id}/audio?s3_url={audio_url}",
            headers=headers,
            timeout=15,
        )
        audio_response.raise_for_status()

        genres_response = client.post(
            f"{CATALOG_URL}/album_create/tracks/{track_id}/genres",
            headers=headers,
            json={"genre_ids": track_cfg["genres"]},
            timeout=15,
        )
        genres_response.raise_for_status()

    publish_response = client.post(
        f"{CATALOG_URL}/album_create/albums/{album_id}/publish",
        headers=headers,
        timeout=15,
    )
    publish_response.raise_for_status()
    print(f"  + Альбом «{album_cfg['title']}» опубликован ({album_id})")


def create_post(client: httpx.Client, token: str, text: str) -> None:
    response = client.post(
        f"{SOCIAL_URL}/posts",
        headers=auth_headers(token),
        json={"text": text, "media": []},
        timeout=15,
    )
    response.raise_for_status()
    post_id = response.json().get("id", "?")
    print(f"  + Пост создан ({post_id}): {text[:50]}...")


def run(force: bool) -> int:
    tokens: dict[str, str] = {}

    with httpx.Client() as client:
        print("Проверка сервисов…")
        ensure_services(client)

        if not force and already_seeded(client):
            print("Демо-данные уже есть (new-releases не пуст). Используйте --force для повторного сида.")
            return 0

        print("Создание демо-пользователей…")
        for user in DEMO_USERS:
            tokens[user.username] = register_or_login(client, user)
            print(f"  + {user.nickname} (@{user.username})")

        print("Создание альбомов и треков…")
        mp3_offset = 1
        for album_cfg in DEMO_ALBUMS:
            token = tokens[album_cfg["user"]]
            create_album(client, token, album_cfg, mp3_offset)
            mp3_offset += len(album_cfg["tracks"]) + 1

        print("Создание постов…")
        for username, text in DEMO_POSTS:
            create_post(client, tokens[username], text)

    print()
    print("Готово! Откройте http://localhost:5173")
    print("Демо-аккаунты (пароль для всех: demo12345):")
    for user in DEMO_USERS:
        print(f"  • {user.email}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Заполнить Melo демо-данными")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Создать данные даже если лента уже не пустая",
    )
    args = parser.parse_args()

    try:
        return run(force=args.force)
    except SeedError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    except httpx.HTTPStatusError as exc:
        print(f"HTTP {exc.response.status_code}: {exc.response.text}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
