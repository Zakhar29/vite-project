# Деплой Melo на VPS (Docker Compose + Caddy)

Стек: PostgreSQL, Redis, MongoDB, MinIO, 6 микросервисов, React-фронтенд, Caddy (HTTPS + reverse proxy).

Локальная разработка по-прежнему через `docker compose up` (файл `docker-compose.yaml`).

## Требования

- VPS с **4–8 GB RAM**, Ubuntu 22.04/24.04 (или аналог)
- Домен, A-запись которого указывает на IP сервера
- Открытые порты **80** и **443**
- Docker Engine + Docker Compose v2

## 1. Подготовка сервера

```bash
# Обновление и Docker (Ubuntu)
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Перелогиньтесь, чтобы группа docker применилась
```

## 2. Клонирование и настройка

```bash
git clone <ваш-репозиторий> melo
cd melo

cp .env.example .env
nano .env   # обязательно смените пароли и SECRET_KEY
```

| Переменная | Описание |
|------------|----------|
| `DOMAIN` | Домен без `https://`, например `melo.example.com` |
| `ACME_EMAIL` | Email для сертификата Let's Encrypt |
| `SECRET_KEY` | Одна строка для JWT во всех сервисах (`openssl rand -hex 32`) |
| `POSTGRES_*`, `MONGO_*`, `MINIO_*` | Пароли БД и хранилища |

## 3. Запуск

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

Проверка статуса:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f caddy gateway_service
```

После того как DNS распространится, сайт будет доступен по `https://<DOMAIN>`.

### Маршрутизация Caddy

| Путь | Куда |
|------|------|
| `/` | React (nginx) |
| `/api/*` | gateway_service:8080 |
| `/media-music/*`, `/avatars/*`, … | MinIO (медиафайлы) |

## 4. Демо-данные (опционально)

С вашего компьютера (после того как домен отвечает):

```bash
pip install httpx
GATEWAY_URL=https://melo.example.com python scripts/seed.py
```

Или с VPS внутри docker-сети:

```bash
docker run --rm --network melo_melo_network \
  -v "$(pwd)/scripts:/scripts" -w /scripts \
  python:3.13-slim sh -c "pip install -q httpx && GATEWAY_URL=http://gateway_service:8080 python seed.py"
```

Демо-пользователи: `luna_waves`, `neon_pulse`, `dj_metro` — пароль `demo12345`.

## 5. Обновление

```bash
git pull
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

## 6. Полезные команды

```bash
# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs -f gateway_service

# Остановка
docker compose -f docker-compose.prod.yml down

# Остановка с удалением томов (ВСЕ ДАННЫЕ БУДУТ УДАЛЕНЫ)
docker compose -f docker-compose.prod.yml down -v
```

## Безопасность

- Не коммитьте файл `.env` в git
- Используйте длинные случайные пароли
- Базы данных и Redis **не** проброшены наружу — только Caddy на 80/443
- MinIO Console (`:9001`) в prod не открыт; при необходимости админки — SSH-туннель

## Устранение неполадок

**Caddy не получает сертификат** — проверьте A-запись домена и что порты 80/443 не заняты.

**502 на /api** — дождитесь старта всех сервисов: `docker compose -f docker-compose.prod.yml logs gateway_service`.

**Медиа не грузятся** — убедитесь, что `CDN_DOMAIN` в media_service совпадает с `DOMAIN` в `.env` (задаётся автоматически в compose).

**Пересборка только фронта** (сменился API URL):

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build frontend
```
