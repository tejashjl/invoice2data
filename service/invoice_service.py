from parser.line_items_extractor import extract_line_items
from parser.main import parse_invoice, parse_invoice_image
import logging as logger


class InvoiceService:
    def __init__(self):
        pass

    def parse_invoice(self, invoice, text_template, image_template):
        extract_line_items(invoice)
        # logger.info("Parsing PDF file by text parser")
        # output = parse_invoice(invoice, text_template)
        # if output == [] or len(output[0]['lines']) == 0:
        #     logger.info("Parsing PDF file by image parser")
        #     output = parse_invoice_image(invoice, image_template)
        # return output
