import time
import socket
from urllib.parse import urlparse
from app.config import settings

def wait_for_db(timeout_seconds: int = 30):
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(db_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    print(f"Waiting for PostgreSQL at {host}:{port}...")
    start = time.time()
    while time.time() - start < timeout_seconds:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"Connected to PostgreSQL at {host}:{port} successfully.")
                return True
        except (socket.error, socket.gaierror, OSError) as e:
            print(f"Database not ready yet ({e}). Retrying in 1s...")
            time.sleep(1)
    print(f"Timed out after {timeout_seconds}s waiting for {host}:{port}")
    return False

if __name__ == "__main__":
    wait_for_db()
