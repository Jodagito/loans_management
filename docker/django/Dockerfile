FROM python:3.11-slim

WORKDIR /app/loans_manager

COPY loans_manager /app/loans_manager
COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install poetry && \
    poetry install --no-root

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python3.11", "-m", "poetry", "run", "gunicorn", "-w", "3", "-t", "60", "--max-requests", "1000", "--max-requests-jitter", "50", "--bind", "0.0.0.0:8000", "loans_manager.wsgi:application"]