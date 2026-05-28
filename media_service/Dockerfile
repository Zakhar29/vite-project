FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir \
    aiobotocore==3.4.0 \
    boto3==1.42.84 \
    fastapi==0.135.3 \
    uvicorn==0.44.0 \
    pillow==11.3.0 \
    moviepy==2.2.1 \
    python-multipart==0.0.28 \
    audioop-lts==0.2.2 \
    pydub==0.25.1 \
    pydantic==2.12.5 \
    pydantic-settings==2.14.0 \
    python-dotenv==1.2.2 \
    numpy==2.4.4 \
    ImageIO==2.37.3 \
    imageio-ffmpeg==0.6.0

COPY . .

RUN ls -la /app && cat /app/main.py | head -20 || echo "main.py not found"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "debug"]