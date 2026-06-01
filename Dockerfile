FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    WEBAPP_ENV=production

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY webapp ./webapp

RUN mkdir -p /app/data

EXPOSE 8000

RUN useradd --no-create-home --uid 10001 webapp \
    && chown -R webapp:webapp /app
USER webapp

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "10", "--access-logfile", "-", "webapp:create_app()"]
