# usage: gunicorn --workers=# --bind:0.0.0.0:5000 uberonto_wsgi:app
from uberonto import app

if __name__ == "__main__":
    app.run()