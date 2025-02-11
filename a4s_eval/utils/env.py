import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/cache")