from parser.main import parse_invoice, parse_invoice_image


class InvoiceService:
    def __init__(self):
        pass

    def parse_invoice(self, invoice, template, file_type):
        if file_type == 'PDF_WITH_IMAGE':
            return parse_invoice_image(invoice, template)
        else:
            return parse_invoice(invoice, template)
