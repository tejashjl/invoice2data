#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

import pkg_resources

import parser.in_pdftotext as pdftotext
from parser.template import read_templates

logger = logging.getLogger(__name__)

FILENAME = "{date} {desc}.pdf"


def parse_invoice(invoice, output):
    templates = read_templates(pkg_resources.resource_filename('parser', 'templates'))
    res = extract_data(invoice, templates=templates)
    if res:
        logger.info(json.dumps(res))
        output.append(res)


def extract_data(invoicefile, templates=None, debug=False):
    if templates is None:
        templates = read_templates(
            pkg_resources.resource_filename('parser', 'templates'))

    extracted_str = pdftotext.to_text(invoicefile).decode('utf-8')

    charcount = len(extracted_str)
    logger.debug('number of char in pdf2text extract: %d', charcount)
    # Disable Tesseract for now.
    # if charcount < 40:
    # logger.info('Starting OCR')
    # extracted_str = image_to_text.to_text(invoicefile)
    logger.debug('START pdftotext result ===========================')
    logger.debug(extracted_str)
    logger.debug('END pdftotext result =============================')

    logger.debug('Testing {} template files'.format(len(templates)))
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)

        if t.matches_input(optimized_str):
            return t.extract(optimized_str)

    logger.error('No template for %s', invoicefile)
    return False
