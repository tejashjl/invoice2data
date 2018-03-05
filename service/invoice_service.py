from parser.main import parse_invoice


class InvoiceService:
    def __init__(self):
        pass

    def parse_invoice(self, invoice):
        output = []
        parse_invoice(invoice, output)
        return output
