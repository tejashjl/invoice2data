import os
import string

from flask import Blueprint
from flask import jsonify
from flask import request
from werkzeug.utils import secure_filename

from service.invoice_service import InvoiceService

invoice_parser = Blueprint("invoice_parser", __name__)
service = InvoiceService()
UPLOAD_FOLDER = '/tmp/'
DEFAULT_FILE_TYPE = 'PDF'


@invoice_parser.route('/extract', methods=["POST"])
def extract_data():
    invoice = request.files['file']
    text_template = request.files['text_template']
    image_template = request.files['image_template']
    if invoice:
        filename = secure_filename(invoice.filename)
    invoice.save(os.path.join(UPLOAD_FOLDER, filename))
    file_path = os.path.join(UPLOAD_FOLDER + filename)
    return jsonify(service.parse_invoice(invoice=file_path, text_template=text_template, image_template=image_template))
