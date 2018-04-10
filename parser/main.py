#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

import parser.in_pdftotext as pdftotext
from parser.extarct_items import extract_items
from parser.template import get_template

from parser.utils import convert_pdf_to_images, cleanup

logger = logging.getLogger(__name__)

FILENAME = "{date} {desc}.pdf"


def parse_invoice(invoice, template):
    output = []
    res = extract_data(invoice, template)
    if res:
        logger.info(json.dumps(res))
        output.append(res)
    return output


def parse_invoice_image(invoice_path):
    return extract_image_data(invoice_path)


def extract_image_data(invoice_path):
    output = []
    image_file_paths = convert_pdf_to_images(invoice_path)
    logger.debug('Number of PDF pages: %d', len(image_file_paths))
    for index, image_file in enumerate(image_file_paths):
        logger.debug('Parsing page: (%d/%d)', index, len(image_file_paths))
        is_last_page = (len(image_file_paths) == (index + 1))
        output.extend(extract_items(image_file_path=image_file, page_number=index + 1, last_page=is_last_page))
    [cleanup(file_path) for file_path in image_file_paths]
    return output


def extract_data(invoicefile, template, debug=False):
    extracted_str = pdftotext.to_text(invoicefile).decode('utf-8')

    charcount = len(extracted_str)
    logger.debug('number of char in pdf2text extract: %d', charcount)
    logger.debug('START pdftotext result ===========================')
    logger.debug(extracted_str)
    logger.debug('END pdftotext result =============================')

    t = get_template(template)
    optimized_str = t.prepare_input(extracted_str)
    return t.extract(optimized_str)
