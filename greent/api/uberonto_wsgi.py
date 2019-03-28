# usage: gunicorn --workers=3 --bind=0.0.0.0:5000 uberonto_wsgi:app
from uberonto import app

if __name__ == "__main__":
    app.run()