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
COPY alembic /app/alembic
COPY backend/app /app/app
COPY data /app/data

ENV PYTHONPATH=/app
EXPOSE 8000

# Run migrations, seed database, and launch uvicorn server
CMD ["sh", "-c", "alembic upgrade head && python app/seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
