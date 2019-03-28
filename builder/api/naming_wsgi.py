# usage: gunicorn --workers=3 --bind=0.0.0.0:5000 --pythonpath '../../' naming_wsgi:app
from naming import app

if __name__ == "__main__":
    app.run()