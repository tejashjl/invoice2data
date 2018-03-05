import json
import os

from flask import Blueprint
from flask import request
from werkzeug.utils import secure_filename
from flask import jsonify

from service.invoice_service import InvoiceService

invoice_parser = Blueprint("invoice_parser", __name__)
service = InvoiceService()
UPLOAD_FOLDER = '/tmp/'


@invoice_parser.route('/extract', methods=["POST"])
def extract_data():
    invoice = request.files['file']
    template = request.files['template']
    if invoice:
        filename = secure_filename(invoice.filename)
    invoice.save(os.path.join(UPLOAD_FOLDER, filename))
    file_path = os.path.join(UPLOAD_FOLDER + invoice.filename)
    return jsonify(service.parse_invoice(invoice=file_path, template=template))



