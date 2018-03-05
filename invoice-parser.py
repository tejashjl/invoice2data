import logging
from flask import Flask

from controller.invoice_controller import invoice_parser

app = Flask(__name__)
logger = app.logger

stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.DEBUG)
app.logger.info('first startup')
app.register_blueprint(invoice_parser)

if __name__ == '__main__':
    app.run()
