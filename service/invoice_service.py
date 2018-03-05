from parser.main import parse_invoice


class InvoiceService:
    def __init__(self):
        pass

    def parse_invoice(self, invoice, template):
        parsed_data = parse_invoice(invoice, template)
        return parsed_data
