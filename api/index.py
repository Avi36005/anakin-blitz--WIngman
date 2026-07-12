# Vercel serverless entrypoint — exposes the FastAPI app as an ASGI function.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app  # noqa: E402  (FastAPI ASGI app)
