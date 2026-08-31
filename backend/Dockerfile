FROM python:3.11-slim

WORKDIR /app

# Install system dependencies & curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code, migrations, and data fixtures
COPY alembic.ini /app/
COPY backend/alembic /app/backend/alembic
COPY backend/app /app/app
COPY backend/app /app/backend/app
COPY data /app/data

ENV PYTHONPATH=/app:/app/backend
EXPOSE 8000

# Wait for database, run migrations, seed database, and launch uvicorn server
CMD ["sh", "-c", "python app/wait_for_db.py && alembic upgrade head && python app/seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
