# syntax=docker/dockerfile:1
FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN useradd --create-home --uid 10001 appuser
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir .
COPY backend/ ./
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
