# run_flask.py
# Author: Indrajit Ghosh
# Created On: Jun 17, 2024
#
import sys

from vaultsafe.web import create_app
from vaultsafe.config import Config

app = create_app(config_class=Config)

if __name__ == '__main__':
    port = sys.argv[1]
    app.run(port=port)
