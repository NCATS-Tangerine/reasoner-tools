# usage: gunicorn --workers=3 --timeout=120 --bind=0.0.0.0:5000 --pythonpath '../../' onto_wsgi:app
from onto_gunicorn import app

if __name__ == "__main__":
    app.run()