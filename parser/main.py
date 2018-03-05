#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

import parser.in_pdftotext as pdftotext
from parser.template import get_template

logger = logging.getLogger(__name__)

FILENAME = "{date} {desc}.pdf"


def parse_invoice(invoice, template):
    output = []
    res = extract_data(invoice, template)
    if res:
        logger.info(json.dumps(res))
        output.append(res)
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
