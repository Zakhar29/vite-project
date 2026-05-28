
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir \
    fastapi==0.135.3 \
    uvicorn==0.44.0 \
    SQLAlchemy==2.0.49 \
    pydantic==2.12.5 \
    pydantic-settings==2.13.1 \
    python-jose==3.5.0 \
    passlib==1.7.4 \
    redis==7.4.0 \
    uuid6==2025.0.1 \
    python-dotenv==1.2.2 \
    "asyncpg>=0.29.0" \
    "psycopg2-binary>=2.9.0" \
    "bcrypt>=4.0.0" \
    "email-validator>=2.0.0"

COPY . .

RUN ls -la /app && cat /app/main.py | head -20 || echo "main.py not found"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]