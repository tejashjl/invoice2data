from parser.main import parse_invoice, parse_invoice_image
from parser.tesseract import Tesseract


class InvoiceService:
    def __init__(self):
        pass

    def parse_invoice(self, invoice, template, file_type):
        tesseract = Tesseract()
        if file_type == 'PDF_WITH_IMAGE':
            return parse_invoice_image(invoice)
        if file_type == 'IMAGE':
            invoice = tesseract.to_pdf(invoice, file_type)

        parsed_data = parse_invoice(invoice, template)
        return parsed_data
