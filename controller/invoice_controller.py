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
FILE_TYPES = ['PDF', 'PDF_WITH_IMAGE', 'IMAGE']


@invoice_parser.route('/extract', methods=["POST"])
def extract_data():
    invoice = request.files['file']
    template = request.files['template']
    file_type = request.form.get('file_type', DEFAULT_FILE_TYPE)
    if file_type not in FILE_TYPES:
        return jsonify({"message": "Invalid file type"})
    if invoice:
        filename = secure_filename(invoice.filename)
    invoice.save(os.path.join(UPLOAD_FOLDER, filename))
    file_path = os.path.join(UPLOAD_FOLDER + filename)
    return jsonify(service.parse_invoice(invoice=file_path, template=template, file_type=file_type))
