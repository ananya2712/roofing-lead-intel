# gunicorn entry point (wsgi:app).
from app import create_app

app = create_app()
