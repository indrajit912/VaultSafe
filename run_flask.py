# run_flask.py
from vaultsafe.web import create_app
from vaultsafe.config import Config

app = create_app(config_class=Config)

if __name__ == '__main__':
    app.run()
